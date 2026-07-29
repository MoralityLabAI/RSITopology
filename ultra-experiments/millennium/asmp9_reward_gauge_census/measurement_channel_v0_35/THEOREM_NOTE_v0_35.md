# Exact monotone-ruler repair radius

Let `C` be the cone of nonincreasing sequences in `R^(m+1)`. For an observed
ordered ruler curve `y`,

```text
d_inf(y,C) = (1/2) max_{i<j} (y_j-y_i)_+.
```

## Proof

If `z` is nonincreasing and `||z-y||_inf <= delta`, then for every `i<j`,

```text
y_j-y_i <= (z_j+delta)-(z_i-delta) <= 2 delta.
```

Therefore every repair needs at least half the largest order violation.

Set `delta` equal to that lower bound and define

```text
z_i = max_{j>=i} (y_j-delta).
```

The suffix maxima are nonincreasing. The term `j=i` gives
`z_i >= y_i-delta`; the defining pairwise bound gives
`y_j-delta <= y_i+delta` for all `j>=i`, hence
`z_i <= y_i+delta`. Thus `||z-y||_inf <= delta`, attaining the lower bound.

## Robust crossing corollary

If `y_0 >= delta` and `y_m <= -delta`, every monotone curve within `delta` of
`y` has nonnegative left endpoint and nonpositive right endpoint. A zero
crossing is therefore forced on the registered grid. If either endpoint
condition fails, isotonic smoothing cannot certify the missing support.

This is a classical isotonic-regression specialization, not a novelty claim.
Its role here is to replace a brittle count of adjacent violations with an
exact, scale-aware certificate.
