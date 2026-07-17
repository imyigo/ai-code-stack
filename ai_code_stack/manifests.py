from __future__ import annotations

import hashlib
from pathlib import Path

from .filesystem import atomic_write_json, normalized, sha256
from .inventory import build_capabilities, build_repository_inventory, build_skill_inventory, load_lock, load_roles
from .result import Result


MANIFEST_FILES = (
    "repositories.json", "skills.json", "platforms.json", "roles.json",
    "capabilities.json", "links.json", "checksums.json",
)


def build_payloads(root: Path) -> dict[str, dict]:
    lock = load_lock(root)
    roles = load_roles(root)
    skills = build_skill_inventory(root)
    repositories = build_repository_inventory(root, lock)
    capabilities = build_capabilities(root, roles)
    platforms = {
        "schema_version": 1,
        "platforms": {name: {
            "installed": data["installed"], "version": data["version"],
            "adapter_path": f"adapters/{name}", "adapter_mode": data["adapter_mode"],
        } for name, data in capabilities["platforms"].items()},
    }
    links = {
        "schema_version": 1,
        "policy": {"windows": ["junction", "symlink", "controlled_copy"], "macos": ["symlink", "controlled_copy"], "linux": ["symlink", "controlled_copy"]},
        "active_root": None,
        "entries": [{"name": row["active_name"], "source": row["source_path"], "mode": row["activation"]} for row in skills["skills"]],
    }
    return {
        "repositories.json": repositories, "skills.json": skills, "platforms.json": platforms,
        "roles.json": roles, "capabilities.json": capabilities, "links.json": links,
    }


def build_manifests(root: Path, dry_run: bool = False) -> Result:
    payloads = build_payloads(root)
    artifacts = [str(root / "manifests" / name) for name in MANIFEST_FILES]
    if dry_run:
        return Result("success", "Manifest dry-run completed; no files changed.", ["Run without --dry-run after review."], artifacts, {"counts": {name: len(payload) for name, payload in payloads.items()}})
    for name, payload in payloads.items():
        atomic_write_json(root / "manifests" / name, payload)
    checks = []
    excluded = {root / "manifests" / "checksums.json"}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path in excluded or ".git" in path.parts or "vendors" in path.parts or "__pycache__" in path.parts:
            continue
        checks.append({"path": path.relative_to(root).as_posix(), "sha256": sha256(path)})
    atomic_write_json(root / "manifests" / "checksums.json", {"schema_version": 1, "files": checks})
    return Result("success", f"Generated {len(MANIFEST_FILES)} manifests.", [], artifacts)
