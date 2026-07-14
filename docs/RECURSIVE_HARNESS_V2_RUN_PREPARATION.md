# Recursive harness v2.0.3: locked schema and run preparation

## Current state

The scientific schema is locked at v2.0.3. The operational preparation kit is
fail-closed and has not authorized or launched a scientific run.

The v1 G1 measurement component failed under its frozen rule. That result is
immutable. A later run must be a new hypothesis with a fresh disjoint holdout;
it cannot be described as adding observations to or reopening v1.

## Prepared target

- Model: `Qwen/Qwen3-1.7B` at revision
  `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.
- Execution substrate: the validated Windows-native Research_Engine Job Object
  wrapper. The obsolete WSL-only route is not used.
- Prepared caps, awaiting explicit user confirmation: 5,632 MB hard host
  working set, 9,199 MB combined commit, 3,567 MB GPU allowance, 50% CPU,
  50 MB/s sustained-I/O abort, zero swap, and a six-hour outer timeout.
- Chunking: one proposal batch, one selected edit, and one held-out evaluation
  cell at a time.
- Checkpoints: every round or 300 seconds, whichever comes first.
- Abort semantics: cap, timeout, provenance, anchor, and cleanup failures are
  first-class outcomes; none release a scientific result.

## State transitions

```text
locked schema
    -> preparation report
    -> complete new hypothesis + fresh holdout + editor/scorer/edit family
    -> seal complete run-specific universe and environment
    -> external pre-anchor submitted
    -> pre-anchor independently Bitcoin-verified
    -> one exact command authorized
    -> registered Windows Job Object wrapper launches
    -> write-once run receipt + PID-scoped cleanup audit
    -> post-anchor submission
    -> provisional release; final after Bitcoin verification
```

A schema chronology proof cannot enter this state machine as a run pre-anchor.
The authorization code requires `anchor_purpose=run_authorization`, a complete
file universe, the same runtime environment, and a nonempty independently
verified Bitcoin-block record.

## Known blockers

The prepared Qwen registration intentionally remains blocked on:

1. a new hypothesis/protocol responding to the v1 failure;
2. a fresh, disjoint, outcomes-unread holdout manifest;
3. a concrete proposal entrypoint;
4. a frozen external scorer;
5. a stable target-blind edit-family manifest;
6. the exact hard-capped command/adapter;
7. a complete source universe; and
8. explicit confirmation of the prepared resource caps.

The existing ARC prompt corpus is quarantined from the fresh holdout because
its currently observed hash differs from the value frozen in the earlier
lineage protocol. This is a preparation finding, not a scientific result.

## Commands

Readiness only; this cannot load the model:

```powershell
python scripts\prepare_recursive_run_v2.py `
  --registration protocols\proposal_recursive_run_preparation_qwen17_v2_0_3.json `
  --out-dir artifacts\proposal_recursive_run_preparation_qwen17_v2_0_3
```

After every blocker is resolved, `--seal` creates the environment lock and
run-specific pre-anchor payload. It still does not authorize source access.

The launcher accepts only an authorization receipt produced from an
independently verified pre-anchor and invokes the exact registered command. Its
registered inner wrapper owns hard-cap enforcement. Both layers perform
PID-scoped cleanup; neither may kill processes by name.

## Required logs

- `events.jsonl`: authorization, launch, checkpoint, abort, and completion.
- `summary.json`: status, exit code, resource peaks, steps, checkpoints, and
  cleanup status.
- `owned_pids.json`: only run-owned process IDs.
- `cleanup_summary.json`: before/after RAM, commit, GPU applications, stopped
  owned PIDs, lingering owned PIDs, and `cleanup_passed`.

No claim about recursive improvement is available until a new scientific
protocol passes its own registered gates.
