# ASMP-8 adaptive deterministic-audit reuse v0.6

ASMP-8 v0.5 left adaptive policy generation outside its claim boundary.  This
CPU-exact successor isolates the part that can be settled without a stochastic
or learned-policy model: a movement-weighted partial-census lower bound remains
sound even when the candidate policy and next audited atom are chosen from the
revealed error transcript.

The theorem is pointwise, so it does not spend a multiple-testing budget.  A
matched plug-in selector that treats unaudited error as zero is included as an
anti-gaming control and produces false positive-gain declarations.

Run:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_6_adaptive_reuse/test_adaptive_reuse.py
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_6_adaptive_reuse/run.py
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_6_adaptive_reuse/verify_independent.py
```

This exact six-atom regression is not a learned-reward-model or open-ended
policy-search experiment.
