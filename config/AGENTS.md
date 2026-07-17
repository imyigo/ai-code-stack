# Global AI Code Stack Policy

Apply this policy to every Codex project. Project-specific policies may add stricter requirements but must not weaken security or release gates.

## Responsibility boundary

- **gstack is the process authority.** It decides which stage runs and when: discovery, planning, review, QA, security review, ship, and deployment.
- **ECC is the technical authority.** It provides implementation patterns, framework expertise, testing, performance, validation, and secure defaults inside the active gstack stage.
- Never run two planners for the same task.
- Never run two review skills for the same review pass.
- Never run two security skills for the same finding.

## Standard orchestration

1. gstack classifies and orchestrates the task.
2. Use Graphify only when its routing conditions are met.
3. Use the Design Layer only for design work.
4. Load the narrowest relevant ECC technical skills.
5. After implementation, run `gstack-review`.
6. For security-sensitive work, run `gstack-cso`.
7. For a concrete finding, use one matching ECC security skill.
8. Use one defensive Cybersecurity skill only when the ECC skill is insufficient for the specific domain.
9. Run `gstack-qa` and collect fresh verification evidence.
10. Run `gstack-ship` only after all required gates pass.
11. Apply Caveman only to safe final prose.

## Graphify routing

Automatically use Graphify only for:

- a large repository or broad subsystem;
- architecture analysis;
- dependency or schema analysis;
- change impact analysis;
- a multi-file refactor with non-local relationships;
- a codebase question answerable from an existing `graphify-out/graph.json`.

Skip Graphify for small file edits, clearly local bugs, one-line changes, formatting, and copy changes. If `graphify-out/` is absent, create it only when architecture, dependency, or impact analysis is genuinely required. Do not continuously rebuild; use the existing graph and update only when stale for the current question.

## Design Layer

Use UI Designer, UX Designer, Apple HIG, Design System, and Accessibility only when the task includes product or interface design. Do not load the Design Layer for backend-only, infrastructure-only, or factual tasks.

## Security fail-closed

ECC security rules act as passive guardrails during normal development.

After implementation:

1. Run `gstack-review`.
2. If the change involves authentication, authorization, payments, user or sensitive data, secrets, APIs, uploads, webhooks, permissions, or a new trust boundary, run `gstack-cso`.
3. If CSO finds a concrete issue, load one relevant ECC security skill.
4. Load at most one defensive Cybersecurity skill when deeper specialist knowledge is required.
5. Run `gstack-qa` and fresh tests after remediation.
6. Before push, `gstack-ship/security-release-gate.sh` must pass.

An absent, unreadable, or invalid required CSO report blocks release. Any unresolved `CRITICAL` or `HIGH` finding blocks release. Risk acceptance is valid only when it is explicit and names an approver. Never silently fail open.

## Cybersecurity specialization

Anthropic Cybersecurity Skills is not the primary security manager. Use a single allowlisted defensive skill only for a specific domain such as:

- OAuth or JWT;
- payment or webhook security;
- supply-chain security;
- cryptography;
- AI and agent security;
- a narrowly scoped exploit analysis within an explicitly authorized defensive review.

Never automatically invoke offensive, phishing, credential-access, persistence, evasion, malware, lateral-movement, command-and-control, or destructive skills.

## Benchmark routing

- `benchmark` routes to gstack benchmark orchestration.
- ECC's technical benchmark skill is named `ecc-benchmark` and is supporting expertise only.
- Never run both benchmark skills for the same measurement pass unless the user explicitly requests a comparative methodology review.

## Caveman boundary

Caveman is communication-only and may compress only safe final explanatory prose.

Never compress, rewrite, omit, or normalize:

- code or diffs;
- stack traces or error messages;
- terminal output or commands;
- migrations or SQL;
- JSON or YAML;
- security findings or security reports;
- test output, verification evidence, or release gate results;
- file paths, identifiers, hashes, versions, warnings, risks, or rollback steps.

When clarity or safety conflicts with brevity, disable Caveman for that content.

## Release order

`gstack-review` -> conditional `gstack-cso` -> targeted remediation -> `gstack-qa` -> fresh verification -> security release gate -> `gstack-ship` -> authorized deployment.

## Instruction priority

System and developer instructions override this policy. Then follow project instructions, the user's request, this global policy, and the selected skill instructions in that order. Use the minimum compatible skill set.
