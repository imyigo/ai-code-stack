# Fail-closed release gate

Ship is blocked when a required report is missing, unreadable, stale, or invalid; when security state is unknown; when required verification failed; or when an unresolved CRITICAL/HIGH finding exists.

A pass requires a report fingerprint matching the current diff, fresh tests, and no unresolved blocking findings. A resolved or proven false-positive finding must carry verification evidence. Explicit risk acceptance must identify the approver.

Machine output uses `status: pass|blocked|needs-review`. Any value other than `pass` blocks ship.
