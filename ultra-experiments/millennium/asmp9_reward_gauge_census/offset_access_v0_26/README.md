# ASMP-9 v0.26: offset-calibrated unknown-link access

Status: prereveal development until `registration_v0_26.json` is created from
a committed implementation.

This theorem seed follows the v0.8 unknown-link obstruction with one declared
positive access channel. A known scalar offset turns every strictly increasing
symmetric link into the same threshold oracle at probability one half.

The contribution is the access and gauge ledger, not new bisection or
preference-elicitation mathematics.

## Prereveal checks

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26 `
  -q
```

After committing the prereveal implementation:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/register_v0_26.py `
  --output ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/registration_v0_26.json
```

Commit the registration before execution. Then:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/run_verification_v0_26.py `
  --registration ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/registration_v0_26.json `
  --output-dir ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/artifacts_v0_26

python ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/verify_result_v0_26.py `
  --registration ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/registration_v0_26.json `
  --result ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/artifacts_v0_26/result_v0_26.json `
  --receipt ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/artifacts_v0_26/run_receipt_v0_26.json `
  --output ultra-experiments/millennium/asmp9_reward_gauge_census/offset_access_v0_26/artifacts_v0_26/independent_verification_v0_26.json
```

No GPU is used. No random scientific outcome is generated.
