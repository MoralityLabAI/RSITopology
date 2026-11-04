# ASMP-9 finite-MDP access v0.10

This development module computes exact reward-ambiguity dimensions for
entropy-regularized finite-MDP policies under transition and discount
interventions.

Run:

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/finite_mdp_access_v0_10 `
  -q
```

The prospective files are:

- `PROTOCOL_v0_10.md`;
- `protocol_v0_10.json`;
- `environment_v0_10.json`;
- `run_verification.py`; and
- `verify_result.py`.

They must be hash-sealed in a registration commit before fresh execution.
