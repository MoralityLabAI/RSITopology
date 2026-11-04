# ASMP-9 v0.25 development note

## Correction made during exploration

An initial scratch derivation used an incorrect two-terminal diagonalization
for the ASMP partial-orientation law.  It was never committed as a result.
Direct comparison with the v0.23 multivariate evaluator exposed the error.

The corrected path-state derivation gives:

```text
S = product(2A-B) - 2 product(A-B).
```

All executable tests use this corrected formula and independently compare it
with v0.23.

## Why this branch matters

The v0.23 K4 trap ruled out one-exchange/M-concavity but left open whether any
overlapping-cycle blocks have a provable global optimizer.  Generalized theta
blocks provide such a boundary:

- the strong-orientation event has a closed path-state formula;
- strict smoothing removes all within-path count gaps of two or more; and
- exact search remains only over path totals.

This does not solve the arbitrary-block optimizer.  It identifies a larger
tractable class than a single cycle or a cactus block while preserving the
binary-budget complexity caveat.

## Burned development cells

The following cells were inspected during theorem formation and cannot be
used as fresh registered evidence:

- path lengths `(1,2,2)`, total budget `10`;
- `(1,2,3)`, total budget `11`; and
- `(2,2,3)`, total budget `12`;
- all formula cells in `test_theta_optimizer_v0_25.py`; and
- all enumerated count vectors used by the smoothing test.

Any registration must use separately generated graph lengths and budgets
whose outcomes have not been read.

## Current status

Development-only, unregistered, and not claim-eligible.

