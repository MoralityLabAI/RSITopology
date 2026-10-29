# ASMP-10 modular-addition pilot trainer plan

## Status

Pilot-only, pre-registration. This run maps runtime and transition liveness; it
cannot support the eventual held-out prediction claim. The claim-eligible
protocol will be frozen only after the pilot fixes a horizon, model family,
observable time, and train/holdout seed split.

## Training task

- **Task ID:** `asmp10-grokking-v0-1`
- **Task:** modular addition modulo 31 from two input tokens.
- **Model:** one-layer, four-head transformer, width 64, full-batch AdamW.
- **Chunk unit:** one `(seed, weight_decay)` run.
- **Pilot horizon:** 4,000 optimizer steps per chunk.
- **Checkpoint cadence:** every 100 steps or 60 seconds, whichever comes first.
- **Evaluation cadence:** every 50 steps.
- **Transition definition:** held-out accuracy at least 0.90 and held-out loss at
  most 0.50 for five consecutive evaluation points.

## Hard caps

The inner trainer must run only through the validated Windows Job Object wrapper.

- aggregate/process commit: 2,048 MB;
- CPU hard cap: 50%;
- monitored I/O cap: 50 MB/s, abort after three consecutive breaches;
- GPU allowance: 3,072 MB;
- wall timeout: 1,800 seconds;
- declared swap allocation by the experiment: zero;
- host free-memory preflight: 4,096 MB (2,048 MB run cap plus 2,048 MB reserve).

The current wrapper was revalidated on 2026-07-20 against success, memory, CPU,
I/O, timeout, and cleanup probes. The authorization JSON binds the wrapper,
validation receipt, cleanup script, config, and trainer hashes.

## Observables

The pilot records metrics prospectively at every evaluation and geometry once at
the frozen early-feature step:

- train and held-out cross-entropy and exact accuracy;
- total parameter norm and gradient norm;
- stable rank of token embeddings and output weights;
- participation-ratio effective rank of the final-token representation over the
  complete modular-addition domain.

These are spectral/geometry candidates, not local learning coefficients. A later
claim may compare them with loss-curve features; this pilot cannot make that
comparison on held-out data.

## Abort and cleanup semantics

Cap breach, stale checkpoint, timeout, nonfinite loss, or owned-process cleanup
failure is a valid abort outcome. Each abort writes a summary and event record.
The trainer releases model, optimizer, tensors, and CUDA allocations in a
`finally` block. The wrapper terminates only recorded owned PIDs and runs the
shared post-run memory/GPU audit.
