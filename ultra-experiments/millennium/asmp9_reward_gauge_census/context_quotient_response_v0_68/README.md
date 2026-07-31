# ASMP-9 context-quotient response development v0.68

## Construction status

The amended v0.68.1 construction split has now run to completion. All 528
registered records were recovered, the release reproduces from the imported
record table, and the frozen decision is:

> `local_and_global_confirmation_authorized`

See:

- [`CONSTRUCTION_RESULT_v0_68_1.md`](CONSTRUCTION_RESULT_v0_68_1.md);
- [`RESOLUTION_STATUS_AFTER_CONSTRUCTION_v0_68_1.md`](RESOLUTION_STATUS_AFTER_CONSTRUCTION_v0_68_1.md);
- [`CONSTRUCTION_RELEASE_VERIFICATION_v0_68_1.json`](CONSTRUCTION_RELEASE_VERIFICATION_v0_68_1.json);
- [`release_manifest_v0_68_1_construction.json`](release_manifest_v0_68_1_construction.json); and
- [`PRIME_POD_CLOSEOUT_ASMP9_V0681_20260729.json`](PRIME_POD_CLOSEOUT_ASMP9_V0681_20260729.json).

The untouched confirmation split has not been run. Construction authorization
is not confirmation and is not evidence of value or reward-orbit
identification.

## Local confirmation execution amendment

The additive
[`LOCAL_EXECUTION_RESOURCE_AMENDMENT_v0_68_2.md`](LOCAL_EXECUTION_RESOURCE_AMENDMENT_v0_68_2.md)
binds a Windows Job Object and RTX 3050 resource envelope for the untouched
confirmation split. It changes no model bytes, score jobs, endpoints,
thresholds, gates, or decisions. The associated wrapper has passed a
no-outcome two-phase smoke test; confirmation remains unread until an exact
registration and authorization hash are committed separately.

## Current prereveal amendment

The executable design is now governed by the additive
[`SCIENTIFIC_PROTOCOL_AMENDMENT_v0_68_1.md`](SCIENTIFIC_PROTOCOL_AMENDMENT_v0_68_1.md).
It leaves the immutable v0.68 protocol and scenario registry in place but
corrects one inferential label before any model outcome: the `2^12` sign
enumeration is a descriptive sign-orbit sensitivity statistic, not a
randomization p-value. The replacement `L0` is an exact finite-registry
practical-margin gate. Any future execution registration must bind both
protocol versions and the v0.68.1 analyzer.

Version 0.68 is the bounded successor analysis prompted by the registered
v0.67.1 construction stop.

The failed experiment mixed three different quantities into one envelope:
mechanical repeatability, display-order sensitivity, and absolute baseline
state. The v0.68 development separates them.

- `THEOREM_DRAFT_v0_68.md` proves the exact maximal measurement-nuisance
  quotient and the endpoint-admission criterion.
- `response_quotient.py` implements the exact rational quotient, orbit test,
  linear-estimand admission, interval globality test, and exhaustive audit.
- `test_response_quotient.py` includes an arm-by-order interaction that must
  survive the quotient.
- `reanalyze_burned_v067.py` applies the new coordinates to the already-seen
  construction records as explicitly post-hoc design evidence.
- `DEVELOPMENT_RESULT_v0_68.md` records the exact verification and the bounded
  burned-data liveness check.
- `scenario_manifest_v0_68.json` contains 12 fresh construction/confirmation
  family pairs, built deterministically by `prepare_fresh_scenarios.py`.
- `protocol_v0_68.json` and `SCIENTIFIC_PROTOCOL_v0_68.md` freeze the
  scientific object, scenario-level decision unit, exact `10/12` boundary,
  and separable local/global decisions.
- `run_qwen_v068.py`, `analyze_v068.py`, and
  `prepare_execution_registration.py` implement singleton resumable scoring,
  write-once analysis, and construction-gated confirmation.
- `validate_prereveal_v068.py` checks tokenizer/rendering contracts, exact job
  lists, source/model hashes, and both synthetic quotient controls without
  loading model weights.
- `prime/` contains the cgroup/systemd hard-cap wrapper and PID-scoped cleanup;
  `EXECUTION_RESOURCE_PLAN_v0_68.md` records the caps and abort semantics.
- `SUCCESSOR_PROTOCOL_DRAFT_v0_68.md` preserves the design-stage rationale.
- `PRIOR_ART_GATE_v0_68.md` places the mathematics under classical fixed
  effects and paired-comparison theory.

Run the bounded development checks:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/context_quotient_response_v0_68/test_response_quotient.py

python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/context_quotient_response_v0_68/verify_development.py `
  --output `
  ultra-experiments/millennium/asmp9_reward_gauge_census/context_quotient_response_v0_68/DEVELOPMENT_VERIFICATION_v0_68.json

python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/context_quotient_response_v0_68/validate_scientific_design.py `
  --output `
  ultra-experiments/millennium/asmp9_reward_gauge_census/context_quotient_response_v0_68/SCIENTIFIC_DESIGN_VALIDATION_v0_68.json

python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/context_quotient_response_v0_68/verify_construction_release_v0681.py
```

The initial files in this directory record development and prereveal freezing.
The construction execution is now registered and complete under v0.68.1. Only
a separately registered execution of the untouched confirmation split can
advance the empirical claim.
