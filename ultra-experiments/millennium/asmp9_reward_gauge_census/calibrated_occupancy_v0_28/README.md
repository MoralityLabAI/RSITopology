# ASMP-9 calibrated occupancy access v0.28

Prospective theorem-and-instrument branch. No claim-eligible outcome exists
until the implementation is committed, `registration_v0_28.json` is generated
and committed, and the registered runner is executed unchanged.

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

The fresh protocol additionally requires every integer measurement matrix to
be realized by one explicit reward-independent deterministic finite MDP. Each
registered row is a query initial state with two first actions entering
disjoint feature-emission chains at one shared finite horizon.

Run the prereveal tests with:

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28 `
  -q
```

After committing the implementation, create the write-once registration:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/register_v0_28.py `
  --output ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/registration_v0_28.json
```

Commit that registration before execution. Then run:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/run_verification_v0_28.py `
  --registration ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/registration_v0_28.json `
  --output-dir ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/artifacts_v0_28

python ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/verify_result_v0_28.py `
  --registration ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/registration_v0_28.json `
  --result ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/artifacts_v0_28/result_v0_28.json `
  --receipt ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/artifacts_v0_28/run_receipt_v0_28.json `
  --output ultra-experiments/millennium/asmp9_reward_gauge_census/calibrated_occupancy_v0_28/artifacts_v0_28/independent_verification_v0_28.json
```

The finite construction can establish an access boundary in its declared
linear model. It cannot establish that a practical consequence is a stable
cardinal numeraire or resolve ASMP-9.
