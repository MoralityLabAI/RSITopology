# ASMP-9 v0.35 monotone-ruler repair-radius analysis

**Status:** `retrospective_development_not_confirmation`

For an ordered score curve `y`, the exact distance to the cone of
nonincreasing curves is

```text
d_inf(y, C) = 0.5 * max_(i<j) (y_j - y_i)_+.
```

This is a classical isotonic-regression fact. It separates small local
non-monotonicity from the distinct problem of missing endpoint support.

| Curve set | Curves | Robust crossings | Median d_inf | Maximum d_inf |
|---|---:|---:|---:|---:|
| standard gambles | 36 | 4 | 0.015022 | 0.053540 |
| preferred standard basis | 18 | 2 | 0.013755 | 0.053540 |
| compound gambles | 18 | 10 | 0.001538 | 0.026448 |

The repair radii are modest, especially for compound lotteries, but only a
strict subset of the required curves has endpoints that force a zero crossing
under every radius-close repair. Isotonic regression would smooth the curves;
it would not make the unavailable certainty equivalents observed.

## Decision

`v0_34_prompt_ruler_not_admissible`

The successor must independently estimate code/position error and include the
dominance endpoints `p=0` and `p=1`. Mixture and decision-quotient analysis
remain downstream of that admission gate.

## Claim boundary

This is a retrospective analysis of burned pilot summaries. It cannot confirm a ruler, consume the untouched holdout, or resolve ASMP-9.

Analysis content SHA-256:
`8bd9c44d3d6a7a6a7849c7f79484317edd7d0ea53cacb11d707e29b19c9cd4e5`
