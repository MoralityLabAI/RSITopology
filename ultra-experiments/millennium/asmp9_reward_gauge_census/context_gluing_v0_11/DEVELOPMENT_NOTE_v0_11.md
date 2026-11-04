# ASMP-9 v0.11 development note

## Burned cells

Development tests exhaust every pair of simple context graphs on the common
item universes of size two, three, and four. The largest burned universe is:

```text
2^(2 * choose(4,2)) = 4,096 context-graph pairs.
```

For every pair, the direct exact incidence-rank difference matched:

```text
beta_1(labelled union) - sum_context beta_1(context graph).
```

The four-item/two-context mixed-rank distribution was:

| mixed-cycle rank | graph pairs |
|---:|---:|
| 0 | 277 |
| 1 | 864 |
| 2 | 1,511 |
| 3 | 1,444 |

Thus `3,819/4,096` burned pairs had a live mixed-context obstruction space,
while 277 forced gluing by design.

The implementation also constructed a locally scalar nongluing witness if and
only if that mixed-cycle rank was positive, extended local cycle bases to the
mixed quotient at the predicted dimension, and exercised all four decision
statuses on deterministic fixtures.

These cells are burned. A prospective verification must use a different
context count or item universe, plus fresh seeded graph cells.

## Interpretation

The theorem is elementary graph linear algebra. Its ASMP-9 value is the access
separation:

- local scalar rationality does not imply a shared scalar across contexts;
- the exact missing information is a quotient of cycle spaces; and
- quotient dimension zero is a forced result, not a live empirical
  confirmation.

No claim is made about human preferences, language-model preferences, or
infinite histories.
