# ASMP-9 calibrated occupancy access v0.28

Development-only theorem branch.

The candidate boundary separates:

- homogeneous transition/occupancy interventions, which cannot break reward
  scale under an unknown rescalable response link;
- an unknown-value side feature, which remains part of the reward vector; and
- an externally calibrated numeraire, which turns each occupancy functional
  into a v0.26 threshold.

The proposed exact quotient criterion is:

```text
ker(X) = declared reward gauge.
```

Run the burned development tests with:

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28 `
  -q
```

