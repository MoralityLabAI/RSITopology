# ASMP-9 contextual scalar-gluing protocol v0.11

## Status

Prospective CPU-only exact verification protocol. All two-context graph pairs
on two through four common items, all three- and four-context graph tuples on
three items, the canonical two-item witness, and all unit-test fixtures are
burned.

## Frozen statement

Each registered context or finite history supplies a comparison graph on one
common finite item universe. Parallel edge copies in different contexts remain
distinct. A flow is context-locally scalar when each context flow is a
gradient; it has a shared scalar when the labelled-union flow is one global
gradient.

Conditional on local scalarity, the obstruction quotient has dimension

```text
q
  = rank(D_local)-rank(D_union)
  = beta_1(labelled union)-sum_context beta_1(context graph).
```

Exactly `q` independent mixed-context cycle checks are necessary and
sufficient in the registered exact-linear access model.

The decision vocabulary is total:

- `local_scalar_failed`;
- `shared_scalar_forced_by_design` when `q=0`;
- `shared_scalar_verified` when `q>0` and all mixed circulations vanish; and
- `shared_scalar_refuted` when at least one mixed circulation is nonzero.

## Fresh cells

### Exact three-context census

Enumerate every ordered triple of simple context graphs on four common items:

```text
2^(3 * choose(4,2)) = 262,144 tuples.
```

For every tuple, compute the direct incidence-rank difference and the
cycle-rank formula. The census must contain every possible quotient dimension
`0..6`.

### Seeded structure and decision cells

Seed `1101101`: 4,096 fresh graph families with:

```text
items in 5..9;
contexts in 2..5;
each simple edge independently admitted by one seeded fair bit.
```

Every cell must check:

- rank difference equals mixed-cycle rank;
- the constructed mixed-cycle basis has exactly that rank;
- every prefix of the basis has its declared independent rank;
- a shared global utility receives the forced or verified status as dictated
  by `q`;
- a locally scalar nongluing witness exists if and only if `q>0` and is
  refuted exactly; and
- when a local cycle exists, a one-edge perturbation returns
  `local_scalar_failed`.

### Minimality controls

One item under as many as six contexts and one context under as many as ten
items must have `q=0`. The two-item/two-context parallel-edge witness must
have `q=1`, remain locally scalar, and refute a shared scalar.

## Gates

- **G0 registration binding:** registration commit, implementation ancestry,
  clean tracked tree, and every sealed hash agree.
- **G1 exact census:** all 262,144 triples execute with zero rank-formula
  mismatches.
- **G2 census liveness:** the census contains quotient dimensions `0..6`,
  including both forced-by-design and live tuples.
- **G3 seeded coverage:** exactly 4,096 fresh cells execute and every
  registered item count and context count occurs.
- **G4 quotient and sharpness:** every fresh rank formula, mixed-basis
  dimension, and prefix-rank sharpness check passes.
- **G5 shared controls:** every shared global utility receives the exact
  forced or verified status dictated by `q`.
- **G6 nongluing controls:** a witness exists exactly when `q>0`, is locally
  scalar, and is rejected by both the mixed-cycle and direct-rank decisions.
- **G7 local-failure and status liveness:** at least one local-cycle
  perturbation executes, all return `local_scalar_failed`, and all four
  registered statuses occur.
- **G8 minimality:** all one-item and one-context controls have `q=0`, while
  the two-item/two-context witness has `q=1` and refutes gluing.
- **G9 resource envelope:** the registered run uses no GPU, finishes within
  360 seconds, and its process peak resident set remains at or below 2 GiB.

All gates passing yields:

```text
finite_contextual_scalar_gluing_geometry_verified
```

## Claim boundary

This is exact finite real-valued graph linear algebra. HodgeRank already
supplies the gradient/cycle decomposition, and local-to-global obstruction is
classical. The result is not ordinal rationalizability, finite-sample
preference estimation, a human or language-model preference theorem,
infinite-history analysis, general revealed preference, or an ASMP-9
resolution.

## Resources

CPU only; 2 GiB process peak resident memory; 360 seconds; no GPU.
