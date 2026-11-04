# ASMP-9 history stabilization v0.73

This CPU-only development package separates conditional finite-state
identification from unrestricted finite-prefix inference.

```powershell
python -m pytest -q test_history_stabilization.py
python verify_development.py
```

The exhaustive verifier checks all 256 labelled two-state and 46,656 labelled
three-state binary machines, all 32,896 unordered two-state machine pairs with
repetition, and delayed-prefix witnesses for horizons 0 through 12.

The theorem is classical Myhill-Nerode/Mealy-machine theory plus an explicit
delayed-pulse boundary:

```text
declared K-state class -> finite distinguishing horizon;
no declared bound      -> no unrestricted finite-prefix certificate.
```

The package is unregistered development. It does not establish that a human,
model, or environment has finite reward memory, and it does not resolve
ASMP-9.
