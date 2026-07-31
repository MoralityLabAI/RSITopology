# ASMP-9 v0.68.2 local execution-resource amendment

Status: **execution-only amendment; no confirmation outcome read**.

This additive amendment replaces only the v0.68 Prime execution envelope for
the untouched v0.68.1 confirmation split. It does not change:

- the Qwen3.5-0.8B-Instruct model or tokenizer bytes;
- the 528 confirmation records or their deterministic order;
- singleton float16 CUDA scoring;
- the v0.68 scientific protocol or v0.68.1 inferential amendment;
- the construction decision and sealed construction intersection;
- any endpoint, threshold, gate, or decision mapping; or
- the claim boundary.

## Reason

The user explicitly authorized the already-free local RTX 3050 on 2026-07-31.
The workload is inference only: no model is trained or updated. The model
weights occupy about 1.75 GB and the runner checkpoints every scored record,
so the four-GB device is adequate if it passes the prereveal allocation and
temperature checks.

## Frozen local envelope

The machine-readable authority is
`local_execution_resource_amendment_v0_68_2.json`.

```text
job memory hard cap:             6,144 MB
minimum free host memory:        4,096 MB
CPU hard cap:                       50%
sustained process I/O ceiling:      50 MB/s
GPU allocation delta ceiling:    3,900 MB
GPU temperature abort:              88 C
wall timeout per phase:           3,600 s
batch size:                           1
prompt cap:                         768 tokens
checkpoint cadence:                   1 record
```

Windows Job Objects enforce the job-memory, CPU, and kill-on-close limits.
The wrapper polls process I/O, GPU allocation, temperature, elapsed time, and
free host memory. Five consecutive one-second I/O samples over the ceiling
are a hard abort. Any timeout, resource breach, source/hash mismatch, changed
answer-token boundary, or incomplete record set is an abort, not permission
to relax the envelope.

The Windows page file cannot be disabled per Job Object. The wrapper therefore
records system page-file usage and page reads before, during, and after the
run; any detected increase while the owned job is live is reported as
`swap_activity_detected` and makes cleanup invalid. This is a disclosed
platform limitation, not a scientific result.

## Chronology

The local wrapper, cleanup script, registration builder, tests, this document,
and the machine-readable amendment must be committed before prereveal
validation. The exact external registration and authorization hashes must then
be committed and pushed in a second receipt before any confirmation forward
pass.

## Claim boundary

This amendment authorizes one bounded execution environment. It contributes
no evidence about value identification and cannot change the meaning of a
positive, negative, invalid, or aborted confirmation result.
