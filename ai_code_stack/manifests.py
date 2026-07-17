from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from .filesystem import atomic_write_json, normalized, sha256
from .inventory import build_capabilities, build_repository_inventory, build_skill_inventory, load_lock, load_roles
from .result import Result


MANIFEST_FILES = (
    "repositories.json", "skills.json", "platforms.json", "roles.json",
    "capabilities.json", "links.json", "knowledge-registry.json",
    "skill-routing.json", "token-costs.json", "cache-state.json", "checksums.json",
)

_EXCLUDED_DIR_NAMES = {".git", "vendors", "__pycache__", "backups", "work", ".gate-test"}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def build_knowledge_registry(root: Path) -> dict:
    policy = _load_yaml(root / "policies" / "knowledge-registry.yaml")
    return {
        "schema_version": 1,
        "includes": policy.get("includes", []),
        "excludes": policy.get("excludes", []),
        "manifests": policy.get("manifests", []),
        "statement": "A skill's removal from active context does not mean the skill is deleted from the system or forgotten.",
    }


def build_skill_routing(root: Path, skills: dict) -> dict:
    routing = _load_yaml(root / "policies" / "routing.yaml")
    graphify = _load_yaml(root / "policies" / "graphify-routing.yaml")
    execution_budget = _load_yaml(root / "policies" / "execution-budget.yaml")
    return {
        "schema_version": 1,
        "singletons": routing.get("singletons", {}),
        "graphify": {"role_policy": graphify, "legacy_routing": routing.get("graphify", {})},
        "security_flow": routing.get("security", {}),
        "caveman": routing.get("caveman", {}),
        "task_classes": execution_budget.get("task_classes", {}),
        "alias_routes": sorted({row["active_name"] for row in skills["skills"] if row["active_name"] != row["vendor_name"]}),
    }


def build_token_costs(root: Path, skills: dict) -> dict:
    # Deterministic estimate derived from source file size (~4 bytes per token); not a
    # measured value. Every entry is explicitly marked as an estimate.
    rows = []
    for row in skills["skills"]:
        size = (root / row["skill_file"]).stat().st_size
        rows.append({
            "active_name": row["active_name"],
            "source_bytes": size,
            "estimated_tokens_full": {"value": max(1, size // 4), "estimate": True},
            "estimated_tokens_metadata": {"value": 40, "estimate": True},
        })
    return {"schema_version": 1, "estimation_method": "source_bytes_div_4", "skills": rows}


def build_cache_state(root: Path, skills: dict, repositories: dict) -> dict:
    cache_policy = _load_yaml(root / "policies" / "cache.yaml")
    entries = [{
        "cache_key": f"{row['repository']}:{row['active_name']}:{row['sha256'][:16]}",
        "source_commit": next((repo["commit"] for repo in repositories["repositories"] if repo["name"] == row["repository"]), None),
        "checksum": row["sha256"],
        "cache_validity": "valid_while_source_checksum_and_commit_unchanged",
    } for row in skills["skills"]]
    return {
        "schema_version": 1,
        "invalidation_signals": cache_policy.get("invalidation_signals", []),
        "reparse_full_catalog_when_source_unchanged": cache_policy.get("rules", {}).get("reparse_full_catalog_when_source_unchanged", False),
        "entries": entries,
    }


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
        "knowledge-registry.json": build_knowledge_registry(root),
        "skill-routing.json": build_skill_routing(root, skills),
        "token-costs.json": build_token_costs(root, skills),
        "cache-state.json": build_cache_state(root, skills, repositories),
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
        if not path.is_file() or path in excluded or _EXCLUDED_DIR_NAMES & set(path.parts):
            continue
        checks.append({"path": path.relative_to(root).as_posix(), "sha256": sha256(path)})
    atomic_write_json(root / "manifests" / "checksums.json", {"schema_version": 1, "files": checks})
    return Result("success", f"Generated {len(MANIFEST_FILES)} manifests.", [], artifacts)
