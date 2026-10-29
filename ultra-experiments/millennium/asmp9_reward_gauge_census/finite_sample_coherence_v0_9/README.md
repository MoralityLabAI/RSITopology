# ASMP-9 finite-sample coherence v0.9

This development branch turns the exact population-law coherence test from
v0.7 into a simultaneous finite-sample certificate.

Run the development tests:

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/finite_sample_coherence_v0_9/test_finite_sample_coherence.py `
  -q
```

The admissible output levels are:

- `certified_coherent_within_tolerance`;
- `certified_incoherent`;
- `inconclusive`;
- `unavailable_no_cycles`;
- `unavailable_probability_floor`; and
- `unavailable_no_edges`.

No finite sample is allowed to certify exact zero circulation.

The prospective confirmatory files are:

- `PROTOCOL_v0_9.md`;
- `protocol_v0_9.json`;
- `environment_v0_9.json`;
- `run_verification.py`; and
- `verify_result.py`.

They must be hash-sealed in a registration commit before the fresh seeds are
executed.
