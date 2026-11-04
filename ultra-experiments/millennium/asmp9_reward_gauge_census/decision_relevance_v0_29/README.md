# ASMP-9 decision relevance v0.29

Development-only successor to calibrated occupancy access v0.28.

The candidate theorem translates quotient reward error into a policy regret
bound only after checking that the declared reward gauge is decision-null on
the registered policy family.

Run the burned development tests:

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/decision_relevance_v0_29 `
  -q
```

No registration or claim-eligible result exists yet.
