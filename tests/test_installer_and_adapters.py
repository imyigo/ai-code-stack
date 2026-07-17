from __future__ import annotations

from pathlib import Path

from ai_code_stack import platforms as platforms_module
from ai_code_stack.adapters import adapter_outputs
from ai_code_stack.installer import install, install_plan
from ai_code_stack.inventory import build_capabilities, load_roles
from ai_code_stack.platforms import detect_platforms


def _snapshot(root: Path) -> set[str]:
    return {str(p) for p in root.rglob("*") if p.is_file()}


def test_install_dry_run_changes_no_files(repo_root: Path):
    before = _snapshot(repo_root)
    result = install(repo_root, dry_run=True)
    after = _snapshot(repo_root)
    assert after == before
    assert result.status == "success"
    assert "no files, links, configs, submodules, commits, or remotes changed" in result.summary


def test_install_dry_run_reports_full_plan(repo_root: Path):
    result = install(repo_root, dry_run=True)
    assert result.details["actions"] == install_plan(repo_root)


def test_install_dry_run_does_not_create_backup_dir(repo_root: Path):
    backups = repo_root / "backups"
    before = {p.name for p in backups.iterdir()} if backups.exists() else set()
    install(repo_root, dry_run=True)
    after = {p.name for p in backups.iterdir()} if backups.exists() else set()
    assert after == before


def test_antigravity_native_subagents_never_fabricated_true():
    detected = detect_platforms()
    assert detected["platforms"]["antigravity"]["native_subagents"] in (None, False)


def test_cursor_native_subagents_never_fabricated_true():
    detected = detect_platforms()
    assert detected["platforms"]["cursor"]["native_subagents"] in (None, False)


def test_antigravity_native_subagents_stays_unverified_even_if_binary_detected(monkeypatch):
    def fake_command_version(command: str, *args: str):
        if command == "agy":
            return "/usr/local/bin/agy", "agy 9.9.9"
        return None, None

    monkeypatch.setattr(platforms_module, "command_version", fake_command_version)
    detected = detect_platforms()
    assert detected["platforms"]["antigravity"]["installed"] is True
    assert detected["platforms"]["antigravity"]["native_subagents"] in (None, False)


def test_cursor_native_subagents_stays_unverified_even_if_binary_detected(monkeypatch):
    def fake_command_version(command: str, *args: str):
        if command == "cursor":
            return "/usr/local/bin/cursor", "cursor 9.9.9"
        return None, None

    monkeypatch.setattr(platforms_module, "command_version", fake_command_version)
    detected = detect_platforms()
    assert detected["platforms"]["cursor"]["installed"] is True
    assert detected["platforms"]["cursor"]["native_subagents"] in (None, False)


def test_adapter_outputs_use_role_profile_mode_for_unverified_platforms(repo_root: Path):
    roles = load_roles(repo_root)["roles"]
    capabilities = build_capabilities(repo_root, {"roles": roles})["platforms"]
    assert capabilities["antigravity"]["native_subagents"] is not True
    assert capabilities["cursor"]["native_subagents"] is not True
    outputs = adapter_outputs(repo_root)
    antigravity_role_files = [
        content for path, content in outputs.items()
        if "/adapters/antigravity/role-profiles/" in path.as_posix()
    ]
    cursor_role_files = [
        content for path, content in outputs.items()
        if "/adapters/cursor/role-profiles/" in path.as_posix()
    ]
    assert antigravity_role_files, "expected at least one antigravity role profile"
    assert cursor_role_files, "expected at least one cursor role profile"
    for content in antigravity_role_files + cursor_role_files:
        assert "main-agent role profile" in content
        assert "native subagent" not in content


def test_link_strategy_plan_windows_leads_with_junction(monkeypatch):
    fake_home = Path("/tmp/fake-windows-home")
    # Path.home() would try to build a real WindowsPath on this OS and fail;
    # stub it before flipping os.name so only the link_strategy branch is exercised.
    monkeypatch.setattr(platforms_module.Path, "home", classmethod(lambda cls: fake_home))
    monkeypatch.setattr(platforms_module.os, "name", "nt")
    detected = detect_platforms()
    assert detected["link_strategy"][0] == "junction"
    assert "symlink" in detected["link_strategy"]


def test_link_strategy_plan_posix_has_no_junction(monkeypatch):
    monkeypatch.setattr(platforms_module.os, "name", "posix")
    detected = detect_platforms()
    assert "junction" not in detected["link_strategy"]
    assert detected["link_strategy"][0] == "symlink"
