from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


class FrontmatterError(ValueError):
    pass


_TOP_LEVEL_SCALAR = re.compile(r"^([A-Za-z_][\w-]*):[ \t]+(.*)$")
_QUOTED_OR_STRUCTURED = re.compile(r"""^(['"\[{]|[|>])""")


def _requote_unsafe_scalars(block: str) -> str:
    """Quote top-level single-line scalar values that contain an unquoted ': ' or trailing ':'.

    Real-world SKILL.md frontmatter is written as one logical line per key with free-text
    values (a documented, human-authored convention), not hand-crafted strict YAML. A plain
    YAML scalar cannot contain ": " because it is ambiguous with a new mapping key, so a
    free-text description such as "Two actions: (1) ..." is invalid YAML even though the
    frontmatter author's intent is unambiguous. This repairs only that narrow, deterministic
    case before handing the block to the real YAML parser; it does not implement YAML.
    """
    repaired_lines: list[str] = []
    for line in block.split("\n"):
        match = _TOP_LEVEL_SCALAR.match(line)
        if not match:
            repaired_lines.append(line)
            continue
        key, value = match.group(1), match.group(2)
        if not value or _QUOTED_OR_STRUCTURED.match(value):
            repaired_lines.append(line)
            continue
        if ": " in value or value.rstrip().endswith(":") or "#" in value:
            repaired_lines.append(f"{key}: {json.dumps(value)}")
        else:
            repaired_lines.append(line)
    return "\n".join(repaired_lines)


def parse_frontmatter_bytes(raw: bytes) -> tuple[dict[str, Any], str]:
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("missing opening YAML frontmatter delimiter")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise FrontmatterError("missing closing YAML frontmatter delimiter") from exc
    block = "\n".join(lines[1:end])
    try:
        data = yaml.safe_load(block) or {}
    except yaml.YAMLError:
        try:
            data = yaml.safe_load(_requote_unsafe_scalars(block)) or {}
        except yaml.YAMLError as exc:
            raise FrontmatterError(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        raise FrontmatterError("frontmatter name must be a non-empty string")
    return data, "\n".join(lines[end + 1 :])


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    return parse_frontmatter_bytes(path.read_bytes())
