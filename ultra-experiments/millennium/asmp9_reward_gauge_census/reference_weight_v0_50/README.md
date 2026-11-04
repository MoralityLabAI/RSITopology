# ASMP-9 v0.50 reference-law robustness development

Version v0.49 characterizes common optimal evidence ordering at one frozen
reference law. Version v0.50 asks whether that compatibility survives a
declared family of reference laws.

The exact instrument returns:

1. the rational weight polytope where one ordering is jointly optimal;
2. a robust common-chain count over all objective/vertex scenarios;
3. a labelled obstruction when no robust chain exists; and
4. the exact minimum worst-case regret for small outcome sets.

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest -q -p no:cacheprovider `
  ultra-experiments/millennium/asmp9_reward_gauge_census/reference_weight_v0_50/test_reference_weight.py
```

This directory is theorem development, not a prospective empirical
registration, a novelty claim, or an ASMP-9 resolution.
