# ASMP-9 v0.22.1 post-run note

## Outcome

```text
uniform_above_floor_value_complexity_classified_v0_22_1
```

All ten registered gates passed.  The independent verifier passed 17/17
checks.

## What changed relative to v0.22

Only the frozen complexity-attribution evaluator changed: complete structured
lists are now compared by exact equality.  The predecessor's failed verdict,
gate map, registration, result, receipt, and independent-verification files
were hash-bound and matched.  Three new graph cells replaced the burned v0.22
cells.

## Scientific consequence

The count-floor complexity of v0.21 extends to every declared fixed uniform
count `r>=2`.  Exact value evaluation, not optimizer search, is already
#P-hard within one irreducible biconnected block.

The next load-bearing gap is not another uniform-count cell.  It is the
nonuniform local-design problem: characterize or bound maximin allocation
when edge counts vary inside an overlapping-cycle block, including whether
optimization can avoid repeated #P-hard value-oracle calls.
