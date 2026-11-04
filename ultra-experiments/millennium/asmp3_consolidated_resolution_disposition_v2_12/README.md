# ASMP-3 consolidated resolution disposition v2.12

This package updates the stale v2.6 disposition with the v2.7-v2.11 normal-form
and minimality results.  It separates the exact literal refutation, the repaired
online subclass, unrestricted classification, normative authority, and external
acceptance.

Run:

```powershell
python run_consolidated_resolution_disposition.py
python verify_consolidated_resolution_disposition.py
python build_release_manifest.py
python -m pytest . -q
```

The safe label is: literal v0.1 iff refuted internally; repaired online subclass
characterized and black-box minimal; unrestricted classification and external
acceptance not established.
