# ASMP-3 consolidated resource scope v2.17

This package incorporates the v2.15 arbitrary-round interactive covering
theorem and v2.16 bounded-soundness theorem into the consolidated ASMP-3
requirement ledger.

It records the unique-marker resource frontier as exact through public-coin
interaction, adaptive queries, and bounded soundness, while keeping the
cross-task resource classification open until a formal task/protocol class is
frozen.

Run:

```powershell
python run_consolidated_resource_scope.py
python verify_consolidated_resource_scope.py
python build_release_manifest.py
python -m pytest . -q
```
