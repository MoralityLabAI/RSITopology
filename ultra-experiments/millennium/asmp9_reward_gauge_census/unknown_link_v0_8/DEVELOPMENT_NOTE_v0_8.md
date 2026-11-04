# ASMP-9 unknown-link development note v0.8

## Exact witness

The rational construction verifies:

```text
u  = (0,1,3),
u' = (0,1,4),
```

are not positive-affine equivalent, but have identical complete pairwise
probability laws under separate strictly increasing symmetric rational links:

```text
P(1>0)=3/4,
P(2>1)=5/6,
P(2>0)=7/8.
```

The same known link distinguishes them. The ambiguity is therefore caused by
the nuisance-link class, not by a coding error in the utilities.

## Burned finite census

Before prospective registration, primitive strictly increasing integer utility
rays were anchored at zero, quotiented by integer common scale, and grouped by
their complete labelled difference-order signatures.

| items | coordinate bound | primitive rays | difference-order classes | ambiguous classes | rays in ambiguous classes | largest class |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 64 | 1,259 | 3 | 2 | 1,258 | 629 |
| 4 | 24 | 1,747 | 25 | 22 | 1,744 | 247 |
| 5 | 12 | 479 | 239 | 104 | 344 | 9 |

For three items, the three classes are exactly whether the first adjacent
utility gap is less than, equal to, or greater than the second. All but the
single symmetric primitive ray fall into non-affine ambiguity classes at the
registered bound.

The current development suite contains 144 exact tests covering link inversion,
unknown-temperature recovery, the non-affine witness, generic
difference-order interpolation, minimality at two items, and equality of
arbitrarily repeated response laws.

## Status

These counts are burned design evidence. They show the obstruction is not an
isolated example but cannot serve as fresh verification cells. No
claim-eligible v0.8 execution has occurred.
