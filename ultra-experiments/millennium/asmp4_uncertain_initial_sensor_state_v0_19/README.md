# ASMP-4 uncertain initial sensor state v0.19

This package makes the finite transducer's initial-state knowledge explicit.
It proves the start-belief theorem, exact language and margin formulas,
separating transient/rate fixtures, and a complete 768-pair census.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_uncertain_initial_sensor_state.py
```

Run focused tests:

```powershell
python -m pytest -q test_uncertain_initial_sensor_state.py
```

The machine-readable registration and claim are
`uncertain_initial_sensor_contract_v0_19.json` and
`uncertain_initial_sensor_claim_v0_19.json`.

The v0.20 successor proves that irrelevant raw-symbol colors can inflate read
entropy without changing this theorem's feasibility or write requirement. It
therefore supplies a scoped stop against a plant-only forced-raw reading.
