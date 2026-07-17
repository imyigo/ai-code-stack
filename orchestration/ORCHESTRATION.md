# Canonical orchestration

`gstack` owns process and stage selection. `ECC` owns technical implementation expertise.

Standard conditional flow:

```text
task classification
-> gstack planning when needed
-> Graphify when routing conditions match
-> Design Layer for design work
-> ECC implementation
-> gstack-review
-> risk classification
-> gstack-cso for risky work
-> at most one targeted ECC security skill
-> at most one Cybersecurity specialist only if still needed
-> gstack-qa and fresh evidence
-> fail-closed release gate
-> gstack-ship
-> Caveman for safe final prose only
```

Never run two planners, two general reviewers, two broad security audits, two architecture systems, or two release workflows for the same pass.
