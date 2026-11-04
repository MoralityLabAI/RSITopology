# ASMP-9 selection-channel boundary development v0.60

This unregistered CPU-only lane distinguishes:

1. recorded pre-response menu selection, where support controls which clean
   conditionals are identified;
2. the positive selection floor, which controls total finite-sample cost; and
3. unknown outcome-dependent recording, which can confound every pair of
   positive clean kernels even under complete menu assignment.

The implementation tests exact rational factorizations, the v0.56 and v0.58
handoffs, a common selected-law construction, inverse correction with known
weights, and matching inverse-selection-probability rate scaling.

Nothing here is prospectively registered or claim eligible.

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"

python -m pytest -p no:cacheprovider `
  ultra-experiments/millennium/asmp9_reward_gauge_census/selection_channel_v0_60/test_selection_channel.py `
  -q

python ultra-experiments/millennium/asmp9_reward_gauge_census/selection_channel_v0_60/verify_development.py
```

See:

- `THEOREM_DRAFT_v0_60.md`;
- `PRIOR_ART_GATE_v0_60.md`; and
- `DEVELOPMENT_RESULT_v0_60.md`.
