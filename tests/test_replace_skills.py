from __future__ import annotations

from pathlib import Path

from ai_code_stack import replace_skills as replace_skills_module
from ai_code_stack.replace_skills import replace_skills


def _use_fake_home(monkeypatch, fake_home: Path) -> None:
    monkeypatch.setattr(replace_skills_module.Path, "home", classmethod(lambda cls: fake_home))


def test_dry_run_moves_and_writes_nothing(repo_root: Path, tmp_path: Path, monkeypatch):
    home = tmp_path / "home"
    claude_skills = home / ".claude" / "skills"
    claude_skills.mkdir(parents=True)
    (claude_skills / "old-skill").mkdir()
    (claude_skills / "old-skill" / "SKILL.md").write_text("old", encoding="utf-8")
    (home / ".codex" / "skills").mkdir(parents=True)
    _use_fake_home(monkeypatch, home)

    result = replace_skills(repo_root, dry_run=True)

    assert result.status == "success"
    assert claude_skills.is_dir()
    assert (claude_skills / "old-skill").is_dir()
    assert result.details["platforms"]["claude-code"]["existing_entries_to_move_aside"] == 1
    assert result.details["platforms"]["claude-code"]["skills_to_write"] == 455


def test_apply_moves_existing_dir_aside_and_writes_all_skills(repo_root: Path, tmp_path: Path, monkeypatch):
    home = tmp_path / "home"
    claude_skills = home / ".claude" / "skills"
    claude_skills.mkdir(parents=True)
    (claude_skills / "old-skill").mkdir()
    (claude_skills / "old-skill" / "SKILL.md").write_text("old content, must survive", encoding="utf-8")
    _use_fake_home(monkeypatch, home)

    result = replace_skills(repo_root, dry_run=False)

    claude_result = result.details["platforms"]["claude-code"]
    assert claude_result["status"] == "replaced"
    backup_dir = Path(claude_result["backup"])
    assert (backup_dir / "old-skill" / "SKILL.md").read_text(encoding="utf-8") == "old content, must survive"
    assert not (claude_skills / "old-skill").exists()
    assert (claude_skills / "caveman" / "SKILL.md").is_file()
    assert claude_result["skills_written"] == 455


def test_apply_skips_platform_with_no_config_dir(repo_root: Path, tmp_path: Path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    _use_fake_home(monkeypatch, home)

    result = replace_skills(repo_root, dry_run=False)

    assert result.details["platforms"]["claude-code"]["status"] == "skipped"
    assert result.details["platforms"]["codex"]["status"] == "skipped"


def test_antigravity_always_skipped(repo_root: Path, tmp_path: Path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    _use_fake_home(monkeypatch, home)

    result = replace_skills(repo_root, dry_run=True)

    assert result.details["platforms"]["antigravity"]["status"] == "skipped"


def test_apply_creates_skills_dir_when_absent(repo_root: Path, tmp_path: Path, monkeypatch):
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    _use_fake_home(monkeypatch, home)

    result = replace_skills(repo_root, dry_run=False)

    codex_result = result.details["platforms"]["codex"]
    assert codex_result["status"] == "replaced"
    assert codex_result["backup"] is None
    assert (home / ".codex" / "skills" / "caveman" / "SKILL.md").is_file()
