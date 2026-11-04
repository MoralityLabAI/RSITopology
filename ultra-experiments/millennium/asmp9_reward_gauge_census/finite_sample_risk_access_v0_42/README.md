# Finite-sample risk access v0.42

This additive ASMP-9 development propagates simultaneous query-channel
uncertainty through every finite-horizon adaptive policy and into the directed
upper-risk-polytope containment radius.

The primary theorem target is:

```text
|true deficiency - empirical deficiency|
  <= source policy-risk radius
     + reference policy-risk radius.
```

The access gate is total:

```text
upper < tolerance  -> pass
lower > tolerance  -> fail
otherwise          -> inconclusive.
```

The first burned calibration uses the v0.41 exact deficiencies as centered
inputs and checks the analytic sample-floor transitions. A second burned
integration draws 4,800 samples per target/query, rebuilds exact rational
channels, and invokes the unchanged v0.41 compiler. Both are instrument
calibrations, not registered confirmation evidence. See
`DEVELOPMENT_NOTE_v0_42.md`.

The prospective confirmation uses 48,000 samples per target/query and derives
its seed from the exact write-once registration bytes. Its strict decisions
are arithmetically forced whenever the registered simultaneous channel event
holds; see `PROTOCOL_v0_42.md`.

Run:

```powershell
python -m pytest -q ultra-experiments/millennium/asmp9_reward_gauge_census/finite_sample_risk_access_v0_42
python ultra-experiments/millennium/asmp9_reward_gauge_census/finite_sample_risk_access_v0_42/run_burned_calibration.py
python ultra-experiments/millennium/asmp9_reward_gauge_census/finite_sample_risk_access_v0_42/run_burned_sample.py
```
