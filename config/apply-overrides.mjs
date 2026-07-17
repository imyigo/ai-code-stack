import fs from 'node:fs';
import path from 'node:path';

const [skillsRoot, repoRoot] = process.argv.slice(2);
if (!skillsRoot || !repoRoot) {
  throw new Error('usage: node config/apply-overrides.mjs <skills-root> <repo-root>');
}

function read(file) {
  return fs.readFileSync(file, 'utf8');
}

function write(file, content) {
  fs.writeFileSync(file, content, 'utf8');
}

const benchmark = path.join(skillsRoot, 'benchmark', 'SKILL.md');
let benchmarkText = read(benchmark);
benchmarkText = benchmarkText.replace(/^name: benchmark$/m, 'name: ecc-benchmark');
write(benchmark, benchmarkText);

const graphify = path.join(skillsRoot, 'graphify', 'SKILL.md');
let graphifyText = read(graphify);
graphifyText = graphifyText.replace(
  /^description:.*$/m,
  'description: "Use automatically only for a large repository, architecture or dependency analysis, impact analysis, or a multi-file refactor. Skip small file and clearly local changes. If graphify-out exists, use it for matching codebase questions without rebuilding it."',
);

if (!graphifyText.includes('## Automatic routing policy')) {
  const anchor = '## What You Must Do When Invoked';
  const policy = `## Automatic routing policy

Automatically use Graphify only for a large repository, architecture or dependency analysis, impact analysis, a multi-file refactor, or a matching question answerable from an existing graph.

Do not automatically use Graphify for a small file edit, clearly local bug, one-line change, formatting, or copy change. If \`graphify-out/\` is missing, build it only when architecture, dependency, or impact analysis is required. Do not continuously rebuild; update only when stale for the current question.

`;
  if (!graphifyText.includes(anchor)) throw new Error('Graphify routing anchor missing');
  graphifyText = graphifyText.replace(anchor, policy + anchor);
}
write(graphify, graphifyText);

const ship = path.join(skillsRoot, 'gstack-ship', 'SKILL.md');
let shipText = read(ship);
if (!shipText.includes('AI_CODE_STACK_SECURITY_GATE')) {
  const anchor = '## Step 17: Push';
  const gate = `## Step 16.5: Security Release Gate

<!-- AI_CODE_STACK_SECURITY_GATE -->

Run the fail-closed security gate before any push:

\`\`\`bash
_SECURITY_GATE="$GSTACK_ROOT/gstack-ship/security-release-gate.sh"
if [ ! -f "$_SECURITY_GATE" ]; then
  echo "SECURITY_GATE_BLOCKED: gate script missing at $_SECURITY_GATE"
  exit 1
fi
bash "$_SECURITY_GATE"
_SECURITY_GATE_STATUS=$?
if [ "$_SECURITY_GATE_STATUS" -ne 0 ]; then
  echo "STATUS: BLOCKED — security release gate failed (exit $_SECURITY_GATE_STATUS)"
  exit "$_SECURITY_GATE_STATUS"
fi
\`\`\`

A missing or invalid required CSO report blocks release. Any unresolved \`CRITICAL\` or \`HIGH\` finding blocks release.

---

`;
  if (!shipText.includes(anchor)) throw new Error('gstack-ship Step 17 anchor missing');
  shipText = shipText.replace(anchor, gate + anchor);
}
write(ship, shipText);

const cso = path.join(skillsRoot, 'gstack-cso', 'SKILL.md');
let csoText = read(cso);
if (!csoText.includes('"audited_diff_sha256"')) {
  csoText = csoText.replace(
    '  "diff_mode": false,',
    '  "diff_mode": false,\n  "audited_diff_sha256": "output of: bash ../gstack-ship/security-release-gate.sh --fingerprint",',
  );
  csoText = csoText.replace(
    'Write findings to `.gstack/security-reports/{date}-{HHMMSS}.json` using this schema:',
    'Before saving, run `bash ../gstack-ship/security-release-gate.sh --fingerprint` from the gstack-cso skill directory (or the installed gate by absolute path). Store the exact output as `audited_diff_sha256`. The release gate rejects a missing or stale fingerprint.\n\nWrite findings to `.gstack/security-reports/{date}-{HHMMSS}.json` using this schema:',
  );
}
write(cso, csoText);

fs.copyFileSync(
  path.join(repoRoot, 'config', 'security-release-gate.sh'),
  path.join(skillsRoot, 'gstack-ship', 'security-release-gate.sh'),
);
