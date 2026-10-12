# ASMP-3 perfect-recall sequence-form bridge v1.3

This package compiles finite rational perfect-recall extensive games into
realization constraints and a chance-weighted sequence payoff matrix.

It certifies hidden versus revealed matching pennies, a nested length-two
realization game, and a signaling family with `k^k` pure strategies per role but
only `1+k²` sequences.

Run:

```powershell
python run_sequence_form_bridge.py
python verify_sequence_form_bridge.py
python build_release_manifest.py
python -m pytest . -q
```

The result is polynomial in the explicit history tree and requires perfect
recall, two-player zero-sum payoffs, and a frozen interface.
