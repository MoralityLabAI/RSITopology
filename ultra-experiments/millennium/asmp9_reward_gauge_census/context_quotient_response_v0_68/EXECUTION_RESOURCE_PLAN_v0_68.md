# ASMP-9 v0.68 execution resource and cleanup plan

Status: **runner implemented; construction execution not registered**.

Current scientific authority is the additive v0.68.1 amendment. Resource
limits and the score-job universe are unchanged; target registration must hash
the amended analyzer, validator, and both protocol files.

## Workload

Each split contains 528 next-token score records:

```text
12 scenarios
x 22 semantic inputs
x 2 exact singleton repeats.
```

There is no sampled generation and no training. Every semantic input is scored
as `batch_size = 1`; changing batching would invalidate the numerical premise
being tested.

The intended target is a dedicated inexpensive CUDA pod with at least 8 GB
VRAM. The model is Qwen3.5-0.8B-Instruct in float16. Based on the completed
v0.67 batch-four run, singleton execution should remain below the frozen
4,096 MB GPU-allocation allowance but take longer. The one-hour timeout is
binding; timeout is an abort, not permission to relax the cap.

## Hard caps

```text
private/cgroup RAM:       8,192 MB
minimum free host RAM:   12,288 MB
CPU quota:                   50%
I/O read/write rate:       50 MB/s
GPU allocation delta:    4,096 MB
GPU temperature:            88 C
wall timeout:             3,600 s
swap:                           0
checkpoint cadence:       every record
```

The Prime wrapper uses `systemd-run` with `MemoryMax`, `MemorySwapMax=0`,
`CPUQuota`, block-device I/O bandwidth limits, and `RuntimeMaxSec`. It refuses
an unclean GPU start or insufficient free RAM and independently polls
temperature and VRAM.

## Resume and abort semantics

- Each record and exact rendered input are atomically write-once.
- Resume accepts only the 528 registered IDs and their registered fields.
- Every record is validated before reuse.
- Hash mismatch, changed answer-token boundary, nonfinite score, prompt-cap
  breach, cap breach, timeout, or missing record aborts the phase.
- Aborts write timestamped receipts and are valid results of resource
  enforcement.
- Construction analysis writes a total authorization decision. Confirmation
  cannot be registered without a hash-bound positive local authorization.

## Cleanup

The runner releases model/tokenizer references, runs garbage collection,
synchronizes CUDA, empties the allocator cache, and calls IPC collection in a
`finally` block. The wrapper kills only its unique run-owned systemd units,
then records:

- lingering GPU compute applications;
- runner/analysis unit state;
- GPU temperature, memory, and utilization;
- available RAM; and
- whether cleanup passed.

No local GPU and no Prime pod are authorized by this plan alone. Registration
must be created on the final execution environment after the source commit and
prereveal tokenizer validation.

## Availability hold

The 2026-07-29 Prime check found zero active pods and two available one-GPU
A100-80GB offers, priced at USD 1.23/hour and USD 1.79/hour. Both exceed the
delegated USD 0.70/GPU-hour ceiling. No pod was created and no substitute GPU
was selected. `PRIME_AVAILABILITY_HOLD_v0_68.json` records the exact offers and
the no-launch decision.
