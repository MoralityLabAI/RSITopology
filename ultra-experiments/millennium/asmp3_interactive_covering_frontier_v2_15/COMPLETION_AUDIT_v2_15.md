# ASMP-3 interactive covering completion audit v2.15

```text
registered interactive frontier rows = 13,413
adaptive trees exhaustively enumerated = 97,062
adaptive marker runs = 464,010
zero-path compression violations = 0
small compressed-codebook frontiers = 49
cyclic public-coin attainment rows = 738
round-schedule rows = 78
power-of-two bit/query rows = 3,310
producer gates = 10/10
clean-room checks = 10/10
focused tests = 11 passed
cross-package tests = 412 passed across 36 test files
standalone clean-room checkers = 32/32 successful
```

The release proves the exact arbitrary-round public-coin value
`min(1,Kq/N)` for the zero-or-one-marker family under pointwise perfect
zero-world soundness.  It closes the specific v2.2 firewall for interaction,
public randomness, bounded completeness, and adaptive semantic queries.

It does not close the full ASMP-3 resource requirement: the theorem remains a
registered unstructured family result, and it does not cover positive
soundness error or all task-specific protocols.

The standalone checker total includes the expert-review gate, which correctly
reports `0/2; complete=false` while exiting successfully.  That is an explicit
external-status receipt, not an internal theorem failure.

Reproduce from this directory:

```powershell
python run_interactive_covering_frontier.py
python verify_interactive_covering_frontier.py
python build_release_manifest.py
python -m pytest . -q
```
