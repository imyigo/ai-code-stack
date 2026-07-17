from __future__ import annotations

import re
import shutil
from pathlib import Path

from .adapters import adapter_outputs
from .filesystem import GENERATED_MARKER, atomic_write_text
from .result import Result

# detect_platforms() in platforms.py answers a narrower question (is the CLI binary
# on PATH, verified enough to claim native_subagents=True?). Placing config files only
# needs "does this platform's own config directory already exist on this machine" —
# true even when the CLI runs through an SDK/managed harness with no binary on PATH.
_CONFIG_DIR_NAMES = {"codex": ".codex", "claude-code": ".claude", "cursor": ".cursor"}


def _codex_agents_md(root: Path) -> str:
    source = (root / "config" / "AGENTS.md").read_text(encoding="utf-8")
    return f"<!-- {GENERATED_MARKER}; source: config/AGENTS.md -->\n\n{source}"


def _claude_code_agent_files(root: Path) -> dict[Path, str]:
    outputs = adapter_outputs(root)
    home = Path.home()
    return {
        home / ".claude" / "agents" / path.name: content
        for path, content in outputs.items()
        if "/adapters/claude-code/.claude/agents/" in path.as_posix()
    }


def _cursor_rule_file(root: Path) -> dict[Path, str]:
    outputs = adapter_outputs(root)
    home = Path.home()
    for path, content in outputs.items():
        if path.as_posix().endswith("/adapters/cursor/.cursor/rules/ai-code-stack.mdc"):
            return {home / ".cursor" / "rules" / "ai-code-stack.mdc": content}
    return {}


def _write_or_skip(path: Path, content: str, dry_run: bool, planned: list[str], written: list[str], skipped: list[str]) -> None:
    planned.append(str(path))
    if dry_run:
        return
    try:
        atomic_write_text(path, content)
        written.append(str(path))
    except FileExistsError:
        skipped.append(str(path))


def _configure_codex_graphify_mcp(home: Path, dry_run: bool) -> dict:
    graphify_mcp = shutil.which("graphify-mcp")
    if not graphify_mcp:
        return {"status": "skipped", "reason": "graphify-mcp binary not found on PATH"}
    codex_dir = home / ".codex"
    if not codex_dir.is_dir():
        return {"status": "skipped", "reason": f"{codex_dir} does not exist"}
    config_path = codex_dir / "config.toml"
    if dry_run:
        return {"status": "planned", "path": str(config_path), "command": graphify_mcp}
    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    escaped = graphify_mcp.replace("'", "''")
    section = f"[mcp_servers.graphify]\ncommand = '{escaped}'\nargs = []\nstartup_timeout_sec = 120\n"
    pattern = re.compile(r"\n?\[mcp_servers\.graphify\][\s\S]*?(?=\n\[[^\]]+\]|\s*$)", re.MULTILINE)
    if pattern.search(text):
        text = pattern.sub(f"\n{section}", text)
    elif text.strip():
        text = f"{text.rstrip()}\n\n{section}"
    else:
        text = section
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(text, encoding="utf-8")
    return {"status": "written", "path": str(config_path)}


def _present(home: Path, platform_id: str) -> bool:
    return (home / _CONFIG_DIR_NAMES[platform_id]).is_dir()


def global_install(root: Path, dry_run: bool) -> Result:
    home = Path.home()
    planned: list[str] = []
    written: list[str] = []
    skipped: list[str] = []
    per_platform: dict[str, dict] = {}

    if _present(home, "codex"):
        targets = {home / ".codex" / "AGENTS.md": _codex_agents_md(root)}
        for path, content in targets.items():
            _write_or_skip(path, content, dry_run, planned, written, skipped)
        per_platform["codex"] = {
            "agents_md": [str(p) for p in targets],
            "mcp": _configure_codex_graphify_mcp(home, dry_run),
        }
    else:
        per_platform["codex"] = {"status": "skipped", "reason": f"{home / '.codex'} not found"}

    if _present(home, "claude-code"):
        targets = _claude_code_agent_files(root)
        for path, content in targets.items():
            _write_or_skip(path, content, dry_run, planned, written, skipped)
        per_platform["claude-code"] = {"agent_files": [str(p) for p in targets]}
    else:
        per_platform["claude-code"] = {"status": "skipped", "reason": f"{home / '.claude'} not found"}

    if _present(home, "cursor"):
        targets = _cursor_rule_file(root)
        for path, content in targets.items():
            _write_or_skip(path, content, dry_run, planned, written, skipped)
        per_platform["cursor"] = {"rule_files": [str(p) for p in targets]}
    else:
        per_platform["cursor"] = {"status": "skipped", "reason": f"{home / '.cursor'} not found"}

    per_platform["antigravity"] = {
        "status": "skipped",
        "reason": "no verified global config file format for antigravity yet; "
                  "role profiles remain repo-local under adapters/antigravity/",
    }

    if dry_run:
        return Result(
            "success",
            f"Global install dry-run planned {len(planned)} file write(s) across detected platforms; no state changed.",
            ["Rerun with --apply to write. Hand-written files at the same path are never overwritten."],
            planned,
            {"platforms": per_platform},
        )
    next_actions = []
    if skipped:
        next_actions.append(f"{len(skipped)} pre-existing hand-written file(s) were left untouched: {', '.join(skipped)}")
    return Result(
        "success",
        f"Global install wrote {len(written)} file(s); skipped {len(skipped)} pre-existing hand-written file(s).",
        next_actions,
        written,
        {"platforms": per_platform, "skipped": skipped},
    )
