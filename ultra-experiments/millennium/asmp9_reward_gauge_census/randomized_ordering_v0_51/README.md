# ASMP-9 v0.51 randomized evidence-ordering development

This finite instrument treats evidence ordering as the optimizer's mixed
strategy and objective/reference scenarios as the adversary's strategy.

It returns:

1. exact deterministic and randomized minimax regret;
2. exact primal and dual rational strategies;
3. complementary-slackness support receipts; and
4. the deterministic common-zero intersection.

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest -q -p no:cacheprovider `
  ultra-experiments/millennium/asmp9_reward_gauge_census/randomized_ordering_v0_51/test_randomized_ordering.py
```

The core randomized-minmax construction is directly subsumed by prior work.
This directory is a finite ASMP-9 specialization, not a novelty claim or a
resolution.
