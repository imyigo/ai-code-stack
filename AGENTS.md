# AI Code Stack project policy

The canonical policies are under `orchestration/`. Generated platform adapters must not override them. Vendor repositories are read-only inputs. User instructions and system safety constraints remain higher priority.

Run `scripts/verify.ps1` before proposing a release. A non-pass release gate blocks ship.

## Skill Registry vs Knowledge Registry vs Active Context vs Graphify vs Caveman

These are five distinct layers; none substitutes for another. See README.md § "Kayıt katmanları" for full definitions and worked examples. Skill Registry (`manifests/skills.json`) is the persistent, deterministic, rebuildable skill catalog. Knowledge Registry (`manifests/knowledge-registry.json`) additionally covers roles, policies, vendors, aliases, capabilities, and routing — but never conversation history, task content, or agent reasoning. Active Context is the temporary, per-task working set only. Graphify is code intelligence only, never skill memory. Caveman only shortens safe final prose, never structural or technical content.

Bir skill'in active context'ten çıkarılması, skill'in sistemden silindiği veya unutulduğu anlamına gelmez.
