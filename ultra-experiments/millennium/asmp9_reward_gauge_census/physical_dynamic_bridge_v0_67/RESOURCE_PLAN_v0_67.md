# ASMP-9 v0.67 resource and cleanup plan

## Workload

Each phase contains 240 prompts and no generated tokens. With batch size eight,
the model executes thirty forward batches. Every prompt is capped at 768
tokens, and every prompt record is a write-once resumable work unit.

The registered model is Qwen3.5-0.8B-Instruct loaded in float16. The preferred
execution target is a dedicated inexpensive CUDA pod with at least 8 GB VRAM.
The registered GPU allowance remains 4,096 MB; exceeding it is an abort, not
permission to enlarge the cap after seeing an outcome.

## Hard caps

```text
private/job RAM:       8,192 MB
host RAM reserve:      4,096 MB
minimum free RAM:     12,288 MB
CPU hard cap:             50%
I/O rate cap:          50 MB/s
GPU allocation cap:    4,096 MB
wall timeout:          3,600 s
swap:                       0
checkpoint interval:      30 s
```

The Windows authorization uses the existing Job Object wrapper, verifies the
wrapper, registration, and cleanup hashes, and refuses a low-memory preflight.
A Linux pod must provide an equivalently logged cgroup/container limit before
its environment-specific registration is sealed.

## Abort and resume

- A record is complete only after its individual JSON artifact is atomically
  written.
- A restart accepts only registered record IDs and skips byte-identical
  completed work.
- Failed attempts write separate abort receipts and cannot overwrite a later
  completion receipt.
- Any CUDA error, hash mismatch, prompt cap violation, answer-token boundary
  mismatch, resource-cap breach, or missing work unit aborts the phase.
- Confirmation cannot be prepared from an incomplete construction phase.

## Cleanup

The runner deletes model references, invokes Python garbage collection,
synchronizes CUDA, empties the allocator cache, and invokes IPC collection in
`finally`. The outer wrapper terminates only owned processes and runs the
hash-bound HRM cleanup script. Cleanup status, lingering owned PIDs, peak RAM,
peak CUDA allocation, and abort reason remain part of the execution receipt.

The local laptop GPU is excluded while it is shared with deadline work or
thermally elevated. No local outcome run is authorized by this document.
