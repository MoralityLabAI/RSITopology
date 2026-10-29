# ASMP-9 bond-design protocol v0.18

## Status and inherited object

This is a prospective, CPU-only structural successor to v0.17. It does not
alter v0.17.

The inherited object is the v0.17 independent Bernoulli comparison graph.
Realized edge counts compress to statuses `Z/I/F`; full conditional-fiber
quotient rank is available exactly when every original nonbridge edge lies on
a directed residual cycle.

The question frozen here is:

> Are the inclusion-minimal boundary supports that destroy full rank exactly
> the bonds of the original graph's cyclic core?

The mathematics and prior-art audit were written before registration.
Development used all connected cyclic simple graphs through four vertices and
one seven-node triangle/square cactus. None of those cells may count as fresh
evidence.

## Fresh registry

The first proposed registry was accidentally executed by the pre-freeze test
suite. Those four cells are explicitly burned in `development_registry` and
cannot support a v0.18 claim.

The replacement scientific registry contains four untouched graphs not
isomorphic to any v0.17 registered/burned graph or any declared v0.18
development cell:

1. the three-dimensional cube, eight vertices and twelve edges;
2. `K_(3,4)`, seven vertices and twelve edges;
3. `K_(2,5)`, seven vertices and ten edges; and
4. a square and hexagon joined by one bridge, ten vertices and eleven edges.

The cube and `K_(3,4)` deliberately have the same edge count and max-min
certificate value while differing in order, cycle rank, and graph structure.

All graph definitions, edge orders, expected bridge sets, rational design
certificates, and resource caps are frozen in `protocol_v0_18.json`.

## Gates

### G0 - registration binding

The runner must revalidate every sealed file hash and the registration hash.
The implementation commit must be an ancestor of the execution commit.

### G1 - fresh graph registry

Every scientific graph must be pairwise nonisomorphic and nonisomorphic to
every v0.17 registered/burned graph and the declared v0.18 development
cactus. Freshness is checked by exact vertex-permutation isomorphism.

### G2 - SCC bad supports equal bonds

For every fresh graph, independently enumerate all `3^|E|` residual status
vectors, identify bad supports using residual strongly connected components,
minimize supports by inclusion, and require exact set equality with bonds
enumerated from connected cut sides.

No cut criterion may be used inside the SCC enumerator.

### G3 - bridge exclusion and cut completeness

For every fresh graph:

- computed bridges equal the frozen bridge list;
- no bond contains an original bridge;
- every nonempty cyclic-core cut contains at least one enumerated bond; and
- every enumerated bond is a cyclic-core cut with connected induced sides.

### G4 - primal/dual cut-design certificates

For every fresh graph, the frozen rational primal weights must:

- be nonnegative and sum to one; and
- give every cyclic-core bond weight at least the frozen threshold.

The frozen rational bond distribution must:

- use only enumerated bonds;
- be nonnegative and sum to one; and
- give every edge inclusion load at most the same threshold.

Primal and dual equality certifies the exact max-min cut-design value.

### G5 - cactus closed form

For the fresh square/hexagon bridge graph:

- the ten nonbridge edges must each lie on exactly one simple cycle;
- the bridge must receive zero weight;
- the computed closed form must be `tau*=2/10=1/5`; and
- its uniform nonbridge allocation must match the frozen primal certificate.

### G6 - structural search reduction

For every fresh graph:

- SCC enumeration examines exactly `3^|E|` status vectors;
- bond enumeration examines at most `2^(|V_H|-1)-1` canonical cuts in each
  cyclic-core component; and
- the two methods return the same minimal support family.

This gate validates the finite structural reduction. Polynomial solvability of
the max-min cut design follows from classical min-cut separation and is
attributed, not claimed as a new algorithm.

### G7 - resource and scope

The run must remain CPU-only and below:

```text
wall time: 180 seconds
peak resident memory: 1 GiB
```

Every output must preserve the frozen claim boundary.

## Decision rule

All eight gates must pass. Any false gate yields:

```text
bond_characterization_not_established
```

A passing run yields:

```text
bond_characterization_established_in_frozen_model
```

No threshold, graph, certificate, or claim boundary may be changed after
registration. A repair requires a versioned successor.

## Claim boundary

Exact identification, on the frozen independent-binomial conditional-access
object inherited from v0.17, of inclusion-minimal full-rank failure supports
with cyclic-core bonds; exact fresh finite SCC-versus-bond checks; classical
max-min cut primal/dual certificates; and an elementary cactus closed form.
Not a novelty claim for bonds, cut design, or fractional packing; not an
arbitrary finite-budget integer theorem, adaptive allocation, dependent or
unknown-link response theorem, downstream power theorem, behavioral
reward-identification theorem, general IRL theorem, or ASMP-9 resolution.
