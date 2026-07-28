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

## Successor

The [ordinal access frontier v0.2](ordinal_frontier_v0_2/PUBLIC_SUMMARY_v0_2.md)
replaces exact real-valued loop returns with signs of trajectory-bundle
comparisons. It separately sweeps comparison count, coefficient width, and a
frozen half-unit threshold perturbation. The exact 32-cell census finds that
robust identification requires wider questions and more comparisons in every
registered nontrivial stratum. It remains a finite population-oracle result,
not a human-preference or behavioral-IRL theorem.

The [corrected sharp-width theorem v0.3.1](width_theorem_v0_3_1/PUBLIC_SUMMARY_v0_3_1.md)
then proves the dimension-uniform coefficient threshold for the strictly
positive ambiguity regime: width `2` at reward bound one and `2B-1`
thereafter. The immutable v0.3 record documents the endpoint error that led to
the corrected open interval `0<delta<1`.
