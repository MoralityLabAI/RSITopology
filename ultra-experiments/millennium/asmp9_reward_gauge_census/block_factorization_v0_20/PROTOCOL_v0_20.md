# ASMP-9 block-factorization protocol v0.20

Status: implementation freeze candidate. Do not run the registered cells
until this document, the machine-readable protocol, implementation, tests,
and verifier are committed and a separate registration file binds their
hashes.

## Question

Does the finite residual-liveness object from ASMP-9 v0.17-v0.19 factor
exactly over arbitrary vertex-biconnected blocks, not merely over cactus
cycles?

## Frozen object

For each original comparison edge, repeated independent Bernoulli outcomes
produce one of three residual statuses:

```text
ZERO      only the registered forward residual direction survives
INTERIOR  both directions survive
FULL      only the reverse direction survives
```

Original bridges are outside the quotient. Full quotient liveness means that
the endpoints of every original nonbridge edge are mutually reachable in the
residual digraph.

The endpoint-label adversary assigns one bit independently to every edge. At
the declared symmetric interior `epsilon`, the bit selects Bernoulli
probability `epsilon` or `1-epsilon`.

## Statements under test

### T1. Deterministic block equivalence

For every ternary residual status vector:

```text
full quotient liveness
iff
every nontrivial vertex-biconnected edge block is residual-strongly-connected.
```

The proof uses the block-cut forest. A path that leaves one block and first
returns to it must return at the same articulation vertex; otherwise the
outside subpath and an inside path create a cycle spanning two blocks.
Deleting such excursions projects global paths into the block.

### T2. Exact product

Under independent edge responses:

```text
F_G(n, labels) = product_B F_B(n_B, labels_B).
```

Because the label universe is rectangular over disjoint block edge sets:

```text
min_labels F_G(n, labels)
  = product_B min_(labels_B) F_B(n_B, labels_B).
```

### T3. Exact between-block allocation

Let `f_B(t)` be the exact local maximin availability of block `B` with `t`
positive integer trials. Once these tables are supplied, the global optimum
is the exact Bellman product recursion over block totals. The protocol makes
no claim that the local table of a general overlapping-cycle block can be
computed efficiently.

## Fresh cells

All full registered graphs have at least seven vertices and lie outside the
burned NetworkX atlas census. The protocol includes:

- a diamond block with attachments at two different articulation vertices;
- a theta block separated from a triangle by a bridge;
- cyclic components separated by two bridges;
- a chorded seven-cycle as a genuinely overlapping-cycle one-block control;
- a chorded seven-cycle joined to a triangle for exact allocation; and
- a triangle joined to a pentagon for complete rectangular-label checking.

Sub-block reuse inside this single sealed protocol is allowed and reported.
No full graph from the development registry is reused.

## Gates

1. `G0_registration_binding`: every sealed source, protocol, prior-art,
   dependency, and evaluator hash matches the immutable registration.
2. `G1_fresh_graph_registry`: all graph signatures are unique, every graph
   has at least seven vertices, and no burned full graph is reused.
3. `G2_block_partition`: Tarjan blocks equal an independent brute simple-cycle
   union decomposition and the frozen expected partitions.
4. `G3_exhaustive_status_equivalence`: direct liveness, implementation
   blockwise liveness, and an independent block oracle agree on every
   registered ternary status.
5. `G4_fixed_label_probability_product`: direct exact rational availability
   equals the product of local block availabilities in every fixed-label cell.
6. `G5_rectangular_worst_label_product`: complete global endpoint-label
   enumeration equals the product of independently minimized block factors.
7. `G6_bridge_irrelevance`: changing only bridge counts, labels, and statuses
   never changes the registered liveness or exact availability.
8. `G7_bellman_equals_full_edge_census`: Bellman recursion and a complete
   positive edge-allocation census return exactly the same value and optimizer
   set.
9. `G8_one_block_negative_control`: the chorded cycle has exactly one
   nontrivial block; product evaluation equals direct evaluation but yields no
   within-block decomposition or claimed computational gain.
10. `G9_resource_and_scope`: CPU-only, no GPU use, at most 180 wall seconds
    and 1 GiB peak resident memory; the result reproduces the frozen claim
    boundary exactly.

Every gate is binding. A resource failure remains a negative registered
outcome even if every mathematical equality holds. The evaluator has no
positive-outcome assumption.

## Claim boundary

The exact claim boundary is stored in `protocol_v0_20.json` and must be copied
byte-for-byte into the result.

This version can establish only an exact decomposition and between-block
allocation theorem for the frozen independent-binomial conditional-access
model. Classical block decomposition, reliability multiplication, and
Bellman allocation are prior art. Arbitrary within-block design complexity,
adaptive sampling, response dependence, link misspecification, behavioral
validity, downstream utility, general IRL, and full ASMP-9 resolution remain
open.
