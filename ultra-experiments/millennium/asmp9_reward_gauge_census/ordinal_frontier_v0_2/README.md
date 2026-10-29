# ASMP-9 ordinal reward-ray access frontier v0.2

This successor to the exact loop-return census replaces real-valued access with
pairwise comparison signs. It enumerates a finite reward-ray registry modulo
positive scale, sweeps the coefficient width of admissible trajectory-bundle
comparisons, and measures robustness to a frozen adversarial response-threshold
perturbation.

The result distinguishes two failure modes:

1. too few queries from a sufficient grammar; and
2. a query grammar that cannot separate the reward rays at any query count.

## Prereveal workflow

```powershell
python -m pytest ultra-experiments/millennium/asmp9_reward_gauge_census/ordinal_frontier_v0_2/test_ordinal_frontier.py -q
```

After the implementation and registration commits:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/ordinal_frontier_v0_2/run.py `
  --registration ultra-experiments/millennium/asmp9_reward_gauge_census/ordinal_frontier_v0_2/registration_v0_2.json `
  --output-dir ultra-experiments/millennium/asmp9_reward_gauge_census/ordinal_frontier_v0_2/artifacts_v0_2

python ultra-experiments/millennium/asmp9_reward_gauge_census/ordinal_frontier_v0_2/verify_result.py `
  --registration ultra-experiments/millennium/asmp9_reward_gauge_census/ordinal_frontier_v0_2/registration_v0_2.json `
  --artifact-dir ultra-experiments/millennium/asmp9_reward_gauge_census/ordinal_frontier_v0_2/artifacts_v0_2
```

The experiment is CPU-only and bounded. See `PROTOCOL_v0_2.md` for the exact
claim boundary.

