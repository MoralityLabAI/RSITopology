# Experiment 01: transient amplification

This experiment validates a finite-horizon control gate on a synthetic linear
response system. It keeps every eigenvalue equal to `0.9` while increasing an
upper-bidiagonal non-normal coupling. The spectral-radius gate therefore gives
the same answer throughout, while the singular-value gate can detect a
temporary declared-radius crossing.

The exact finite-horizon statement is proved in `CLAIM_PACKET.md`. Exact
rational lower/upper bounds give three-state decisions on the planted Jordan
family. The float64 SVD supplies a witness and descriptive gain estimate. The runner
also samples 4,096 directions per coupling as a red-team search, but those
directions are only a lower bound. The top singular vector is the universal
worst-case witness over the registered time set.

Run the tests:

```powershell
python -m pytest tests/test_transient_amplification.py -q
```

Run the sealed synthetic pilot:

```powershell
python ultra-experiments/01_transient_amplification/run.py `
  --protocol ultra-experiments/protocols/transient_amplification_v0_1.json `
  --amendment ultra-experiments/protocols/transient_amplification_v0_1_1_amendment.json `
  --output ultra-experiments/01_transient_amplification/artifacts
```

The experiment can establish only that the instrument distinguishes a planted
matched-spectrum separation. A real application requires an independently
estimated response operator, a registered physical metric, and a bound on the
linearization remainder.
