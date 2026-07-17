from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .adapters import build_adapters
from .filesystem import copy_backup, link_strategy, normalized
from .inventory import load_lock
from .manifests import build_manifests
from .result import Result


def install_plan(root: Path) -> list[dict]:
    lock = load_lock(root)
    return [
        {"action": "verify_runtime", "python_min": lock["runtimes"]["python_min"]},
        {"action": "verify_submodules", "vendors": list(lock["repositories"])},
        {"action": "build_manifests", "canonical": "python"},
        {"action": "build_adapters", "platforms": ["claude-code", "antigravity", "codex", "cursor"]},
        {"action": "plan_skill_links", "strategies": {"windows": link_strategy("windows"), "posix": link_strategy("posix")}},
        {"action": "preserve_configs", "mode": "merge-or-include-only"},
        {"action": "verify", "fail_closed": True},
    ]


def _submodule_populated(vendor_dir: Path) -> bool:
    return vendor_dir.is_dir() and any(vendor_dir.iterdir())


def ensure_submodules(root: Path, dry_run: bool) -> list[dict]:
    lock = load_lock(root)
    statuses: list[dict] = []
    missing: list[str] = []
    for name in lock["repositories"]:
        vendor_dir = root / "vendors" / name
        if _submodule_populated(vendor_dir):
            statuses.append({"vendor": name, "status": "already_present"})
        else:
            missing.append(name)
            statuses.append({"vendor": name, "status": "would_fetch" if dry_run else "fetching"})
    if not missing or dry_run:
        return statuses
    subprocess.run(
        ["git", "-C", str(root), "submodule", "update", "--init", "--", *(f"vendors/{name}" for name in missing)],
        check=True, capture_output=True, text=True, timeout=600,
    )
    for entry in statuses:
        if entry["vendor"] in missing:
            entry["status"] = "fetched" if _submodule_populated(root / "vendors" / entry["vendor"]) else "fetch_failed"
    failed = [entry["vendor"] for entry in statuses if entry["status"] == "fetch_failed"]
    if failed:
        raise RuntimeError(f"submodule fetch did not populate: {', '.join(failed)}")
    return statuses


def create_backup(root: Path) -> Path:
    backup = root / "backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup.mkdir(parents=True, exist_ok=False)
    for relative in ("manifests", "adapters", "versions.lock", "AGENTS.md", "CLAUDE.md"):
        source = root / relative
        if source.exists():
            copy_backup(source, backup / relative)
    (backup / "journal.json").write_text(json.dumps({
        "schema_version": 1, "status": "prepared", "root": normalized(root), "created": datetime.now(timezone.utc).isoformat(), "actions": [],
    }, indent=2), encoding="utf-8")
    return backup


def install(root: Path, dry_run: bool) -> Result:
    plan = install_plan(root)
    artifacts = [str(root / "versions.lock"), str(root / "manifests"), str(root / "adapters")]
    if dry_run:
        submodules = ensure_submodules(root, dry_run=True)
        return Result("success", "Install dry-run completed; no files, links, configs, submodules, commits, or remotes changed.", ["Review the plan before --apply."], artifacts, {"actions": plan, "submodules": submodules})
    submodules = ensure_submodules(root, dry_run=False)
    backup = create_backup(root)
    try:
        adapters = build_adapters(root)
        manifests = build_manifests(root)
        journal_path = backup / "journal.json"
        journal = json.loads(journal_path.read_text(encoding="utf-8"))
        journal.update({"status": "applied", "actions": plan})
        journal_path.write_text(json.dumps(journal, indent=2), encoding="utf-8")
        return Result("success", "Canonical manifests and adapters installed. Live platform configs and skill roots were preserved.", ["Run verify before activating any optional link plan.", "Run 'ai-code-stack global-install --apply' to place generated config into installed platforms (Codex/Claude Code/Cursor/Antigravity), if desired."], artifacts + [str(backup)], {"submodules": submodules, "manifests": manifests.to_dict(), "adapters": adapters.to_dict()})
    except Exception:
        rollback(root, backup)
        raise


def rollback(root: Path, backup: Path) -> Result:
    journal_path = backup / "journal.json"
    if not journal_path.is_file():
        raise FileNotFoundError(f"rollback journal missing: {journal_path}")
    for relative in ("manifests", "adapters"):
        current, saved = root / relative, backup / relative
        if current.exists():
            shutil.rmtree(current)
        if saved.exists():
            shutil.copytree(saved, current)
    for relative in ("versions.lock", "AGENTS.md", "CLAUDE.md"):
        saved = backup / relative
        if saved.exists():
            shutil.copy2(saved, root / relative)
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    journal["status"] = "rolled_back"
    journal_path.write_text(json.dumps(journal, indent=2), encoding="utf-8")
    return Result("success", "Rolled back the failed install stage.", [], [str(backup)])
