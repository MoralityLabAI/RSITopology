# ASMP-9 exact reward-gauge query census

This CPU-only theorem-seed instrument exhausts all 33,866 labelled simple
graphs on two through six vertices. Edge rewards are real 1-cochains;
potential-based shaping is the incidence coboundary `B^T phi`; exact loop-return
queries are a fundamental cycle basis.

The experiment checks the finite access threshold `beta_1 = m-n+c` and includes
an ordinal-feedback counterexample. It deliberately does not transfer an exact
linear-query result to human preference comparisons, discounted MDPs, or
behavioral IRL.

## Prereveal tests

```powershell
python -m pytest ultra-experiments/millennium/asmp9_reward_gauge_census/test_reward_gauge.py -q
```

Commit the five sealed files before running. Then:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/run.py `
  --protocol ultra-experiments/millennium/asmp9_reward_gauge_census/protocol_v0_1.json `
  --output-dir ultra-experiments/millennium/asmp9_reward_gauge_census/artifacts

python ultra-experiments/millennium/asmp9_reward_gauge_census/verify_result.py `
  --artifact-dir ultra-experiments/millennium/asmp9_reward_gauge_census/artifacts
```

The output is an exact finite census and instrument validation, not a novelty
claim for graph cohomology and not an ASMP-9 resolution.
