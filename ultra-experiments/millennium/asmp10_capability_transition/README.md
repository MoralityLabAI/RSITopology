# ASMP-10 capability-transition pilot

This directory begins with a hard-capped pilot, not a claim-eligible experiment.
It asks whether a tiny modular-addition transformer produces enough variation in
held-out transition times to support a later preregistered comparison between
loss-only and spectral/geometry predictors.

The trainer is seed-chunked, resumable, checkpointed, and explicitly cleans CUDA
objects. It must run through the validated Windows Job Object wrapper described
in `TRAINER_PLAN.md`.

## Unit tests

```powershell
python -m pytest ultra-experiments/millennium/asmp10_capability_transition/test_train_pilot.py -q
```

## Pilot outputs

Each run writes evaluation histories, one resumable checkpoint, early geometry
features, and a completion record. The root writes `events.jsonl` and
`summary.json`. Wrapper outputs separately record cap enforcement, resource
samples, owned PIDs, and post-run cleanup.

Do not cite pilot transition behavior as held-out prediction evidence. The
pilot's only job is to choose a viable registered horizon and model family.

## Pilot outcome

The completed 4,000-step pilot did not produce a live transition. The extension
attempts are resource diagnostics: v0.2 exposed a WDDM GPU-accounting gap and
v0.3 safely aborted under the fail-closed aggregate GPU guard. See
`PILOT_REPORT_v0_1.md`. The positive held-out predictor experiment remains
unregistered; the active successor is the CPU-exact prefix-obstruction branch.

## Liveness pilot v0.4

The later v0.4 construction pilot completed a prospective train-fraction ×
weight-decay factorial and found three delayed first-passage transitions. See
`LIVENESS_PILOT_RESULT_v0_4.md`. The result opens only the drafting branch:
`PREDICTOR_PROTOCOL_DRAFT_v0_5.md` is not registered and not authorized to run.
