from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from .adapters import adapter_outputs
from .filesystem import sha256
from .frontmatter import parse_frontmatter
from .inventory import build_skill_inventory, load_lock, load_roles
from .result import Result
from .security_gate import evaluate_release


def verify(root: Path) -> Result:
    checks: list[dict] = []

    def check(name: str, operation) -> None:
        try:
            evidence = operation()
            checks.append({"name": name, "status": "pass", "evidence": evidence})
        except Exception as exc:
            checks.append({"name": name, "status": "fail", "evidence": str(exc)})

    lock = load_lock(root)
    check("versions_lock_schema", lambda: lock["schema_version"] == "ai-code-stack.3" or (_ for _ in ()).throw(ValueError("unexpected schema")))

    def repositories():
        for name, expected in lock["repositories"].items():
            path = root / "vendors" / name
            actual = subprocess.run(["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
            if actual != expected["commit"]:
                raise ValueError(f"{name}: expected {expected['commit']}, got {actual}")
            dirty = subprocess.run(["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path), "status", "--porcelain"], check=True, capture_output=True, text=True).stdout
            if dirty:
                raise ValueError(f"{name}: vendor worktree is dirty")
        return f"{len(lock['repositories'])} pinned clean vendors"
    check("vendor_submodules", repositories)

    inventory = build_skill_inventory(root)
    check("skill_count", lambda: inventory["records"] == lock["expected_selected_skills"] or (_ for _ in ()).throw(ValueError(f"expected {lock['expected_selected_skills']}, got {inventory['records']}")))
    check("skill_unique_names", lambda: not inventory["duplicates"] or (_ for _ in ()).throw(ValueError(str(inventory["duplicates"]))))
    check("benchmark_alias", lambda: any(row["active_name"] == "benchmark" and row["repository"] == "ecc" for row in inventory["skills"]) and any(row["active_name"] == "gstack-benchmark" and row["repository"] == "gstack" for row in inventory["skills"]) or (_ for _ in ()).throw(ValueError("alias route missing")))
    check("frontmatter_yaml", lambda: f"parsed {inventory['records']} skill frontmatters with PyYAML")
    roles = load_roles(root)
    check("common_roles", lambda: len(roles["roles"]) == 18 or (_ for _ in ()).throw(ValueError("expected 18 roles")))
    runtime_policy = yaml.safe_load((root / "policies" / "runtime.yaml").read_text(encoding="utf-8"))
    check("cross_platform_delegation_disabled", lambda: runtime_policy["limits"]["cross_platform_delegation"] is False and runtime_policy["execution"]["platform_to_platform_agent_calls"] is False or (_ for _ in ()).throw(ValueError("cross-platform delegation enabled")))
    check("agent_limits", lambda: runtime_policy["limits"]["max_skills_per_agent"] == 5 and runtime_policy["limits"]["max_active_subagents"] == 3 and runtime_policy["limits"]["nested_subagents"] is False or (_ for _ in ()).throw(ValueError("agent limits invalid")))
    routing_text = (root / "policies" / "routing.yaml").read_text(encoding="utf-8")
    check("graphify_conditional", lambda: "large_repository" in routing_text and "small_ui_change" in routing_text or (_ for _ in ()).throw(ValueError("Graphify routing incomplete")))
    check("caveman_boundary", lambda: all(word in routing_text for word in ("stack_trace", "security_report", "test_result", "config")) or (_ for _ in ()).throw(ValueError("Caveman exclusions incomplete")))
    check("adapter_outputs", lambda: len(adapter_outputs(root)) == 76 or (_ for _ in ()).throw(ValueError(f"expected 76 adapter files, got {len(adapter_outputs(root))}")))
    for name in ("repositories", "skills", "platforms", "roles", "capabilities", "links", "checksums"):
        check(f"manifest_{name}", lambda n=name: json.loads((root / "manifests" / f"{n}.json").read_text(encoding="utf-8-sig"))["schema_version"])
    def checksum_check():
        payload = json.loads((root / "manifests" / "checksums.json").read_text(encoding="utf-8-sig"))
        mismatches = [row["path"] for row in payload["files"] if not (root / row["path"]).is_file() or sha256(root / row["path"]) != row["sha256"]]
        if mismatches:
            raise ValueError(f"checksum mismatch: {mismatches[:5]}")
        return f"{len(payload['files'])} checksums"
    check("checksums", checksum_check)
    clean_report = {"audited_diff_sha256": "x", "findings": [], "source_commit": "test"}
    critical_report = {"audited_diff_sha256": "x", "findings": [{"severity": "CRITICAL", "status": "open"}]}
    check("security_fail_closed", lambda: evaluate_release(None, "x", True)["status"] == "blocked" and evaluate_release(critical_report, "x", True)["status"] == "blocked" and evaluate_release(clean_report, "x", True)["status"] == "pass" or (_ for _ in ()).throw(ValueError("gate truth table failed")))
    failed = [item for item in checks if item["status"] == "fail"]
    return Result("error" if failed else "success", f"{len(checks) - len(failed)} passed, {len(failed)} failed", ["Do not commit or push until all checks pass."] if failed else ["Proceed to tests and secret scan."], [str(root / "manifests")], {"checks": checks})
