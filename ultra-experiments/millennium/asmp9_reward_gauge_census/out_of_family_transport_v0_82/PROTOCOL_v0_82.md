# ASMP-9 v0.82: Out-of-family response transport

Status: **prospective; no v0.82 model score read**.

## Question

Does a nuisance-quotiented content-versus-label response contrast fitted on the
sealed v0.68 construction registry transport without refitting to twelve
behavior families absent from that registry?

This is the next admissible test after v0.81.  The synthetic v0.81 result showed
that known physical intervention offsets can make a decoder succeed.  It did
not show that useful structure survives a real response channel or transports
outside the calibration families.  V0.82 asks only the latter question.

## Frozen construction object

The v0.68 construction analysis is burned design input.  Its hash and exact
derived quantities are frozen in `protocol_v0_82.json`:

- scenario-mean center: `0.9381510370100538`;
- maximum construction residual: `0.4173176869129162`;
- prediction envelope: `[0.5208333500971378, 1.3554687239229698]`; and
- common-coefficient intersection: `[0.7343614199407966, 0.750013550256881]`.

The v0.82 outcome cannot move these quantities.  The first interval is a
finite-registry max-residual prediction envelope, not a population confidence
interval.  The second is a compatibility intersection, not a point estimate.

## Freshness

The twelve executed family labels are disjoint from all twelve v0.68 family
labels.  Situations, options, and reasons are prospectively frozen.  The
manifest contains unexecuted construction rows only because the unchanged
v0.68 scoring module validates a paired split schema; those rows are structural
padding and cannot enter any v0.82 statistic.

## Measurement

The model scores only the exact next-token alternatives `A` and `B`.  Each
semantic input is repeated byte-identically twice and rendered in both display
orders.  For target `t`, the directed specificity is

```text
d(t) * (score(content_t) - score(label_t))
```

where `d(0)=+1`, `d(1)=-1`, and scores are canonicalized across the display
swap.  The content and label coefficients sum to zero, so a scenario/display
common additive nuisance is removed exactly.

## Gates and decision

The machine-readable protocol is authoritative.  In words:

- `N0` binds the new-family and score universes;
- `I0` binds repeated inputs, rendering, arithmetic, and quotient mechanics;
- `L0` requires local liveness on at least ten of twelve families;
- `T0` requires at least ten scenario means inside the frozen construction
  prediction envelope;
- `G0` requires all 24 target cells to remain compatible with the frozen
  construction coefficient interval; and
- `R0` requires the owned process to respect its hard execution contract.

All gates are fixed-sequence and equality does not pass.  A negative result is
reported without changing the family registry, envelope, interval, or endpoint
epsilon.

## Resource semantics

The scorer remains singleton float16 inference on the local Qwen0.8B model.
The Windows job object limits the owned process tree.  GPU temperature, GPU
memory, free RAM, I/O, and system page-file use are recorded.  A system-wide
page-file delta cannot be causally assigned to this process and is therefore
diagnostic in v0.82; owned-process hard-limit or cleanup failure remains fatal.
This prospective clarification responds to v0.68.2.1's three-megabyte
system-wide movement and does not revise that prior receipt.

## Claim boundary

Even a pass is evidence about an expressed model response contrast in one
finite registry.  It is not preference or reward identification, natural
availability of intervention metadata, human-value inference, population
generalization, self-improvement authorization, or an ASMP-9 resolution.

