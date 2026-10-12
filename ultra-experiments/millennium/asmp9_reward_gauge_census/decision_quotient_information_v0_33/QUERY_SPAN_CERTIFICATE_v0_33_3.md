# Fail-closed query-span certificate for the ASMP-9 coupling quotient

## Status

**Unregistered development result. Not claim-eligible.**

This instrument decides whether a proposed coupling-probe grammar measures
everything needed for the declared policy decision. When it does not, the
instrument returns an exact counterexample rather than a low-rank warning.

The machine-readable result is
[`QUERY_SPAN_DEVELOPMENT_v0_33_3.json`](QUERY_SPAN_DEVELOPMENT_v0_33_3.json),
SHA-256
`57ad24c0ce2d9cc026faf17af9212c5f905634494d34095a53779c0e726cc8fa`.

```text
focused v0.33 tests                    32 passed
v0.28-v0.33 predecessor/current tests 114 passed
```

## Span criterion

Let `M = transpose(C) kron (Q L)` be the canonical decision operator and let
`H` contain the scalar linear functionals implemented by a proposed query
grammar. Then:

```text
the grammar spans the decision quotient
  iff row(M) is a subset of row(H)
  iff rank(stack(H,M)) = rank(H).
```

The number of missing decision dimensions is:

```text
rank(stack(H,M)) - rank(H).
```

When this number is positive, exact nullspace elimination constructs
`delta_k` satisfying:

```text
H delta_k = 0;
M delta_k != 0.
```

Thus two couplings separated by `delta_k` give every admitted query the same
answer while changing a registered policy effect.

## Passing construction and quantitative reconstruction

For a passing grammar, the code constructs `R` with:

```text
M = R H.
```

If every measured probe has absolute error at most `epsilon`, the reconstructed
decision-effect error is bounded deterministically by:

```text
||error_decision||_infinity
  <= ||R||_(infinity -> infinity) epsilon.
```

The first greedy 18-probe factorized basis spans the quotient but has
worst-case amplification `12`.

An exhaustive exact search over all factorized bases evaluates:

```text
policy-row bases       10
behavioral-cell bases  432
```

The preferred basis is:

```text
policy contrasts       0, 1, 2
behavioral cells        0, 1, 2, 4, 5, 7
policy amplification   2
cell amplification     4
combined amplification 8
```

It retains 18 queries and exact rank 18 while reducing the deterministic
error multiplier by one third.

## Adversarial controls

The instrument was required to fail on three shortcuts:

```text
omit one factorized probe  18/18 fail, one missing dimension each
omit one raw coordinate    48/48 fail, one missing dimension each
six diagonal composites     fail,  twelve missing dimensions
```

Every failure includes an exact invisible-but-decision-changing witness.
This prevents “almost all probes” from being promoted into complete access.

## Claim boundary

The certificate is exact linear algebra over the sealed finite matrices. It
does not establish that the 18 composite probes can be physically implemented,
that model responses remain linear at useful intervention norms, or that an
empirical error envelope `epsilon` is small enough for a downstream policy
margin. ASMP-9 remains unresolved.
