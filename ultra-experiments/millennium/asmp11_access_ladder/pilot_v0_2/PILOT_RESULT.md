# ASMP-11 v0.2 construction-pilot result

## Status

`construction_only_non_claim_eligible_pilot`

This result was produced before a v0.2 registration and cannot pass a
scientific gate or be pooled with a later claim-eligible run.

## Result

The exact-power pilot evaluated 720 plan cells across 48
`(n,k,flip-rate)` conditions. It used exact rational binomial tails, a
union-bound familywise-error ceiling of `0.05`, and a signal-power floor of
`0.90`.

Two facts held in every condition:

1. No complete nonadaptive plan on the matched boundary `r+s=k` used fewer
   samples than pure order-`k` observation. The best boundary sample count tied
   pure observation exactly.
2. A containment intervention eventually used fewer samples, but only after
   buying additional intervention width. The first inversion required fixing
   between `7/12` and `9/10` of all parents on the pilot grid.

The first inversion width was invariant across the three flip rates. For the
exhaustive containment family it followed

```text
s_first = max(k+1, n-k+1),
```

the first width for which `binom(n,s) < binom(n,k)`. A universal width-`n`
clamp reduced the design to one query and required 9, 17, or 42 oracle samples
at flip rates `0.05`, `0.15`, or `0.25`, respectively. That is a sample-cost
win purchased with maximal intervention strength, not resource dominance.

## Mathematical diagnosis

For order-zero parent fixing, a query on fixed set `I` is live exactly when the
unknown parity support `T` is contained in `I`. Under the clean model every
population response is zero. Therefore, along the all-negative adaptive path,
the queried sets must cover every possible `k`-support; otherwise an uncovered
planted support has the same transcript as clean.

The worst-case adaptive query problem is consequently a covering-design
problem. Its structural cost is the covering number `C(n,s,k)`, not the
exhaustive count `binom(n,s)` used by this pilot. The next registered experiment
should compute that covering frontier on a disjoint grid and layer exact
finite-sample power on the certified block counts.

## Consequence for the draft

The original “adaptive intervention becomes cheaper” hypothesis is
under-specified. It must become:

> At what intervention width does the exact covering-number design require
> fewer oracle samples than pure observation, under matched false-positive and
> power constraints?

An adaptive heuristic may be compared with the covering optimum, but cannot
evade the worst-case coverage lower bound. Internal-wire value injection is a
different access class and remains separately labelled.
