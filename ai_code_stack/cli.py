from __future__ import annotations

import argparse
import json
from pathlib import Path

from .installer import create_backup, install, rollback
from .manifests import build_manifests
from .adapters import build_adapters
from .verifier import verify
from .result import Result


def _print(result: Result) -> int:
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0 if result.status == "success" else 1


def cmd_install(args: argparse.Namespace) -> int:
    return _print(install(args.root.resolve(), dry_run=args.dry_run))


def cmd_verify(args: argparse.Namespace) -> int:
    result = verify(args.root.resolve())
    return _print(result)


def cmd_build_manifests(args: argparse.Namespace) -> int:
    return _print(build_manifests(args.root.resolve(), dry_run=args.dry_run))


def cmd_build_adapters(args: argparse.Namespace) -> int:
    return _print(build_adapters(args.root.resolve(), dry_run=args.dry_run))


def cmd_rollback(args: argparse.Namespace) -> int:
    return _print(rollback(args.root.resolve(), Path(args.backup)))


def cmd_backup(args: argparse.Namespace) -> int:
    backup = create_backup(args.root.resolve())
    print(json.dumps({"status": "success", "backup": str(backup)}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    root_parent = argparse.ArgumentParser(add_help=False)
    root_parent.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root (defaults to the current directory).")

    parser = argparse.ArgumentParser(prog="ai-code-stack", description="Cross-platform AI Code Stack canonical CLI.", parents=[root_parent])
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install", help="Run the canonical install pipeline.", parents=[root_parent])
    install_parser.add_argument("--dry-run", action="store_true", help="Plan only; do not write, link, or push anything.")
    install_parser.set_defaults(func=cmd_install)

    verify_parser = subparsers.add_parser("verify", help="Run the canonical fail-closed verifier.", parents=[root_parent])
    verify_parser.set_defaults(func=cmd_verify)

    manifests_parser = subparsers.add_parser("build-manifests", help="Regenerate manifests/*.json from vendor, role, and policy sources.", parents=[root_parent])
    manifests_parser.add_argument("--dry-run", action="store_true")
    manifests_parser.set_defaults(func=cmd_build_manifests)

    adapters_parser = subparsers.add_parser("build-adapters", help="Regenerate platform adapter files from common roles.", parents=[root_parent])
    adapters_parser.add_argument("--dry-run", action="store_true")
    adapters_parser.set_defaults(func=cmd_build_adapters)

    backup_parser = subparsers.add_parser("backup", help="Create a timestamped backup of manifests, adapters, and locks.", parents=[root_parent])
    backup_parser.set_defaults(func=cmd_backup)

    rollback_parser = subparsers.add_parser("rollback", help="Restore manifests/adapters/locks from a prior backup.", parents=[root_parent])
    rollback_parser.add_argument("--backup", required=True, help="Path to a backup directory created by 'ai-code-stack backup'.")
    rollback_parser.set_defaults(func=cmd_rollback)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # surfaced as a single fail-closed JSON error, never a silent success
        print(json.dumps({"status": "error", "summary": str(exc)}, indent=2, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
