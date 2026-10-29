# ASMP-9 v0.21 protocol: count-floor local-block complexity

Status: frozen only when its source, machine-readable form, runners, tests,
prior-art gate, burned-graph registry, and environment are committed and
hash-bound by `registration_v0_21.json`.

## Question

Version v0.20 proved that exact availability factors over vertex-biconnected
blocks, leaving the exact local finite-design problem inside one
overlapping-cycle block unclassified.  Version v0.21 asks a deliberately
narrow first complexity question:

> What is the complexity of computing the exact value at the positive-count
> floor under the maximally noisy known response channel?

## Frozen boundary

For one finite simple biconnected graph `G=(V,E)`, freeze

```text
epsilon = 1/2
N = |E|
n_e >= 1.
```

The positive allocation is uniquely `n_e=1`.  Every edge becomes one fair
binary orientation, independent of its endpoint label.  Quotient liveness is
total cyclicity, so the registered identity is

```text
F_G = T_G(0,2) / 2^|E|.
```

## Complexity conclusion

The mathematical conclusion is a corollary of classical work, not an
experimental discovery:

- Las Vergnas supplies the totally-cyclic-orientation interpretation of
  `T_G(0,2)`;
- Jaeger, Vertigan, and Welsh make `(0,2)` #P-hard for graphic matroids under
  polynomial-time Turing reductions; and
- the count is in #P because an orientation is a binary witness and directed
  reachability checks total cyclicity in polynomial time.

Thus the numerator is #P-complete and the exact rational value is #P-hard
under that reduction convention.  Hardness localizes to biconnected blocks:
graphs with bridges have zero totally cyclic orientations; bridgeless graphs
decompose into polynomially many biconnected blocks whose counts multiply.

The phrase “optimization is #P-complete” is prohibited.  At `N=|E|`,
optimizer search is trivial; only exact value computation is hard.

## Fresh confirmatory cells

Four previously unused biconnected graphs are sealed:

- wheel on seven vertices;
- Petersen graph;
- pentagonal prism; and
- a `K4` whose three edges incident to one vertex are subdivided.

No count, availability, or orientation outcome from these cells may be read
before registration.  The exact-isomorphism freshness check is against every
graph-shaped object in earlier ASMP-9 machine-readable protocols.

Two controls are also sealed:

- the wheel plus one leaf bridge, which must separate classical total
  cyclicity from the bridge-quotiented ASMP event; and
- the wheel one-point-unioned with a pentagon, which must reproduce the
  block product.

## Gates

1. `G0_registration_binding`: every sealed hash and the clean committed source
   state validate before outcome computation.
2. `G1_freshness_and_structure`: all primary graphs are fresh, pairwise
   nonisomorphic, simple, connected, and one nontrivial biconnected block.
   Controls have their registered block/bridge structure.
3. `G2_tutte_exhaustive_equality`: deletion-contraction `T_G(0,2)` equals
   explicit total-orientation enumeration on all four primary cells.
4. `G3_asmp_boundary_identity`: an independent ASMP quotient-liveness count
   equals the same integer on every primary cell.
5. `G4_normalization_and_label_invariance`: availability equals the count
   divided by `2^|E|`; on the smallest primary cell, the inherited exact
   ternary-status evaluator agrees for all-zero, all-one, and alternating
   endpoint labels.
6. `G5_unique_count_floor_design_value`: exhaustive positive-composition
   accounting finds exactly one allocation at `N=|E|`, and its exact maximin
   value is the registered availability.
7. `G6_bridge_scope_control`: the bridge control has `T_G(0,2)=0`, while ASMP
   quotient availability equals the wheel availability because the bridge is
   ignored and its two directions cancel in the normalization.
8. `G7_block_product_and_localization`: the two-block control agrees across
   direct Tutte evaluation, exhaustive orientations, ASMP counting, and the
   product of the two block counts.  The result records the polynomial
   biconnected-oracle reduction.
9. `G8_complexity_attribution`: result wording uses only the allowed
   classification and preserves all classical attributions and forbidden
   claims.
10. `G9_resource_and_scope`: CPU-only execution stays below 180 seconds and
    1 GiB peak resident memory and emits the frozen claim boundary.

## Independent verification

The main implementation uses deletion-contraction plus explicit
orientation/ASMP enumerators.  The independent verifier imports neither the
implementation nor the runner.  It recomputes `T_G(0,2)` from the spanning
subgraph expansion and separately enumerates orientations.

Finite agreement challenges the translation and implementation.  It is not
the proof of #P-hardness.

## Claim boundary

Passing v0.21 classifies exact value computation at one frozen boundary of
the v0.20 local problem.  It does not classify optimizer search, budgets above
the edge count, arbitrary response interiors, partial-orientation weighting,
approximation, the complete parameterized problem, adaptive allocation,
dependence, contamination, strategic response, behavioral reward
identification, general inverse reinforcement learning, or ASMP-9.

