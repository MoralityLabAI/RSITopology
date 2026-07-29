# ASMP-9 context-quotient response development v0.68

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
```

This is development, not a preregistration. It authorizes no GPU run and does
not reopen the v0.67 confirmation split. The scientific design is frozen, but
execution remains unregistered until the runner, environment, exact job list,
and prereveal validator are bound.
