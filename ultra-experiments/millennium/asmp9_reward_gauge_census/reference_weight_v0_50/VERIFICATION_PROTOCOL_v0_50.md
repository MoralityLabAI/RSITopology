# ASMP-9 v0.50 reference-law theorem verification protocol

## Status

This protocol freezes an exhaustive finite theorem check. It does not
prospectively register a model experiment or establish novelty.

## Frozen objects

### Bound-table universe

Enumerate every monotone binary table on three outcomes satisfying

```text
B(empty)=0.
```

The registered count is:

```text
Dedekind M3:              20
excluded constant-one:     1
admissible tables:        19
ordered objective pairs: 361.
```

### Reference family

Use the convex hull of the two strictly positive vertices

```text
v_0 = (1/2,1/3,1/6)
v_1 = (1/6,1/3,1/2).
```

The complete positive denominator-six grid is used for the explicit
weight-region audit:

```text
{(a,b,c)/6 : a,b,c positive integers, a+b+c=6}.
```

It has ten points.

## Gates

### H0: source integrity

Every registered source hash must match.

### T0: tests

All eight scientific tests and all three verifier tests must pass.

### D0: robust-chain census

For all `19^2=361` ordered table pairs:

- the robust tight-DAG count must equal exhaustive intersection over all six
  orderings and all four `(objective,vertex)` scenarios;
- existence and lexicographic representatives must agree; and
- mismatch count must be zero.

No condition is registered on how many pairs are robust. That is an output,
not a gate chosen in advance.

### R0: weight-region identity

For every table, every ordering, and every positive denominator-six grid
point, halfspace membership must agree with exhaustive optimality:

```text
19 * 6 * 10 = 1,140 checks.
```

### V0: vertex theorem

Every robust lexicographic ordering found at both vertices must remain
optimal for both objectives at interpolation coefficients

```text
0, 1/4, 1/2, 3/4, 1.
```

### M0: minimal sensitivity witness

The registered two-outcome Buehler table `(0,0,0,1)` at reference vertices
`(3/4,1/4)` and `(1/4,3/4)` must have:

```text
robust optimizer count = 0
minimum worst-case regret = 1/2
minimax optimizer count = 2.
```

### Q0: regret equivalence

For every three-outcome table pair, exact minimum worst-case regret is zero
if and only if the exhaustive robust optimizer intersection is nonempty.

### B0: v0.48 recovery

At the singleton v0.48 reference law, the implementation must recover

```text
robust/common optimizer count = 1,451,520.
```

### RESOURCE

The single verification process must finish within 120 seconds and
512 MiB peak working set.

## Stop rule

The theorem is verified only if every gate passes. There is no threshold
adjustment or discretionary near-pass.

If a bookkeeping or verifier defect is discovered after execution, the
original registration and receipt remain immutable. Any repair must be
additive, separately registered, and unable to change a scientific value.

## Claim boundary

Passing verifies finite identities for the registered table and reference
universes. It does not establish novelty, efficient large-width
representation, randomized confidence optimality, continuous or strategic
robustness, a physical preference channel, or an ASMP-9 resolution.
