#!/usr/bin/env bash
set -uo pipefail

# AI_CODE_STACK_SECURITY_GATE
# Exit 0: release may continue. Exit non-zero: fail closed and stop release.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT" ]]; then
  printf 'SECURITY_GATE_BLOCKED: not inside a git repository\n' >&2
  exit 20
fi
cd "$ROOT"

REPORT_DIR="${AI_CODE_SECURITY_REPORT_DIR:-.gstack/security-reports}"
FORCE_REQUIRED="${AI_CODE_SECURITY_REQUIRED:-auto}"
BASE_REF="${AI_CODE_SECURITY_BASE_REF:-}"

if [[ -z "$BASE_REF" ]]; then
  DEFAULT_BRANCH="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)"
  [[ -z "$DEFAULT_BRANCH" ]] && DEFAULT_BRANCH="main"
  if git rev-parse --verify "origin/$DEFAULT_BRANCH" >/dev/null 2>&1; then
    BASE_REF="origin/$DEFAULT_BRANCH"
  elif git rev-parse --verify HEAD^ >/dev/null 2>&1; then
    BASE_REF="HEAD^"
  fi
fi

current_fingerprint() {
  node - "$BASE_REF" "$REPORT_DIR" <<'NODE'
const crypto = require('crypto');
const fs = require('fs');
const { execFileSync } = require('child_process');
const base = process.argv[2];
const reportDir = String(process.argv[3] || '.gstack/security-reports').replace(/\\/g, '/').replace(/\/$/, '');
if (!base) process.exit(2);
const git = (...args) => execFileSync('git', args, { encoding: null, stdio: ['ignore', 'pipe', 'pipe'] });
const hash = crypto.createHash('sha256');
hash.update(git('diff', '--binary', base, '--', '.', `:(exclude)${reportDir}/**`));
const untracked = git('ls-files', '--others', '--exclude-standard')
  .toString('utf8').split(/\r?\n/).filter(Boolean)
  .filter((file) => file !== reportDir && !file.startsWith(`${reportDir}/`)).sort();
for (const file of untracked) {
  hash.update(`\0UNTRACKED\0${file}\0`);
  hash.update(fs.readFileSync(file));
}
process.stdout.write(hash.digest('hex'));
NODE
}

if [[ "${1:-}" == "--fingerprint" ]]; then
  [[ -n "$BASE_REF" ]] || { printf 'SECURITY_GATE_BLOCKED: unable to determine diff base\n' >&2; exit 21; }
  current_fingerprint
  printf '\n'
  exit 0
fi

if [[ "$FORCE_REQUIRED" == "1" || "$FORCE_REQUIRED" == "true" ]]; then
  RISKY=1
elif [[ "$FORCE_REQUIRED" == "0" || "$FORCE_REQUIRED" == "false" ]]; then
  RISKY=0
elif [[ -z "$BASE_REF" ]]; then
  printf 'SECURITY_GATE_BLOCKED: unable to determine diff base; set AI_CODE_SECURITY_BASE_REF or AI_CODE_SECURITY_REQUIRED\n' >&2
  exit 21
else
  FILES="$(git diff --name-only "$BASE_REF"...HEAD 2>/dev/null || true)"
  PATCH="$(git diff --unified=0 "$BASE_REF"...HEAD 2>/dev/null || true)"
  RISK_PATTERN='(^|[/_.-])(auth|authorization|permission|role|rbac|session|token|secret|credential|payment|billing|checkout|webhook|api|upload|user|account|security)([/_.-]|$)'
  CONTENT_PATTERN='authorization|authenticate|oauth|jwt|webhook|payment|billing|upload|api[_-]?key|password|secret|credential|permission|rate.?limit|signature|idempot'
  if printf '%s\n' "$FILES" | grep -Eiq "$RISK_PATTERN" || printf '%s\n' "$PATCH" | grep -Eiq "$CONTENT_PATTERN"; then
    RISKY=1
  else
    RISKY=0
  fi
fi

if [[ "$RISKY" -eq 0 ]]; then
  printf 'SECURITY_GATE_PASS: no security-sensitive change detected\n'
  exit 0
fi

if [[ ! -d "$REPORT_DIR" ]]; then
  printf 'SECURITY_GATE_BLOCKED: risky change detected but %s is missing; run gstack-cso\n' "$REPORT_DIR" >&2
  exit 22
fi

REPORT="$(find "$REPORT_DIR" -maxdepth 1 -type f -name '*.json' -print 2>/dev/null | sort | tail -1)"
if [[ -z "$REPORT" || ! -f "$REPORT" ]]; then
  printf 'SECURITY_GATE_BLOCKED: risky change detected but no gstack-cso JSON report exists\n' >&2
  exit 23
fi

CURRENT_FINGERPRINT="$(current_fingerprint)" || {
  printf 'SECURITY_GATE_BLOCKED: unable to fingerprint the current diff\n' >&2
  exit 27
}

node - "$REPORT" "$CURRENT_FINGERPRINT" <<'NODE'
const fs = require('fs');
const reportPath = process.argv[2];
const currentFingerprint = process.argv[3];
let report;
try {
  report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
} catch (error) {
  console.error(`SECURITY_GATE_BLOCKED: invalid CSO report ${reportPath}: ${error.message}`);
  process.exit(24);
}

if (!/^[a-f0-9]{64}$/.test(String(report.audited_diff_sha256 || '')) ||
    report.audited_diff_sha256 !== currentFingerprint) {
  console.error('SECURITY_GATE_BLOCKED: CSO report does not match the current diff; rerun gstack-cso');
  process.exit(27);
}

const closed = new Set(['resolved', 'closed', 'fixed', 'mitigated']);
const findings = Array.isArray(report.findings) ? report.findings : [];
const blockers = findings.filter((finding) => {
  const severity = String(finding.severity || '').toUpperCase();
  if (!['CRITICAL', 'HIGH'].includes(severity)) return false;
  const resolution = String(
    finding.resolution_status || finding.remediation_status || finding.state || ''
  ).toLowerCase();
  if (closed.has(resolution)) return false;
  const accepted = finding.risk_accepted === true &&
    typeof finding.approved_by === 'string' && finding.approved_by.trim().length > 0;
  return !accepted;
});

if (blockers.length > 0) {
  console.error(`SECURITY_GATE_BLOCKED: ${blockers.length} unresolved CRITICAL/HIGH finding(s) in ${reportPath}`);
  for (const finding of blockers) {
    console.error(`- ${String(finding.severity).toUpperCase()}: ${finding.title || finding.description || 'untitled finding'}`);
  }
  process.exit(25);
}

const totals = report.totals || {};
if (findings.length === 0 && (Number(totals.critical || 0) > 0 || Number(totals.high || 0) > 0)) {
  console.error('SECURITY_GATE_BLOCKED: report totals contain CRITICAL/HIGH findings but finding records are unavailable');
  process.exit(26);
}

console.log(`SECURITY_GATE_PASS: no unresolved CRITICAL/HIGH findings in ${reportPath}`);
NODE
