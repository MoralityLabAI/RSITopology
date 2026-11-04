# ASMP-9 uniform above-floor mechanical successor v0.22.1

This successor preserves the v0.22 weighted-Tutte theorem and repairs one
case-sensitive attribution-gate implementation error.  It uses only new graph
cells and preserves the failed v0.22 record.

Development checks:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/uniform_above_floor_v0_22_1
```

No outcomes may be read before `registration_v0_22_1.json` is committed.
