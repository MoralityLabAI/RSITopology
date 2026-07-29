# ASMP-9 physical acquisition v0.34

This directory turns the exact v0.33 coupling quotient into a prospective
model-facing calibration experiment. Version `v0.34` was sealed and stopped
at its engineering smoke because Qwen's `<think>` control token appeared
outside the intended answer alphabet. Version `v0.34.1` preserves that abort
and uses the model's registered no-thinking chat prefix.

## Scientific sequence

1. `pilot_design.py` defines the 3x4 common-ruler rectangle, six compound
   lotteries, and the preferred 18 cell-by-policy probes.
2. `prepare_burned_pilot.py` verifies the v0.33 preferred basis, generates the
   disjoint pilot/holdout manifest, and seals local model, server, source,
   runner, analyzer, wrapper, cleanup, and environment hashes.
3. `run_burned_pilot.py` can read only `burned_pilot` rows and refuses to run
   without the registered hard-cap wrapper.
4. `analyze_burned_pilot.py` reports common-ruler crossings, mixture-affinity
   residuals, option-order and cold-start instability, and norm-specific
   policy-probe secant errors.

The untouched `future_holdout` families may be used only by a later,
versioned confirmation registration.

## Prepare after the implementation commit

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/physical_acquisition_v0_34/prepare_burned_pilot.py
```

The preparer refuses unrelated dirty worktree state and writes:

```text
burned_pilot_prompt_manifest_v0_34_1.json
burned_pilot_registration_v0_34_1.json
```

Commit those files before any model response is read.

## Guarded smoke

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/run_asmp9_v034_jobobject.ps1 `
  -RegistrationPath ultra-experiments/millennium/asmp9_reward_gauge_census/physical_acquisition_v0_34/burned_pilot_registration_v0_34_1.json `
  -ExecutionClass smoke `
  -OutputDir D:\Research_Engine\runs\asmp9_physical_acquisition_smoke_v0_34 `
  -SmokeRowsPerType 2
```

A smoke is engineering evidence only. It cannot be promoted into the burned
pilot.

## Guarded burned pilot

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/run_asmp9_v034_jobobject.ps1 `
  -RegistrationPath ultra-experiments/millennium/asmp9_reward_gauge_census/physical_acquisition_v0_34/burned_pilot_registration_v0_34_1.json `
  -ExecutionClass burned_pilot
```

## Tests

```powershell
python -m pytest tests/test_asmp9_physical_acquisition_v034.py -q
python -m pytest ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33 -q
```

## Claim boundary

The pilot calibrates one explicit prompt-level access grammar on one Q4 small
model. It is not confirmation, does not establish expected utility, does not
identify a maximal shaping gauge, does not authorize edits or policy changes,
and does not resolve ASMP-9.
