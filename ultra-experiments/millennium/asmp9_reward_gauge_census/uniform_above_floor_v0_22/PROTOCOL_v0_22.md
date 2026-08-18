# ASMP-9 v0.22 protocol: uniform above-floor value complexity

Status: frozen only when the source, protocol, tests, prior-art gate, graph
registry, runners, and environment are committed and hash-bound by
`registration_v0_22.json`.

## Question

Version v0.21 classified exact availability at the forced positive-count
floor.  Version v0.22 asks whether the value-computation barrier survives
when every edge receives more than one comparison.

## Frozen object

On one finite simple biconnected graph, set `epsilon=1/2` and give every edge
the same fixed integer number `r>=2` of independent trials.  With
`z=2^(-r)`, each edge is:

```text
ZERO with probability z
FULL with probability z
INTERIOR with probability 1-2z.
```

For directed-cut liveness, ASMP `INTERIOR` edges and Backman-unoriented edges
play the same role: neither permits a consistently one-way cut.  Backman's
weighted formula therefore gives:

```text
F_G(r)
  = (1-z)^(|V|-1) z^(|E|-|V|+1)
    T_G((1-2z)/(1-z),1/z).
```

For fixed `r`:

```text
x_r = (2^r-2)/(2^r-1)
y_r = 2^r
(x_r-1)(y_r-1) = -1.
```

These are nonexceptional points on the Jaeger-Vertigan-Welsh hard curve
`H_-1`.  The minimal uniform above-floor case `r=2` evaluates `(2/3,4)`.

The dichotomy is stated for general graph evaluation.  Its hardness
localizes to the present block class because the Tutte polynomial is
multiplicative over connected components and vertex-biconnected blocks, while
each bridge contributes the known factor `x_r`.  An oracle for finite simple
biconnected blocks would therefore evaluate an arbitrary simple graph with
polynomially many block queries and rational multiplications.

## Fresh cells

Three full graphs unused in earlier protocols are sealed:

- wheel on six vertices (`m=10`);
- octahedral graph (`m=12`); and
- Wagner graph (`m=12`).

The two six-vertex cells sit outside v0.20's burned graph-atlas envelope
because each has more than nine edges.  No availability or Tutte outcome on
these cells may be read before registration.

Each graph is evaluated at `r in {2,3,5}`.

## Gates

1. `G0_registration_binding`: all source and dependency hashes validate.
2. `G1_freshness_and_structure`: each graph is fresh, pairwise
   nonisomorphic, simple, connected, bridgeless, and biconnected.
3. `G2_state_law_and_semantics`: every registered `r` has exact law
   `(z,1-2z,z)` summing to one, and the implementation's live predicate is
   strong connectivity of the induced directed/bidirected graph.
4. `G3_weighted_tutte_identity`: direct ternary-status enumeration equals
   the Backman/Tutte formula in all nine graph/count cells.
5. `G4_hard_curve_and_fixed_points`: every exact point satisfies
   `(x-1)(y-1)=-1`; `r=2` is exactly `(2/3,4)`; no registered point is one of
   the Jaeger-Vertigan-Welsh exceptions.
6. `G5_minimal_above_floor_microtrial`: direct enumeration of all
   `2^(2|E|)` fair trial matrices on the wheel equals both exact routes.
7. `G6_endpoint_label_invariance`: the inherited exact ternary evaluator
   agrees for all-zero, all-one, and alternating labels on the `r=2` wheel.
8. `G7_exact_numerator_ledger`: every availability multiplied by
   `2^(r|E|)` is a nonnegative integer, matching a finite #P witness count.
9. `G8_complexity_attribution`: only the allowed prior-art-derived
   classification is emitted.
10. `G9_resource_and_scope`: CPU-only execution remains under 180 seconds
    and 1 GiB, matches the sealed Python/platform/NetworkX environment, and
    emits the full claim boundary.

## Independent verification

The primary implementation uses a spanning-subgraph Tutte evaluation and
direct ternary-status enumeration.  The independent verifier imports neither
it nor the runner; it uses multigraph-safe deletion-contraction at the
registered rational points and separately repeats the `r=2` microtrial
control.

## Claim boundary

Passing v0.22 classifies exact evaluation of a declared uniform allocation.
It does not show that allocation is optimal or classify maximin design,
nonuniform counts, arbitrary response probabilities, approximation,
adaptive allocation, dependence, misspecification, behavioral reward
identification, general inverse reinforcement learning, or ASMP-9.
