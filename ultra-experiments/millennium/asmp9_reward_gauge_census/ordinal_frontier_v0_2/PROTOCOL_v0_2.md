# ASMP-9 ordinal reward-ray access frontier protocol v0.2

## Status

Prospective bounded protocol. No claim-grid output may be read before the
protocol, implementation, tests, verifier, prior-art note, and machine-readable
configuration are committed and hashed in `registration_v0_2.json`.

## Mathematical object

Version 0.1 identifies the potential-shaping quotient with a cycle-return
coordinate `z`. Version 0.2 freezes a finite registry of nonzero integer
coordinates and quotients positive scale:

```text
z ~ c z for c > 0.
```

Each orbit is represented by a primitive integer vector. Opposite vectors are
not equivalent because positive scale does not reverse preference.

A comparison query is a primitive integer normal `q`, canonicalized so its
first nonzero coordinate is positive. It represents the return difference
between two nonnegative trajectory bundles via `q = q_plus - q_minus`.

Without misspecification, the response is:

```text
sign(q dot z) in {-1, 0, +1}.
```

With threshold perturbation radius `delta`, an adversary may replace the score
by `q dot z + e` for any rational `e` in `[-delta, delta]`. A query robustly
separates two rays only when their sets of possible responses are disjoint.
The query family separates the registry only when every pair has at least one
robust separator.

## Frozen registry

Primary strata:

```text
(dimension, reward coordinate bound)
  (1,1), (2,1), (3,1), (2,2)
```

Query coefficient-width caps:

```text
Q in {1,2,3,4}
```

All primitive canonical normals with `||q||_infinity <= Q` are available.

Misspecification radii:

```text
delta in {0, 1/2}.
```

The runner evaluates every cell. For each `(dimension, bound, delta)` stratum,
the registered threshold is the first `Q` with zero unresolved ray pairs. At
that first complete `Q`, a binary set-cover MILP finds the smallest
nonadaptive separating family.

## Frozen hypotheses

- **H1 exact-anchor:** At `delta=0`, coefficient width `Q=1` separates the
  `{−1,0,1}^d \ {0}` registry and the minimum query count equals `d` for
  dimensions 1 through 3.
- **H2 expressivity transition:** Under `delta=1/2`, at least one nontrivial
  stratum is incomplete at `Q=1` but complete by `Q=4`.
- **H3 robust access penalty:** For at least one recovered `delta=1/2`
  stratum, the minimum separating family has more queries than the quotient
  dimension.

H2 and H3 are separable scientific hypotheses. Their failure does not
invalidate the exact census.

## Gates

- **G0 registration binding:** every sealed input matches its registered
  SHA-256; the registration commit contains no result artifact.
- **G1 complete enumeration:** candidate rays and canonical query normals are
  unique, primitive, and exhaustive for the frozen bounds.
- **G2 exact anchor:** H1 passes in all three registered dimensions.
- **G3 robust frontier liveness:** H2 passes.
- **G4 solver validity:** every reported optimum has HiGHS optimal status,
  zero reported MIP gap, objective equal to dual bound within `1e-8`, integral
  selected queries, and an independently replayed full cover.
- **G5 monotonicity:** unresolved-pair count never increases with query width
  and never decreases when `delta` changes from `0` to `1/2` at fixed
  `(dimension,bound,Q)`.
- **G6 robust access penalty:** H3 passes.
- **G7 witness integrity:** every unresolved example is replayed against the
  full admitted query family and every recovered threshold has zero unresolved
  pairs.

Decision:

- G0, G1, G4, G5, and G7 are instrument-validity gates.
- G2 failure yields `exact_anchor_failed`.
- G3 failure yields `robust_width_transition_not_established`.
- G6 failure yields `robust_query_penalty_not_established`.
- Passing all gates yields
  `finite_ordinal_reward_ray_access_frontier_established`.

## Outputs

- `frontier_cells_v0_2.csv`
- `thresholds_v0_2.csv`
- `result_v0_2.json`
- `receipt_v0_2.json`
- `RESULT_v0_2.md`

## Claim boundary

This is a finite, nonadaptive, population-oracle comparison census after the
potential-shaping quotient has already been constructed. It is not a theorem
about arbitrary rewards, noisy human preferences, policies, finite-sample
learning, adaptive query complexity, or discounted MDPs. The perturbation arm
tests robustness to one frozen adversarial threshold model only. The
optimization result is solver-certified finite combinatorics, not a new
hyperplane-tessellation theorem and not an ASMP-9 resolution.

## Resources

CPU only; 4 GiB RAM; 10 minutes total wall time. No GPU.

