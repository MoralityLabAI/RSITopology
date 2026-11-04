# ASMP-4 robust public reset atlas v0.35

This package proves that a compact finite fixed-reset atlas with registered
Lipschitz tubes and strict margins supplies constant-cost two-port safe
closing.  It also constructs an exact nonlinear uncertain fixture with 33
charged sensor cells and 33 charged actuator words.

Run the central harness:

```powershell
python run_verification.py
```

Run the independent implementation:

```powershell
python verify_robust_public_atlas.py
```

Run the ten focused tests and lint:

```powershell
python -m pytest -q test_robust_public_atlas.py
python -m ruff check .
```

The fixed-reset atlas directly instantiates v0.33 safe closing.  It does not
silently claim v0.34's stronger all-pairs local premise.  The result is a
quantitative sufficient bridge, not a full resolution of the canonical
ASMP-4 class.  The complete 36-package chain passes all 394 tests.

V0.36 performs the successor single-root stopping audit; no additional local
fixture is authorized without one of its four reopening events.
