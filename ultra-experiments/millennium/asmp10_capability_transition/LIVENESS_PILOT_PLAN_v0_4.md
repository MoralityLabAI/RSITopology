# ASMP-10 transition-liveness pilot v0.4

## Status and purpose

This is a construction pilot, not a claim-eligible prediction experiment. It
tests whether the existing modular-addition family can produce a delayed,
measurable held-out transition inside the registered resource envelope. Its
rows may select a later model family and horizon; they may not be used to fit
or evaluate the eventual predictor.

The pilot implements the prospective factorial suggested in
`prefix_obstruction/SUCCESSOR_SCOPE_v0_2.md`:

- train fraction in `{0.40, 0.55, 0.70}`;
- AdamW weight decay in `{1.0, 2.0}`;
- one construction seed per cell;
- 15,000 optimizer steps per cell.

The same seeded permutation defines nested training sets across train
fractions. This isolates the amount of observed data without changing the
ordering of examples.

## Frozen liveness definitions

Evaluation occurs every 100 steps.

- **Sustained memorization:** train accuracy is at least `0.99` for five
  consecutive evaluations.
- **Sustained held-out transition:** test accuracy is at least `0.90` and test
  loss at most `0.50` for five consecutive evaluations.
- **Delayed-transition candidate:** both events occur and the first sustained
  held-out transition begins at least 500 optimizer steps after the first
  sustained memorization event.

The pilot is live only if at least one cell is a delayed-transition candidate.
An early-generalizing cell is reported but cannot open the predictor protocol.
No transition by step 15,000 is a bounded pilot outcome, not an impossibility
claim.

## Resource enforcement

The trainer must run through the already validated Windows Job Object wrapper.
The existing caps are not loosened:

- host commit/RAM cap: 2,048 MB;
- CPU hard cap: 50%;
- monitored I/O ceiling: 50 MB/s;
- wall timeout: 1,800 seconds;
- registered GPU allowance: 3,072 MB;
- PyTorch allocator hard cap: 2,048 MB;
- checkpoint cadence: every 200 steps or 60 seconds;
- declared swap allocation: zero;
- minimum free physical memory at admission: 4,096 MB.

WDDM does not expose reliable per-process GPU usage through `nvidia-smi` on
this host. Version 0.4 therefore treats global GPU use as descriptive and uses
`torch.cuda.set_per_process_memory_fraction` as the attributable fail-closed
allocator limit. Allocated and reserved bytes are recorded on every trainer
event. The Windows wrapper remains responsible for host memory, CPU, I/O,
timeout, checkpoint liveness, owned-PID cleanup, and the post-run audit.

## Branch rule

- If at least two cells produce delayed transitions, draft—but do not run—a
  disjoint-seed predictor preregistration.
- If exactly one cell does, run a separately registered confirmation pilot on
  a fresh construction seed before drafting the predictor protocol.
- If no cell does, retain the bounded negative and do not enlarge the horizon
  without another versioned authorization.

Nothing in this pilot constitutes evidence that capability transitions are
predictable, that a richer observable beats a loss prefix, or that recursive
self-improvement exists.
