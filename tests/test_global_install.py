from __future__ import annotations

from pathlib import Path

import pytest

from ai_code_stack import global_install as global_install_module
from ai_code_stack.filesystem import GENERATED_MARKER
from ai_code_stack.global_install import global_install


def _use_fake_home(monkeypatch, fake_home: Path) -> None:
    monkeypatch.setattr(global_install_module.Path, "home", classmethod(lambda cls: fake_home))


def _snapshot(home: Path) -> set[str]:
    return {str(p) for p in home.rglob("*") if p.is_file()}


@pytest.fixture
def fake_home_all_platforms(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    (home / ".claude" / "agents").mkdir(parents=True)
    (home / ".cursor" / "rules").mkdir(parents=True)
    return home


def test_dry_run_writes_nothing(repo_root: Path, fake_home_all_platforms: Path, monkeypatch):
    _use_fake_home(monkeypatch, fake_home_all_platforms)
    before = _snapshot(fake_home_all_platforms)
    result = global_install(repo_root, dry_run=True)
    after = _snapshot(fake_home_all_platforms)
    assert after == before
    assert result.status == "success"
    assert any(str(fake_home_all_platforms / ".codex" / "AGENTS.md") == a for a in result.artifacts)


def test_apply_writes_expected_files(repo_root: Path, fake_home_all_platforms: Path, monkeypatch):
    _use_fake_home(monkeypatch, fake_home_all_platforms)
    result = global_install(repo_root, dry_run=False)
    assert result.status == "success"
    assert (fake_home_all_platforms / ".codex" / "AGENTS.md").is_file()
    assert (fake_home_all_platforms / ".cursor" / "rules" / "ai-code-stack.mdc").is_file()
    written_agents = list((fake_home_all_platforms / ".claude" / "agents").glob("*.md"))
    assert written_agents, "expected at least one claude-code agent file to be written"


def test_apply_never_overwrites_hand_written_file(repo_root: Path, fake_home_all_platforms: Path, monkeypatch):
    _use_fake_home(monkeypatch, fake_home_all_platforms)
    hand_written = fake_home_all_platforms / ".codex" / "AGENTS.md"
    hand_written.write_text("my own hand-written policy, do not touch", encoding="utf-8")

    result = global_install(repo_root, dry_run=False)

    assert hand_written.read_text(encoding="utf-8") == "my own hand-written policy, do not touch"
    assert str(hand_written) in result.details["skipped"]


def test_apply_is_idempotent_on_its_own_output(repo_root: Path, fake_home_all_platforms: Path, monkeypatch):
    _use_fake_home(monkeypatch, fake_home_all_platforms)
    first = global_install(repo_root, dry_run=False)
    second = global_install(repo_root, dry_run=False)
    assert first.details["skipped"] == []
    assert second.details["skipped"] == []


def test_codex_agents_md_carries_generated_marker(repo_root: Path, fake_home_all_platforms: Path, monkeypatch):
    _use_fake_home(monkeypatch, fake_home_all_platforms)
    global_install(repo_root, dry_run=False)
    content = (fake_home_all_platforms / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
    assert GENERATED_MARKER in content
    assert "Global AI Code Stack Policy" in content


def test_platform_absent_is_skipped_with_path_reason(repo_root: Path, tmp_path: Path, monkeypatch):
    empty_home = tmp_path / "empty-home"
    empty_home.mkdir()
    _use_fake_home(monkeypatch, empty_home)
    result = global_install(repo_root, dry_run=True)
    for platform_id in ("codex", "claude-code", "cursor"):
        assert result.details["platforms"][platform_id]["status"] == "skipped"
        assert "not found" in result.details["platforms"][platform_id]["reason"]


def test_antigravity_always_skipped_no_verified_location(repo_root: Path, fake_home_all_platforms: Path, monkeypatch):
    _use_fake_home(monkeypatch, fake_home_all_platforms)
    result = global_install(repo_root, dry_run=True)
    assert result.details["platforms"]["antigravity"]["status"] == "skipped"
    assert "no verified" in result.details["platforms"]["antigravity"]["reason"]


def test_codex_mcp_config_merges_without_clobbering_existing_content(repo_root: Path, fake_home_all_platforms: Path, monkeypatch):
    _use_fake_home(monkeypatch, fake_home_all_platforms)
    monkeypatch.setattr(global_install_module.shutil, "which", lambda name: "/usr/local/bin/graphify-mcp" if name == "graphify-mcp" else None)
    config_path = fake_home_all_platforms / ".codex" / "config.toml"
    config_path.write_text("approval_policy = \"on-request\"\n", encoding="utf-8")

    global_install(repo_root, dry_run=False)

    text = config_path.read_text(encoding="utf-8")
    assert 'approval_policy = "on-request"' in text
    assert "[mcp_servers.graphify]" in text
    assert "graphify-mcp" in text


def test_codex_mcp_config_skipped_when_binary_missing(repo_root: Path, fake_home_all_platforms: Path, monkeypatch):
    _use_fake_home(monkeypatch, fake_home_all_platforms)
    monkeypatch.setattr(global_install_module.shutil, "which", lambda name: None)
    result = global_install(repo_root, dry_run=True)
    assert result.details["platforms"]["codex"]["mcp"]["status"] == "skipped"
    assert "PATH" in result.details["platforms"]["codex"]["mcp"]["reason"]
