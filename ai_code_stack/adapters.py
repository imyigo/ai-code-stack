from __future__ import annotations

from pathlib import Path

import yaml

from .filesystem import GENERATED_MARKER, atomic_write_text
from .inventory import build_capabilities, load_roles
from .result import Result


def _role_body(role: dict, platform_id: str, native: bool) -> str:
    skills = ", ".join(role.get("skills", []))
    mode = "native subagent" if native else "main-agent role profile"
    return f"""# {role['name']}

<!-- {GENERATED_MARKER}; source: roles/common/roles.yaml -->

Platform: `{platform_id}`  
Mode: `{mode}`

Purpose: {role['purpose']}.

Load no more than five matching skills. Preferred skills: {skills}.

Work only inside the current platform. Do not call, route to, or delegate to another coding-agent platform. Require a task contract, acceptance criteria, and owned paths before parallel work. Do not spawn nested subagents.
"""


def _claude_agent(role: dict) -> str:
    frontmatter = yaml.safe_dump({
        "name": role["name"], "description": role["purpose"],
        "tools": "Glob, Grep, Read, Edit, Write, Bash",
    }, sort_keys=False).strip()
    return f"---\n{frontmatter}\n---\n\n{_role_body(role, 'claude-code', True)}"


def adapter_outputs(root: Path) -> dict[Path, str]:
    roles = load_roles(root)["roles"]
    capabilities = build_capabilities(root, {"roles": roles})["platforms"]
    outputs: dict[Path, str] = {}
    for role in roles:
        outputs[root / "adapters" / "claude-code" / ".claude" / "agents" / f"{role['name']}.md"] = _claude_agent(role)
        for platform_id in ("codex", "cursor", "antigravity"):
            native = capabilities[platform_id]["native_subagents"] is True
            outputs[root / "adapters" / platform_id / "role-profiles" / f"{role['name']}.md"] = _role_body(role, platform_id, native)
    cursor_rule = f"""---
description: AI Code Stack independent-platform routing
alwaysApply: true
---

<!-- {GENERATED_MARKER}; source: policies/runtime.yaml + policies/routing.yaml -->

Use shared skills lazily, at most five per task. Use role profiles from `../role-profiles/`. Never delegate to Claude Code, Codex, or Antigravity. Keep cross-platform delegation, nested subagents, shared agent memory, and central scheduling disabled. Security is fail-closed.
"""
    outputs[root / "adapters" / "cursor" / ".cursor" / "rules" / "ai-code-stack.mdc"] = cursor_rule
    outputs[root / "adapters" / "codex" / "AGENTS.generated.md"] = _role_body({"name": "codex-native-runtime", "purpose": "Use Codex stable multi_agent only inside Codex", "skills": ["gstack", "coding-standards"]}, "codex", True)
    outputs[root / "adapters" / "antigravity" / "CAPABILITY.generated.md"] = _role_body({"name": "antigravity-main-agent", "purpose": "Use role profiles until a native subagent file format is verified", "skills": ["gstack", "coding-standards"]}, "antigravity", False)
    return outputs


def build_adapters(root: Path, dry_run: bool = False) -> Result:
    outputs = adapter_outputs(root)
    artifacts = [str(path) for path in sorted(outputs)]
    if dry_run:
        return Result("success", f"Adapter dry-run planned {len(outputs)} generated files; no state changed.", ["Review capability fallbacks before applying."], artifacts)
    for path, content in outputs.items():
        atomic_write_text(path, content)
    return Result("success", f"Generated {len(outputs)} platform adapter files.", [], artifacts)
