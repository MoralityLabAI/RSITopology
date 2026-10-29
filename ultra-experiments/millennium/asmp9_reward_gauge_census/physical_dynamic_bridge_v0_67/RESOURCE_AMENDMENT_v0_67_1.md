# ASMP-9 physical dynamic bridge resource amendment v0.67.1

Status: registered before any score record was opened or interpreted.

This amendment changes one execution parameter:

- `resource_contract.batch_size`: `8` to `4`.

It leaves the scenario universe, split assignment, prompt bytes, display
orders, arms, deterministic A/B score, construction calibration rules,
instrument gates, scientific endpoints, stop rules, model bytes, RAM/CPU/I/O
caps, GPU allowance, timeout, and claim boundary unchanged.

## Reason

The first score-producing infrastructure attempt was terminated automatically
at 56 of 240 construction records when total process-visible GPU use reached
4,125 MB, 29 MB above the preregistered 4,096 MB allowance. The attempt's
cleanup receipt passed. Neither the 56 work-unit files nor any option score was
opened before this amendment was frozen.

Earlier zero-record attempts identified a filesystem-cap lookup bug, a
noncanonical model filename, and a missing Python development header. Those
attempts produced no score records.

Batch size four is a conservative resource correction derived from the
observed resource overrun, not from a scientific outcome. The restarted
construction run uses a fresh result directory and does not import or resume
the 56 unrevealed work units. Confirmation, if authorized later, must use this
same amended protocol and batch size.

## Claim boundary

The amendment is not evidence about contextual effects, restoration,
persistence, consensus, a latent transducer, preferences, values, or recursive
self-improvement. It only makes the frozen construction measurement executable
inside the original hard GPU ceiling.
