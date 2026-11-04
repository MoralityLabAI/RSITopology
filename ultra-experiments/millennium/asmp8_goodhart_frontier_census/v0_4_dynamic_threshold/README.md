# ASMP-8 v0.4 dynamic audit threshold

This additive successor replaces v0.3a's arbitrary 50% transfer gate with a
monotone first-passage estimand. Nested target-blind audit streams produce
simultaneous error-norm bounds; their running-minimum envelope makes the robust
certificate margin nondecreasing.

After prospective registration:

```powershell
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_4_dynamic_threshold/run.py
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_4_dynamic_threshold/verify_result.py
python -m pytest ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_4_dynamic_threshold -q
```

The run is CPU-only. Crossing fractions and quantiles are reported but are
never used as pass thresholds.
