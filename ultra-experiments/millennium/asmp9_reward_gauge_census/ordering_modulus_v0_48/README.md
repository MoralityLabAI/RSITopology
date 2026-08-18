# ASMP-9 ordering modulus v0.48

Development successor to the sharp all-zero atom modulus in v0.47.

The module treats the evidence ordering as part of the access certificate.
For small finite count experiments it computes the exact Buehler bound for
every prefix subset and exhausts every outcome ordering under a frozen
reference-law objective.

Run the dedicated tests:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/ordering_modulus_v0_48/test_ordering_modulus.py
```

No confirmation is registered or run in this directory.

The burned ordering search is recorded in
`DEVELOPMENT_RESULT_v0_48.md`. It found four exact cells with disjoint
decision-optimal ordering sets and positive cross-regrets in both directions.
