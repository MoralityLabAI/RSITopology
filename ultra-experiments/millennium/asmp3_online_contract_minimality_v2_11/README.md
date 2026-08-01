# ASMP-3 online-contract minimality v2.11

This package proves that the six-clause v2.10 online extraction contract is
minimal for the registered black-box Las Vegas observation model.  It computes
exact decision-only, ideal-probe, trace-only, trace-plus-`H`, and path-error
frontiers and records a harness-backed stopping boundary.

Run:

```powershell
python run_online_contract_minimality.py
python verify_online_contract_minimality.py
python build_release_manifest.py
python -m pytest . -q
```

The result does not rule out task-specific non-black-box proofs or choose a
normative successor interface.
