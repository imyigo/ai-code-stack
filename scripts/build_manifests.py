#!/usr/bin/env python3
"""Thin entrypoint: delegates to the canonical CLI. Contains no business logic."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ai_code_stack.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["build-manifests", *sys.argv[1:]]))
