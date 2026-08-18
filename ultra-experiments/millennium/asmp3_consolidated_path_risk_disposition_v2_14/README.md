# ASMP-3 consolidated path-risk disposition v2.14

This package updates the consolidated Problem 3 disposition after the v2.13
correlated path-risk theorem.  It replaces the stale “fresh conditional only”
boundary, records the former noise resume trigger as cleared for the repaired
online subclass, and reduces the remaining blocker count from five to four.

Run:

```powershell
python run_consolidated_path_risk_disposition.py
python verify_consolidated_path_risk_disposition.py
python build_release_manifest.py
python -m pytest . -q
```

The safe label is: literal v0.1 iff refuted internally; repaired online
subclass characterized, black-box minimal, and robust to correlated noise via
selected-path risk; unrestricted classification and external acceptance not
established.
