# ASMP-4 compact public connectors v0.34

This package derives v0.33 safe closing from compact connected local
controllability on the registered public information state.

The finite-subcover theorem produces explicit uniform bounds

`L=sum_j L_j`, `B_r=sum_j B_r,j`, and `B_w=sum_j B_w,j`.

It does not treat hidden plant state as free information and requires every
connector to stay in the safe core and reset registered memories.

Run:

```powershell
python run_verification.py
python verify_public_connector.py
python -m pytest -q
python -m ruff check .
```

The remaining global problem is to derive these public connector certificates
from a formally registered normally hyperbolic nonlinear plant class.

The explicit 35-package regression passes all 384 tests.
