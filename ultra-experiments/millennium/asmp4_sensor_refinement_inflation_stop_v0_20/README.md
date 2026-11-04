# ASMP-4 sensor-refinement inflation stop v0.20

This package proves that irrelevant registered raw-label refinements can raise
read capacity without changing safety or write capacity. It supplies the
general clone theorem, coarsening inverse, exact finite margins, exhaustive
small-transducer checks, and a scoped harness stop certificate.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_sensor_refinement_inflation_stop.py
```

Run focused tests:

```powershell
python -m pytest -q test_sensor_refinement_inflation_stop.py
```

The exact registration and frozen claim are
`sensor_refinement_contract_v0_20.json` and
`sensor_refinement_stop_claim_v0_20.json`.

Read `REQUIREMENT_AUDIT_v0_20.md` for the requirement-by-requirement global
resolution audit and the precise resume conditions.

The v0.21 successor executes the exact-support quotient-first route and removes
duplicate raw colors canonically within that declared finite object. It does
not retroactively make the quotient source-mandated or control-minimal.
