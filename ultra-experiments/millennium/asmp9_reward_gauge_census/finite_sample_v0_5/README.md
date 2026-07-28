# ASMP-9 finite-sample sign-and-tie access v0.5

This is an unregistered theorem-development directory. It moves the ASMP-9
access program from exact population-oracle answers to independent noisy
binary responses while preserving positive-scale invariance.

The candidate result has two parts:

1. the exact v0.4 coefficient-width boundary remains a liveness boundary under
   noise; and
2. above that boundary, adaptive Farey search identifies a bounded reward ray
   with near-information-theoretic sample scaling.

Run the development tests with:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/finite_sample_v0_5
```

No claim in this directory is prospective until a later versioned protocol is
committed and registered.

`run_development.py` also solves a small nonadaptive information-design LP.
It is a diagnostic for the sample-bound gap, not a substitute for the adaptive
theorem.
