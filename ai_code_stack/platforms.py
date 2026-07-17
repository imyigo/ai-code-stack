from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path


PLATFORM_IDS = ("claude-code", "antigravity", "codex", "cursor")


def command_version(command: str, *args: str) -> tuple[str | None, str | None]:
    executable = shutil.which(command) or shutil.which(f"{command}.cmd")
    if not executable:
        return None, None
    try:
        completed = subprocess.run([executable, *args], check=False, capture_output=True, text=True, timeout=15)
        output = (completed.stdout or completed.stderr).strip().splitlines()
        return executable, output[0] if output else None
    except (OSError, subprocess.TimeoutExpired):
        return executable, None


def detect_platforms() -> dict:
    home = Path.home()
    claude_path, claude_version = command_version("claude", "--version")
    agy_path, agy_version = command_version("agy", "--version")
    codex_path, codex_version = command_version("codex", "--version")
    cursor_path, cursor_version = command_version("cursor", "--version")
    return {
        "host": {"os": platform.system().lower(), "python": platform.python_version()},
        "platforms": {
            "claude-code": {
                "installed": bool(claude_path), "executable": claude_path, "version": claude_version,
                "native_subagents": True if claude_path else None,
                "native_evidence": "local CLI exposes --agent/--agents and agents command" if claude_path else "not installed",
                "adapter_mode": "native-agent-files", "config_candidates": [str(home / ".claude" / "settings.json")],
            },
            "antigravity": {
                "installed": bool(agy_path), "executable": agy_path, "version": agy_version,
                "native_subagents": None,
                "native_evidence": "local agy help does not expose a verified agent/subagent file format",
                "adapter_mode": "main-agent-role-profile", "config_candidates": [],
            },
            "codex": {
                "installed": bool(codex_path), "executable": codex_path, "version": codex_version,
                "native_subagents": True if codex_path else None,
                "native_evidence": "local Codex features reports multi_agent stable and enabled" if codex_path else "not installed",
                "adapter_mode": "native-runtime-plus-role-profiles", "config_candidates": [str(home / ".codex" / "config.toml")],
            },
            "cursor": {
                "installed": bool(cursor_path), "executable": cursor_path, "version": cursor_version,
                "native_subagents": None,
                "native_evidence": "local CLI exposes agent and MCP but no verified static subagent contract",
                "adapter_mode": "rules-and-main-agent-role-profile", "config_candidates": [str(home / ".cursor" / "mcp.json")],
            },
        },
        "link_strategy": ["junction", "symlink", "controlled_copy"] if os.name == "nt" else ["symlink", "controlled_copy"],
    }
