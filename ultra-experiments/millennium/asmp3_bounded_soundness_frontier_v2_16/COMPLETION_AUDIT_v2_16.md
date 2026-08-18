# ASMP-3 bounded-soundness completion audit v2.16

```text
bounded-soundness frontier rows = 17,784
finite uniform-seed balancing rows = 12,150
small coverage families exhaustively enumerated = 25,523
finite-seed optimality violations = 0
target-gap threshold rows = 3,103
producer gates = 10/10
clean-room checks = 10/10
focused tests = 11 passed
cross-package tests = 423 passed across 37 test files
standalone clean-room checkers = 33/33 successful
```

The release proves and attains

```text
C*=s+(1-s)min(1,Kq/N),
C*-s=(1-s)min(1,Kq/N)
```

for the v2.15 arbitrary-round public-coin marker interface.  It closes the
positive-soundness firewall left by v2.15 at that exact scope.

It does not establish private-coin or cross-task-family resource lower bounds,
and it does not compose ideal soundness with noisy semantic judgments without
the v2.13 selected-path-risk contract.

The standalone checker total includes the expert-review gate, which correctly
reports `0/2; complete=false` while exiting successfully.  This preserves the
external-acceptance firewall.

Reproduce from this directory:

```powershell
python run_bounded_soundness_frontier.py
python verify_bounded_soundness_frontier.py
python build_release_manifest.py
python -m pytest . -q
```
