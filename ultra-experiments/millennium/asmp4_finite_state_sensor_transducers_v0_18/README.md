# ASMP-4 finite-state sensor transducers v0.18

This package extends the v0.17 memoryless sensor-kernel theorem to registered
finite hidden-state transducers. It proves a reachable subset-observer
criterion, exact finite language counts, the spectral read threshold, and a
complete 256-member deterministic census.

Run the central harness:

```powershell
python run_verification.py
```

Run the import-independent verifier:

```powershell
python verify_finite_state_sensor_transducers.py
```

Run focused tests:

```powershell
python -m pytest -q test_finite_state_sensor_transducers.py
```

The frozen machine-readable contract and claim are
`finite_state_sensor_contract_v0_18.json` and
`finite_state_sensor_claim_v0_18.json`.

The v0.19 successor replaces the known initial state by a registered
adversarial initial set and starts the same observer at that set. It shows that
initial uncertainty can add only transient cost, raise the asymptotic read
rate, or destroy feasibility.
