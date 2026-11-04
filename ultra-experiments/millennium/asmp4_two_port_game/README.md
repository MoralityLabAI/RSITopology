# ASMP-4 exact two-port finite safety game

This pilot measures an exact read/write feasibility region in a frozen finite
rational architecture. One time-indexed memoryless controller must confine all
nine registered initial states against every disturbance path. Controller
selection cannot depend on the initial cell.

The result is exact only for the registered point grid, sensor partitions,
action dictionaries, and policy grammar. It is not a continuous-plant capacity
theorem.

## Pre-outcome tests

```powershell
python -m pytest test_two_port_game.py -q
```

## Registered run

Run only after all inputs are committed:

```powershell
python run.py --protocol protocol_v0_1.json --output-dir artifacts
python verify_result.py --result artifacts/result_v0_1.json `
  --receipt artifacts/receipt_v0_1.json `
  --output artifacts/verification_v0_1.json
```

Any invalid or failed gate stops the sequential ASMP queue.
