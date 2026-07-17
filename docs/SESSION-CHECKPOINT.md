# Session checkpoint — master prompt application (in progress)

This session is applying `Claude_Code_AI_Code_Stack_Master_Prompt_v2.txt` to this
repository. It was paused by the user before completion (time constraint, not a
blocker). This file exists so the next session can resume without re-deriving
context. Delete this file once the task reaches Definition of Done and is pushed.

## What is done and verified in this session

1. **Recovery audit** — repo was clean (`main` in sync with `origin/main` at
   `ad634e5`) with no half-applied staged/unstaged state. `.gate-test/` and
   `work/gate-*` were confirmed-empty leftover test dirs from a prior
   `security-release-gate.sh` run and were removed (untracked, no data loss).
2. **Real bug found and fixed**: `ai_code_stack/frontmatter.py` raised on
   `vendors/ecc/skills/loop-design-check/SKILL.md` because its `description:`
   contains an unquoted `": "` inside a plain YAML scalar (valid frontmatter
   convention, invalid strict YAML). Fixed with a deterministic pre-parse repair
   pass (`_requote_unsafe_scalars`) that auto-quotes top-level single-line scalar
   values containing `": "` before handing the block to PyYAML — still a real
   YAML parser, not a regex replacement engine. All 455 vendor skills now parse;
   0 duplicates; matches `versions.lock.expected_selected_skills`.
3. **Real bug found and fixed**: `pyproject.toml` declared
   `ai-code-stack = "ai_code_stack.cli:main"` but `ai_code_stack/cli.py` did not
   exist. Added it (subcommands: `install`, `verify`, `build-manifests`,
   `build-adapters`, `backup`, `rollback`), each a thin wrapper around the
   existing `installer.py` / `verifier.py` / `manifests.py` / `adapters.py`.
4. **Real bug found and fixed**: `ai_code_stack/verifier.py` hardcoded
   `len(adapter_outputs(root)) == 76`; actual generator output is 75
   (`18 roles * 4 + 3`). Changed to a derived expectation instead of a magic number.
5. **Canonical Python CLI wired up end to end** (section 19 of the master
   prompt — no PowerShell-only core logic):
   - Added `scripts/install.py`, `verify.py`, `build_manifests.py`,
     `build_adapters.py`, `rollback.py` — thin `argparse` shims that call
     `ai_code_stack.cli.main(...)`.
   - Rewrote `install.sh`, `verify.sh`, `scripts/install.ps1`,
     `scripts/verify.ps1`, `scripts/build-adapters.ps1`, `scripts/rollback.ps1`
     as thin wrappers that just invoke the Python entrypoints. No business logic
     remains in PowerShell.
   - **Removed** `scripts/link-skills.ps1`, `scripts/update.ps1`,
     `scripts/export-report.ps1`, `scripts/Common.ps1` — these reimplemented
     install/link/rollback business logic in PowerShell (forbidden by section 19),
     referenced a stale schema (`ai-code-stack.2` vs current `.3`) and a
     hardcoded path (`C:\WyvOS\skills`) that doesn't exist anywhere else in the
     repo, and a backup format (`backup-manifest.json`) that doesn't match the
     real installer's `journal.json` backup format. **Backed up, not lost**, at
     `backups/20260717T143730Z-legacy-powershell-scripts/` before removal.
   - Fixed an argparse ordering bug (`--root` only worked before the subcommand;
     now works either side via a shared `parents=[root_parent]` parser).
6. **Manifests**: extended `ai_code_stack/manifests.py` to also generate the 4
   manifests the spec asks for that were missing —
   `manifests/knowledge-registry.json`, `manifests/skill-routing.json`,
   `manifests/token-costs.json` (explicitly marked `"estimate": true`),
   `manifests/cache-state.json`. All 11 manifests now build deterministically
   (checksums.json now also excludes `backups/`, `work/`, `.gate-test/` from its
   scan so point-in-time backups don't get treated as build inputs).
7. **Policies**: added the 8 missing files under `policies/` —
   `execution-budget.yaml`, `context-efficiency.yaml`, `skill-loading.yaml`,
   `knowledge-registry.yaml`, `graphify-routing.yaml`, `caveman.yaml`,
   `cache.yaml`, `security.yaml` — alongside the pre-existing `routing.yaml` and
   `runtime.yaml`. All 10 parse as valid YAML.
8. **Tests**: `tests/` created with `conftest.py` (session-scoped `repo_root`
   fixture) and 5 files — `test_frontmatter.py` (CRLF/LF/BOM/multiline/quotes/
   arrays/key-order/the real vendor-file repair case),
   `test_registry.py` (deterministic rebuild, no duplicates, alias routing,
   required metadata fields), `test_security_gate.py` (fail-closed truth table:
   missing report, fingerprint mismatch, failing tests, open CRITICAL/HIGH,
   resolved finding, explicit risk acceptance with/without approver, clean
   report, LOW/MEDIUM never block), `test_execution_budget.py` (runtime.yaml
   limits, execution-budget.yaml task-class ceilings, nested-subagent/
   cross-platform-delegation disabled), `test_filesystem.py` (link strategy per
   OS, path-escape rejection, generated-marker overwrite protection, checksum
   determinism). **38/38 pass.**
9. **Verifier**: `python -m ai_code_stack.cli verify` → **25/25 checks pass**
   (vendor submodules pinned+clean, 455 unique skills, benchmark alias routing,
   18 common roles, cross-platform delegation disabled, agent limits enforced,
   Graphify conditional routing, Caveman boundary, 75 adapter outputs, all 11
   manifests present and schema-versioned, checksums match, security gate
   fail-closed truth table holds).

## What is NOT done yet — pick up here

- **Task #7 (in progress)**: `tests/` coverage is solid but does not yet include
  the spec's remaining categories: dry-run-no-write assertions for
  `installer.install(..., dry_run=True)`, adapter capability-fallback-not-
  fabricated assertions (antigravity/cursor `native_subagents` must be `None`/
  `False` unless verified, never `True` by assumption), and an explicit
  Windows-junction-plan vs macOS/Linux-symlink-plan test using
  `link_strategy()`.
- **Task #9 (pending)**: has not yet run `config/security-release-gate.sh`
  itself (only the Python `security_gate.evaluate_release` unit truth table),
  and has not yet done a repo-wide secret scan pass over the *new* files added
  this session (the ones added in the prior session were already scanned and
  were clean).
- **Task #10 (pending)**: README/AGENTS.md/CLAUDE.md have not yet been updated
  to explicitly state the Skill Registry vs Knowledge Registry vs Active Context
  vs Graphify vs Caveman distinctions and the exact required sentence: *"Bir
  skill'in active context'ten çıkarılması, skill'in sistemden silindiği veya
  unutulduğu anlamına gelmez."* Nor the 5 worked examples from spec section 27.
- **Task #11 (pending)**: nothing has been committed or pushed yet this
  session. The working tree currently has real, verified, uncommitted changes
  (see `git status`). **Do not push until #9 and #10 are done** per the master
  prompt's own push gate — this checkpoint commit is an explicit, narrow
  exception the user asked for to save work-in-progress; say so plainly if
  asked why history shows a WIP-labeled commit.

## How to resume

1. `git log --oneline -3` and `git status` to confirm you're starting from this
   checkpoint commit.
2. Continue task #7 (dry-run + fallback + link-strategy tests), then #9
   (`bash config/security-release-gate.sh` + secret scan on the diff since
   `ad634e5`), then #10 (docs), then re-run `python -m ai_code_stack.cli verify`
   and `python -m pytest tests/ -q` one more time before committing for real and
   pushing to `https://github.com/imyigo/ai-code-stack.git` `main`.
3. Delete this file as part of that final commit.
