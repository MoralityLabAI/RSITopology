# ASMP-3 simultaneous hidden-action matrix bridge v1.2

This package closes the finite normal-form hidden-action lane with exact
rational primal/dual mixed-strategy certificates.

It certifies matching pennies, rock-paper-scissors, a nonuniform oversight
matrix, `1/k` hidden-attack decay, and duplicated-action invariance.

Run:

```powershell
python run_matrix_game_bridge.py
python verify_matrix_game_bridge.py
python build_release_manifest.py
python -m pytest . -q
```

The payoff matrix must be explicitly supplied.  Compact imperfect-information
protocols still require the sequence-form successor.
