# ASMP-9 v0.18 development note

Status: burned design evidence; not claim-eligible.

## Structural conjecture

The v0.17 inclusion-minimal bad boundary supports appear to be exactly the
bonds of the graph obtained after deleting original bridges, component by
component.

The proof route is through residual directed cuts:

1. full v0.17 liveness is strong connectivity on each cyclic-core component;
2. failure of strong connectivity exposes a one-way cut;
3. all edges of that cut must be boundary edges because an interior edge is
   bidirected; and
4. inclusion-minimizing such supports yields bonds.

The draft proof is in `FORMULATION_DRAFT_v0_18.md`.

## Burned finite checks

`development_check.py` compared:

- direct v0.17 ternary residual-SCC support minimization; and
- independent enumeration of bonds from connected cut sides.

It covered every connected cyclic labelled simple graph through four
vertices:

```text
order 3:  1 graph
order 4: 22 graphs
total:   23 graphs
mismatches: 0
```

The extra burned cactus consists of a triangle and square joined by a bridge.
Its nonbridge bond family equals the union of all edge pairs within each
cycle, and the closed form returns:

```text
tau*=2/7
cyclic-edge weights=1/7
bridge weight=0.
```

## Pre-freeze registry mistake

The first proposed fresh registry contained:

- triangular prism;
- `K_(3,3)`;
- `K_(2,4)`; and
- a triangle/pentagon bridge cactus.

The initial pre-freeze tests executed the SCC-versus-bond and certificate
checks on those cells. They were therefore observed before registration and
cannot be used as fresh v0.18 evidence. They remain explicitly listed under
`development_registry.premature_v0_18_cells` in the protocol.

The replacement scientific registry is untouched by pre-freeze tests:

- cube;
- `K_(3,4)`;
- `K_(2,5)`; and
- a square/hexagon bridge cactus.

The tests now validate only the schema and burned development instruments.
Scientific gates execute only after the protocol and implementation commit
are registered.

## Prior-art conclusion

The graph-design objective is classical. Fulkerson's 1959 capacity-budget
problem, Juttner's budgeted-optimization framework, and
Chakrabarty-Mehta-Vazirani's design framework rule out a novelty claim for
max-min cut allocation or its polynomial solvability.

The surviving contribution is the exact identification of the v0.17
conditional-access bad-support hypergraph with the cyclic-core bond clutter.
