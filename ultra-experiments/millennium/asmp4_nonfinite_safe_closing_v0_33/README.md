# ASMP-4 nonfinite safe closing v0.33

This package proves that sublinear safe closing is sufficient to recover the
entire two-port capacity region directly from reset blocks, component by
component, without a finite public quotient.

It adds three pieces beyond v0.24-v0.31:

- a nonfinite periodic-completeness theorem for arbitrary public state spaces;
- an exact vector finite-horizon closing correction plus a metric safety-margin
  lift; and
- an aperiodic Thue-Morse witness with no finite exact stationary quotient.

Run:

```powershell
python run_verification.py
python verify_safe_closing.py
python -m pytest -q
python -m ruff check .
```

The result remains conditional on a registered safe-closing property and is
not a full ASMP-4 resolution.

The explicit 34-package regression passes all 374 tests.

V0.34 supplies a compact local-to-global sufficient condition for this
package's safe-closing hypothesis on the charged public information state.
