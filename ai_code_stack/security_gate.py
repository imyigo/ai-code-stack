from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .result import Result


BLOCKING = {"CRITICAL", "HIGH"}
CLOSED = {"resolved", "closed", "fixed", "mitigated", "false_positive"}


def evaluate_release(report: dict | None, current_fingerprint: str, tests_passed: bool) -> dict:
    findings = [] if not isinstance(report, dict) else report.get("findings", [])
    if not isinstance(report, dict):
        status, reason = "blocked", "security report missing or unreadable"
    elif report.get("audited_diff_sha256") != current_fingerprint:
        status, reason = "blocked", "security report does not match current diff"
    elif not tests_passed:
        status, reason = "blocked", "required tests did not pass"
    elif not isinstance(findings, list):
        status, reason = "blocked", "security findings are invalid"
    else:
        open_blockers = []
        approved = []
        for finding in findings:
            if str(finding.get("severity", "")).upper() not in BLOCKING:
                continue
            state = str(finding.get("resolution_status", finding.get("status", ""))).lower()
            accepted = finding.get("risk_accepted") is True and bool(str(finding.get("approved_by", "")).strip())
            if accepted:
                approved.append(finding.get("id", finding.get("fingerprint", "unknown")))
            elif state not in CLOSED:
                open_blockers.append(finding)
        status = "blocked" if open_blockers else "pass"
        reason = f"{len(open_blockers)} unresolved CRITICAL/HIGH finding(s)" if open_blockers else "all fail-closed conditions passed"
        return {
            "status": status, "critical_open": sum(str(item.get("severity", "")).upper() == "CRITICAL" for item in open_blockers),
            "high_open": sum(str(item.get("severity", "")).upper() == "HIGH" for item in open_blockers),
            "report_present": True, "tests_passed": tests_passed, "approved_risks": approved,
            "timestamp": datetime.now(timezone.utc).isoformat(), "source_commit": report.get("source_commit", ""), "reason": reason,
        }
    return {
        "status": status, "critical_open": 0, "high_open": 0, "report_present": isinstance(report, dict),
        "tests_passed": tests_passed, "approved_risks": [], "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": "" if not isinstance(report, dict) else report.get("source_commit", ""), "reason": reason,
    }


def diff_fingerprint(root: Path, base: str, report_dir: Path | None = None) -> str:
    relative_report = report_dir.relative_to(root).as_posix() if report_dir and report_dir.is_relative_to(root) else None
    args = ["git", "-C", str(root), "diff", "--binary", base, "--", "."]
    if relative_report:
        args.append(f":(exclude){relative_report}/**")
    digest = hashlib.sha256(subprocess.run(args, check=True, capture_output=True).stdout)
    untracked = subprocess.run(["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"], check=True, capture_output=True, text=True).stdout.splitlines()
    for relative in sorted(untracked):
        if relative_report and (relative == relative_report or relative.startswith(f"{relative_report}/")):
            continue
        digest.update(b"\0UNTRACKED\0" + relative.encode() + b"\0")
        digest.update((root / relative).read_bytes())
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--tests-passed", action="store_true")
    parser.add_argument("--fingerprint", action="store_true")
    args = parser.parse_args(argv)
    fingerprint = diff_fingerprint(args.root.resolve(), args.base, args.report.parent if args.report else None)
    if args.fingerprint:
        print(fingerprint)
        return 0
    report = None
    if args.report and args.report.is_file():
        try:
            report = json.loads(args.report.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            report = None
    outcome = evaluate_release(report, fingerprint, args.tests_passed)
    print(json.dumps(outcome, indent=2))
    return 0 if outcome["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
