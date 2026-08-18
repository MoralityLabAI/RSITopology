# ASMP-9 v0.42.1 protocol amendment

## Reason

The sealed v0.42 executor failed before seed derivation because it attempted
`float("1/1000")`. The repair is restricted to parsing exact rational strings
through `Fraction` before float conversion.

## Frozen invariants

The following remain byte-for-byte or value-for-value identical to v0.42:

- three query signatures and population error rates;
- four targets and 48,000 samples per target/query;
- shared-parameter pooling;
- `alpha=0.05` and the simultaneous TV-radius formula;
- horizon two and exact Bellman/LP compilation;
- decision losses, tolerances, and `1/1000` practical margins;
- all nine scientific/resource gates and their precedence;
- 900-second and 1.25-GiB ceilings; and
- the complete claim boundary.

The repair derives a fresh seed from the exact v0.42.1 registration bytes with
the versioned domain separator:

```text
asmp9-v0.42.1-sampled-confirmation
```

The original registration and failure receipt are sealed into the repair.

## Regression requirement

The executor test must call the same parser used by the run on literal
`"1/1000"` and obtain exactly the binary float conversion of
`Fraction(1,1000)`. Decimal strings remain accepted; malformed strings fail.

No result may be produced until the repair implementation and then the new
registration are separately committed and pushed.
