# ASMP-9 finite risk-polytope access protocol v0.40

## Registration state

`prospective_confirmation_not_yet_executed`

The confirmation is run only after this protocol, source, exact solver,
environment, fixture, and tests are hash-sealed in a pushed registration.

## Question

Can necessary and sufficient access for an arbitrary finite registered
decision type be represented exactly by upper risk-polytope containment, and
does changing only the loss type change the minimal sufficient query
antichain?

## Primary theorem

For every finite decision problem `d`, let `R_d(E)` be the convex polytope of
target-wise risks achievable after experiment `E`, and let

```text
U_d(E) = R_d(E) + R_+^Theta.
```

The registered deficiency is the smallest `epsilon` such that

```text
R_d(F) subset U_d(E) + epsilon*1
```

for every problem in the registered decision type. This is a classical
finite risk-set characterization, not a novelty claim.

## Disjoint fixture

Four targets and four deterministic queries:

```text
s0      = (0,0,1,1)
s1      = (0,1,0,1)
sx      = (0,1,1,0)
s_const = (1,1,1,1).
```

The fixture was not used in the three-target development run.

Decision types:

1. four-target zero-one classification;
2. the `s0` binary partition with false-positive cost `1/4` and
   false-negative cost `1`;
3. the `s1` partition with false-positive cost `3/5` and false-negative cost
   `4/5`; and
4. the conjunction of both asymmetric group problems.

## Frozen predictions

For classification, if the largest unresolved query-signature block has size
`k`,

```text
delta_D = 1 - 1/k.
```

The persistence curve is:

```text
epsilon=0:   {s0,s1}, {s0,sx}, {s1,sx}
epsilon=1/2: {s0}, {s1}, {sx}
epsilon=3/4: empty access.
```

For a mixed binary group block, exact deficiency is

```text
c_fp*c_fn/(c_fp+c_fn).
```

Therefore:

```text
s0 group critical value = 1/5
s1 group critical value = 12/35.
```

The zero-tolerance antichains are:

```text
s0 group:       {s0}, {s1,sx}
s1 group:       {s1}, {s0,sx}
combined groups:{s0,s1}, {s0,sx}, {s1,sx}.
```

For the combined type, tolerance `1/5` leaves `{s1}` and `{s0,sx}`;
tolerance `12/35` admits empty access. The constant query never changes any
deficiency and never enters an inclusion-minimal access family.

## Gates

- **P0:** all eight preregistration tests pass.
- **S0:** every sealed hash matches before evaluation.
- **R0:** exact row-universe equality: 16 analytic classification rows,
  16 rows for each of three compiled types, and 3 exact solver spot checks.
- **C0:** classification values equal `1-1/k`, and zero agrees exactly with
  Test Cover.
- **H0:** exact primal-dual solver spot checks match the partition formula at
  empty, one-query, and revealing access.
- **G0:** both asymmetric group tables match
  `c_fp*c_fn/(c_fp+c_fn)` on mixed blocks and zero on pure blocks.
- **D0:** all four zero-tolerance access antichains match the frozen sets.
- **F0:** every critical tolerance and minimal-access persistence transition
  matches the frozen curves.
- **K0:** appending/removing `s_const` changes no deficiency.
- **RESOURCE:** execution stays within 600 seconds, 1 GiB, one process, and
  one BLAS thread.

All gates are conjunctive. No tolerance or access family is changed after
registration.

## Claim boundary

A passing run establishes a complete exact characterization only for finite
rational experiments relative to registered finite loss types, plus the
deterministic Test Cover specialization. Exhaustively finding a minimum
zero-error family is NP-hard in general. The run does not characterize
continuous reward classes, adaptive query policies, finite-sample learning,
unknown links, strategic demonstrators, real models, or all of ASMP-9.
