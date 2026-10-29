# ASMP-9 context-gluing resource repair v0.11.2

## Reason

The registered v0.11 and v0.11.1 attempts both exceeded the unchanged
360-second wall-time cap and were terminated without scientific artifacts.
Version v0.11.1 reduced the complete ordered graph-triple census to about
0.2 seconds, localizing the remaining cost to repeated rational
rank/augmented-rank calculations in the 4,096 seeded cells.

Both failed attempts remain part of the record:

- `EXECUTION_ATTEMPT_v0_11.md`; and
- `EXECUTION_ATTEMPT_v0_11_1.md`.

## Exact implementation repair

Version v0.11.2 changes no scientific cell, seed, status, gate, threshold, or
resource limit. It uses two exact facts about graph incidence matrices:

1. an oriented incidence matrix has rank `|V|-c` over both the rationals and
   `GF(2)`, including disconnected graphs; and
2. the graphic cycle-space dimension is field-independent.

Incidence supports are therefore represented as integer bitsets and reduced
by exact `GF(2)` elimination. Actual shared-scalar decisions remain signed
circulations computed with `fractions.Fraction`; no sign or magnitude is
discarded from a scientific decision.

The non-gluing witness search scans the exact local-incidence generators and
selects the first generator with nonzero signed circulation on the independent
mixed-cycle checks. The local-failure control likewise uses a signed rational
cycle circulation.

## Burned equivalence evidence

Before freezing v0.11.2, the literal and optimized implementations were
compared on:

- a 64-cell independent burned ensemble;
- the first four cells of the already registered seed; and
- the first sixteen cells of registered seed `1101101`, the prefix that
  exposed the pathological rational-basis cost.

On the sixteen-cell prefix, every scientific field was exactly equal after
removing only the optimized implementation label. The canonical JSON SHA-256
on both sides was:

```text
3ec6e56901ea89fcdbba8b6728e7cfcaab58dbbe6af783db66658d7eceec18d4
```

Measured on the same host:

```text
literal: 129.636437 seconds
optimized: 0.316338 seconds
ratio: 409.80x
```

Those sixteen cells are explicitly burned implementation-validation data. The
4,096-cell scientific specification and all gates were inherited unchanged
from the already frozen v0.11 protocol; no result-dependent threshold choice
was made.

## Claim boundary

This is an implementation repair, not a protocol relaxation and not a new
scientific hypothesis.
