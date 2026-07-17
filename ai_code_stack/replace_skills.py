from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .result import Result

_SKILLS_DIR_NAMES = {"claude-code": ".claude", "codex": ".codex"}


def _skill_sources(root: Path) -> dict[str, Path]:
    manifest = json.loads((root / "manifests" / "skills.json").read_text(encoding="utf-8"))
    return {entry["active_name"]: root / entry["source_path"] for entry in manifest["skills"]}


def _replace_platform_skills(root: Path, home: Path, platform_id: str, dry_run: bool) -> dict:
    target_root = home / _SKILLS_DIR_NAMES[platform_id] / "skills"
    sources = _skill_sources(root)
    existing_count = len(list(target_root.iterdir())) if target_root.is_dir() else 0

    if dry_run:
        return {
            "status": "planned",
            "target": str(target_root),
            "existing_entries_to_move_aside": existing_count,
            "skills_to_write": len(sources),
        }

    backup_path = None
    if target_root.is_dir():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = target_root.parent / f"skills.backup-{timestamp}"
        shutil.move(str(target_root), str(backup_path))
    target_root.mkdir(parents=True, exist_ok=True)
    for active_name, source_dir in sorted(sources.items()):
        shutil.copytree(source_dir, target_root / active_name)
    return {
        "status": "replaced",
        "target": str(target_root),
        "backup": str(backup_path) if backup_path else None,
        "skills_written": len(sources),
    }


def replace_skills(root: Path, dry_run: bool) -> Result:
    home = Path.home()
    per_platform: dict[str, dict] = {}
    for platform_id in ("claude-code", "codex"):
        config_dir = home / _SKILLS_DIR_NAMES[platform_id]
        if config_dir.is_dir():
            per_platform[platform_id] = _replace_platform_skills(root, home, platform_id, dry_run)
        else:
            per_platform[platform_id] = {"status": "skipped", "reason": f"{config_dir} not found"}
    per_platform["antigravity"] = {
        "status": "skipped",
        "reason": "no skills/ directory exists for Antigravity on this machine (checked ~/Library/Application Support/Antigravity)",
    }

    if dry_run:
        return Result(
            "success",
            "replace-skills dry-run planned; no files moved or written.",
            ["Rerun with --apply. The existing skills/ directory is moved aside (not deleted) as a backup before writing, per platform."],
            [],
            {"platforms": per_platform},
        )

    backups = [v["backup"] for v in per_platform.values() if isinstance(v, dict) and v.get("backup")]
    replaced_count = sum(1 for v in per_platform.values() if isinstance(v, dict) and v.get("status") == "replaced")
    return Result(
        "success",
        f"Replaced skills/ on {replaced_count} platform(s) with the {len(_skill_sources(root))} skills selected by this repo.",
        [f"Previous content preserved at: {b}" for b in backups],
        backups,
        {"platforms": per_platform},
    )
