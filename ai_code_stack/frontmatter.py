from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class FrontmatterError(ValueError):
    pass


def parse_frontmatter_bytes(raw: bytes) -> tuple[dict[str, Any], str]:
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("missing opening YAML frontmatter delimiter")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise FrontmatterError("missing closing YAML frontmatter delimiter") from exc
    try:
        data = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        raise FrontmatterError("frontmatter name must be a non-empty string")
    return data, "\n".join(lines[end + 1 :])


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    return parse_frontmatter_bytes(path.read_bytes())
