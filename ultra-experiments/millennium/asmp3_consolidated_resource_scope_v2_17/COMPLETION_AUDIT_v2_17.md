# ASMP-3 consolidated resource-scope completion audit v2.17

```text
decisive evidence packages = 15
sealed manifest members = 344
sealed member bytes = 59,915,052
requirement rows = 18
direct requirement evidence checks = 18/18
resource progress events = 1
marker interface firewalls cleared = 5
remaining blockers = 4
external expert teams = 0/2
producer gates = 10/10
clean-room checks = 10/10
focused tests = 11 passed
cross-package tests = 434 passed across 38 test files
standalone clean-room checkers = 34/34 successful
```

V2.17 records v2.15-v2.16 as a strict strengthening of requirement R2 without
promoting a family theorem into a cross-task claim.  The clean-room checker
rehashes all fifteen decisive packages and independently reconstructs the
interactive and bounded-soundness formulas and counts.

The internal resource-scope disposition and stop certificate are complete.
The normative class, unrestricted classification, and external acceptance are
not.

The standalone checker total includes the expert-review gate, which correctly
reports `0/2; complete=false` while exiting successfully.  That output verifies
the external-acceptance firewall rather than weakening an internal gate.

Reproduce from this directory:

```powershell
python run_consolidated_resource_scope.py
python verify_consolidated_resource_scope.py
python build_release_manifest.py
python -m pytest . -q
```
