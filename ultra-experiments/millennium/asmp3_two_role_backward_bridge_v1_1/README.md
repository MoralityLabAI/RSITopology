# ASMP-3 two-role backward bridge v1.1

This package extends the fixed-interface chain to finite acyclic, turn-based,
perfect-information zero-sum protocol games.

It provides exact rational backward induction, deterministic saddle strategies,
reciprocal deviation checks, an exponential challenger-strategy family, an
alternating game, and a matching-pennies information-boundary audit.

Run:

```powershell
python run_two_role_backward_bridge.py
python verify_two_role_backward_bridge.py
python build_release_manifest.py
python -m pytest . -q
```

Hidden or simultaneous actions require a separate perfect-recall sequence-form
extension; backward induction is not claimed for them.
