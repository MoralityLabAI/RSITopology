# ASMP-10 checkpoint and dwell audit v0.5.2

## Question

Can the burned v0.4 checkpoints be replayed at 25 or 50 optimizer-step
resolution to measure the duration of the seven threshold excursions?

## Answer

No. Each of the six run directories contains one `checkpoint.pt`. Every file
reports `step = 15000` and contains only the final rolling model/optimizer/RNG
state plus the accumulated 100-step metric history. Intermediate checkpoint
states were overwritten rather than retained as a checkpoint series.

The observed event structure is:

- preceding 100-step evaluation: qualified;
- event evaluation: not qualified; and
- following 100-step evaluation: qualified.

Consequently, the duration of each underlying continuous excursion lies within
an interval shorter than 200 optimizer steps. Its precise start, end, and
duration are not recoverable from the retained state.

## Decision

The proposed replay-from-burned-checkpoints option is unavailable. v0.5.2 uses
the alternative allowed by the review:

- primary exit dwell 300 steps, above the censored bound;
- primary metrics every 25 steps;
- deterministic cadence replay at 50 and 100 steps; and
- a separate dwell-fragility replay over 250, 300, and 400 steps.

No GPU work was performed for this audit. Loading the six trusted checkpoints
on CPU was limited to reading their top-level keys and `step` field.

