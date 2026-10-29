# ASMP-3 moment-order addendum: prior-art boundary

The v0.1.3 result is another finite specialization of the classical discrete
binomial moment problem. The governing framework and sharp-bound lineage are
described in `PRIOR_ART_v0_1_2.md`, especially Boros and Prékopa (1989),
[DOI:10.1287/moor.14.2.317](https://doi.org/10.1287/moor.14.2.317).

The fourth-factorial-moment inequality

```text
1{S>=5} <= (S)_4 / 120
```

is a direct finite moment bound, not a new inequality. Likewise, enumerating
extreme distributions with at most `m+1` support points is standard linear
programming geometry for a probability simplex with normalization and `m`
moment constraints.

The contribution claimed here is limited to the exact specialization at nine
exchangeable judgments, independent-reference moments with marginal error
`1/5`, and a `1/20` majority-error requirement. The safety interpretation is
that this frozen reference cannot be certified from moments through order
three, while moments through order four suffice. No general minimal-moment
theorem or empirical judge claim is made.

