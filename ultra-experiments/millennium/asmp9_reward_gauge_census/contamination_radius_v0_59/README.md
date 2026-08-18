# ASMP-9 adversarial-contamination radius development v0.59

This unregistered lane advances the misspecification obligation left open by
the clean iid v0.58 theorem.

It develops three connected statements:

1. two finite categorical laws have intersecting equal-radius Huber
   contamination neighborhoods exactly when
   `TV <= epsilon/(1-epsilon)`;
2. the minimum observed-menu TV between different value-object tiers is the
   exact population contamination threshold for a compact clean class; and
3. in the bounded-context class, contamination subtracts directly from the
   clean coordinate tolerance before any finite-sample error is spent.

The exact overlap theorem is classical robust-testing mathematics specialized
to the ASMP-9 object. Nothing here is registered or claim eligible.

Development commands:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"

python -m pytest -p no:cacheprovider `
  ultra-experiments/millennium/asmp9_reward_gauge_census/contamination_radius_v0_59/test_contamination_radius.py `
  -q

python ultra-experiments/millennium/asmp9_reward_gauge_census/contamination_radius_v0_59/verify_development.py
```

See:

- `THEOREM_DRAFT_v0_59.md` for the statement and proof;
- `PRIOR_ART_GATE_v0_59.md` for the subsumption boundary; and
- `DEVELOPMENT_RESULT_v0_59.md` for the checked development verdict.
