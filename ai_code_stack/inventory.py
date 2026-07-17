from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

from .filesystem import normalized, sha256
from .frontmatter import parse_frontmatter
from .platforms import detect_platforms


@dataclass(frozen=True)
class SkillSource:
    repository: str
    source_dir: Path
    skill_file: Path


def _git(path: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path), *args],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return completed.stdout.strip()


def _skill_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())


def discover_sources(root: Path) -> list[SkillSource]:
    vendors = root / "vendors"
    sources: list[SkillSource] = []
    for directory in _skill_dirs(vendors / "ecc" / "skills"):
        sources.append(SkillSource("ecc", directory, directory / "SKILL.md"))
    gstack = vendors / "gstack"
    if (gstack / "SKILL.md").is_file():
        sources.append(SkillSource("gstack", gstack, gstack / "SKILL.md"))
    for directory in _skill_dirs(gstack):
        sources.append(SkillSource("gstack", directory, directory / "SKILL.md"))
    graphify_file = vendors / "graphify" / "graphify" / "skill.md"
    if graphify_file.is_file():
        sources.append(SkillSource("graphify", graphify_file.parent, graphify_file))
    for directory in _skill_dirs(vendors / "caveman" / "skills"):
        sources.append(SkillSource("caveman", directory, directory / "SKILL.md"))
    allowlist = {
        line.strip() for line in (root / "config" / "cybersecurity-skills.allowlist").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    cyber_root = vendors / "cybersecurity" / "skills"
    for name in sorted(allowlist):
        directory = cyber_root / name
        if not (directory / "SKILL.md").is_file():
            raise FileNotFoundError(f"allowlisted Cybersecurity skill missing: {name}")
        sources.append(SkillSource("cybersecurity", directory, directory / "SKILL.md"))
    return sources


def build_skill_inventory(root: Path) -> dict:
    alias_config = json.loads((root / "overlays" / "shared" / "aliases.json").read_text(encoding="utf-8"))
    explicit_aliases = {
        (value["source"].lower(), value["vendor_name"]): alias
        for alias, value in alias_config["aliases"].items()
    }
    rows: list[dict] = []
    used: dict[str, str] = {}
    duplicates: list[dict] = []
    for source in discover_sources(root):
        frontmatter, _ = parse_frontmatter(source.skill_file)
        vendor_name = frontmatter["name"].strip()
        active_name = explicit_aliases.get((source.repository, vendor_name), vendor_name)
        if active_name in used:
            if source.repository == "gstack":
                active_name = f"gstack-{vendor_name}"
            if active_name in used:
                duplicates.append({"name": active_name, "first": used[active_name], "second": source.repository})
                continue
        used[active_name] = source.repository
        rows.append({
            "active_name": active_name,
            "vendor_name": vendor_name,
            "repository": source.repository,
            "source_path": source.source_dir.relative_to(root).as_posix(),
            "skill_file": source.skill_file.relative_to(root).as_posix(),
            "frontmatter": frontmatter,
            "sha256": sha256(source.skill_file),
            "activation": "controlled_copy_with_overlay" if active_name in {"benchmark", "gstack-benchmark", "graphify", "gstack-cso", "gstack-ship"} else "link",
        })
    return {
        "schema_version": 1,
        "records": len(rows),
        "unique_active_names": len(used),
        "duplicates": duplicates,
        "skills": rows,
    }


def build_repository_inventory(root: Path, lock: dict) -> dict:
    rows = []
    for name, expected in lock["repositories"].items():
        path = root / "vendors" / name
        rows.append({
            "name": name, "path": path.relative_to(root).as_posix(), "url": expected["url"],
            "commit": _git(path, "rev-parse", "HEAD"), "expected_commit": expected["commit"],
            "branch": _git(path, "branch", "--show-current") or None,
            "tag": _git(path, "describe", "--tags", "--exact-match") if _has_exact_tag(path) else None,
            "clean": not bool(_git(path, "status", "--porcelain")), "submodule": True,
        })
    return {"schema_version": 1, "repositories": rows}


def _has_exact_tag(path: Path) -> bool:
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path), "describe", "--tags", "--exact-match"],
        check=False, capture_output=True, text=True, timeout=15,
    )
    return completed.returncode == 0


def load_roles(root: Path) -> dict:
    payload = yaml.safe_load((root / "roles" / "common" / "roles.yaml").read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("roles"), list):
        raise ValueError("invalid common role registry")
    names = [role.get("name") for role in payload["roles"]]
    if len(names) != len(set(names)) or any(not isinstance(name, str) for name in names):
        raise ValueError("duplicate or invalid common role name")
    return payload


def build_capabilities(root: Path, roles: dict) -> dict:
    detected = detect_platforms()
    matrix = {}
    for platform_id, capability in detected["platforms"].items():
        native = capability["native_subagents"] is True
        matrix[platform_id] = {
            **capability,
            "roles": [{
                "name": role["name"], "supported": native,
                "fallback": None if native else "main-agent-role-profile",
                "reason": capability["native_evidence"],
            } for role in roles["roles"]],
            "cross_platform_delegation": False,
        }
    return {"schema_version": 1, "host": detected["host"], "link_strategy": detected["link_strategy"], "platforms": matrix}


def load_lock(root: Path) -> dict:
    return json.loads((root / "versions.lock").read_text(encoding="utf-8-sig"))
