# Qwen0.8B stratified completion measurement — implementation plan v0.1

## Purpose

The 500,000-request endurance run repeats deterministic prompts in contiguous
groups. At its 91,000-request checkpoint it had covered only 105 of 576 unique
prompts and two of nine application families. That run remains useful as a
systems endurance test, but its request count is not an effective scientific
sample size.

This successor measures the reliability and coverage of the completion-audit
instrument itself. It does not consume outcomes and therefore cannot measure
correctness, calibration, oversight sufficiency, Goodhart pressure, or
recursive improvement.

## Frozen measurement object

The requested statistic is the returned probability and identity of the
deterministic top next token for each frozen controller-state prompt.

The schedule has 3,456 requests:

1. Epoch 0: every one of the 576 prompts, interleaved across the 18
   application-by-geometry-half strata, queried as an uncached-then-cached
   pair.
2. Epoch 1: the same census after a planned server restart, with pair order
   reversed to cached-then-uncached.
3. Epochs 2 and 3: one prospectively selected prompt from each of the 18
   strata, repeated 32 times with caching in each epoch.

The first 18 distinct prompts cover every application-by-half stratum once.
All 576 prompts are covered before stability repetitions begin.

## Gates

- `P0_plan_and_session_integrity`: every receipt binds to the frozen plan, and
  each planned epoch contains exactly one server session. An unplanned server
  restart prevents a full instrument pass.
- `C0_full_census_and_cache_order_invariance`: all 576 prompts have four
  census receipts, top-token identity agrees exactly, and the maximum
  probability range is at most `1e-6`.
- `R0_restart_and_repeat_stability`: each of the 18 frozen stability prompts
  has 64 receipts across two planned restart epochs, exact token identity, and
  probability range at most `1e-6`.
- `L0_proxy_liveness`: the unique-prompt reference arm has probability
  variance greater than `1e-8` separately in each of the 18 strata.

There is no correctness gate because the frozen manifest declares
`outcomes_consumed = false`.

## Resource and durability plan

- Windows Job Object: 4,096 MB RAM, 50% CPU, 50 MB/s I/O, zero swap.
- GPU allowance: 1,600 MB.
- Thermal pacing: pause at 84 C and resume at 82 C.
- Independent hard abort: 88 C.
- One request lane, two CPU threads.
- Every completed request is written atomically to its own hash-bearing JSON
  receipt. `progress.json` is updated after every receipt; an append-only event
  checkpoint is emitted every 18 receipts.
- Every planned server epoch has separate stdout and stderr logs.
- Post-run cleanup remains PID-owned and mandatory.

The run may begin only when the existing GPU-exclusive endurance task has
finished or stopped and cleanup has passed.

## Claim boundary

This is a target-blind measurement-reliability study. A pass establishes
coverage and invariance of this specific Qwen0.8B completion-probability
instrument under the registered cache-order and restart interventions. It
does not establish that the returned probability is correct, calibrated,
behaviorally sufficient, or predictive of Goodhart or recursive-improvement
risk.

