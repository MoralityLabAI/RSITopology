# ASMP-9 robust contextual scalar-gluing protocol v0.12

## Status

Prospective protocol. The 4,096-pair four-item census and seed-12 unit cells are
burned development evidence. They cannot satisfy the fresh-cell gates.

## Frozen statements

1. For the nested shared-scalar and context-local-scalar subspaces, the
   Euclidean residual decomposes orthogonally into within-context
   non-scalarity and cross-context non-gluing.
2. Distance to the shared-scalar subspace is the exact minimum Euclidean
   repair radius.
3. A `d`-dimensional gluing quotient needs at least `d` independent linear
   queries.
4. Among `d` square queries with row norms at most one, an orthonormal basis
   uniquely attains worst-case amplification one.
5. The frozen six-edge graph is an exact counterexample to the claim that
   minimum-total-support simple mixed cycles minimize noise amplification.

The theorem and proofs are in `THEOREM_v0_12.md`.

## Frozen exact witness

The burned four-item/two-context graph has obstruction dimension two. Its
minimum-support design has:

```text
amplification^2 = 3/2,
```

while the eight-support orthonormal design has:

```text
amplification^2 = 1.
```

`exact_certificate.py` must reproduce both rational Gram matrices.

## Fresh registry

Use seed `1201201` to draw 512 cells. Every cell has:

- five labelled items;
- two contexts;
- exactly four distinct simple edges sampled uniformly without replacement in
  each context; and
- eight context-labelled edge observations total.

The frozen float64 tolerance is `1e-8`. Expected obstruction dimensions are
exactly `{2,3,4}`. The fresh registry must not be run before the implementation
and protocol are hash-sealed.

## Gates

- **G0 registration binding:** registration commit is HEAD, tracked tree is
  clean, implementation commit is an ancestor, and every sealed hash matches.
- **G1 exact counterexample:** the rational certificate matches every frozen
  rank, Gram, support, and amplification value.
- **G2 nested geometry:** zero dimension, Pythagorean, shared-control, and
  local-projection mismatches.
- **G3 exact repair radius:** projection distance matches direct least-squares
  residual in every fresh cell.
- **G4 query-count lower bound:** every constructed `d-1`-query design is rank
  deficient and has zero smallest singular value.
- **G5 orthonormal optimum:** every orthonormal control has amplification one
  and every square row-normalized random design has `sigma_min <= 1`.
- **G6 fresh coverage:** all 512 cells run and dimensions `{2,3,4}` all occur.
- **G7 simple-cycle basis:** every fresh quotient is spanned by admissible
  simple mixed-cycle queries.
- **G8 conditioning-separation liveness:** at least one fresh cell has a
  shortest-support basis with strictly worse conditioning than the E-optimal
  simple-cycle design. This is a liveness gate, not an effect-size claim.
- **G9 resource envelope:** CPU only, no more than 120 seconds and 2 GiB peak
  resident memory.

All passing yields:

```text
robust_context_gluing_geometry_verified_v0_12
```

## Claim boundary

The mathematical statements are classical finite Euclidean projection and
singular-value facts specialized to the v0.11 access grammar. The finite graph
counterexample and fresh census are synthetic.

The result cannot establish stochastic coverage, infer latent contexts, choose
the correct norm, show that a human or model has scalar preferences, recover a
reward from behavior, or resolve ASMP-9.
