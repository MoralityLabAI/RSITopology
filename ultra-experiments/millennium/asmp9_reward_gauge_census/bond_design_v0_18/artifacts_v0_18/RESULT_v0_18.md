# ASMP-9 v0.18 bond-design result

## Verdict

`bond_characterization_established_in_frozen_model`

## Gates

- `G0_registration_binding`: **PASS**
- `G1_fresh_graph_registry`: **PASS**
- `G2_scc_bad_supports_equal_bonds`: **PASS**
- `G3_bridge_exclusion_and_cut_completeness`: **PASS**
- `G4_primal_dual_cut_design_certificates`: **PASS**
- `G5_cactus_closed_form`: **PASS**
- `G6_structural_search_reduction`: **PASS**
- `G7_resource_and_scope`: **PASS**

## Fresh exact cells

- `cactus_square_hexagon_bridge`: 21 bonds, 177147 SCC states, `tau*=1/5`
- `complete_bipartite_2_5`: 37 bonds, 59049 SCC states, `tau*=1/5`
- `complete_bipartite_3_4`: 49 bonds, 531441 SCC states, `tau*=1/4`
- `cube`: 63 bonds, 531441 SCC states, `tau*=1/4`

Across all fresh cells, the inclusion-minimal supports found by direct
ternary residual-SCC enumeration equal the bonds of the cyclic core exactly.
The frozen rational primal and dual certificates agree in every cell.

The cactus control returns `tau*=1/5`, uniform weight on its ten cyclic
edges, and zero weight on its bridge.

## Interpretation

The v0.17 bad-support hypergraph is not an arbitrary reliability object. In
the frozen conditional-access model it is exactly the bond clutter of the
cyclic core. Consequently its leading allocation exponent is the classical
problem of allocating edge capacity to maximize the minimum relevant cut.

This removes ternary-status enumeration from the structural characterization.
The cut-design optimization and its polynomial solvability are classical and
are not claimed as new.

## Claim boundary

Exact identification, on the frozen independent-binomial conditional-access object inherited from v0.17, of inclusion-minimal full-rank failure supports with cyclic-core bonds; exact fresh finite SCC-versus-bond checks; classical max-min cut primal/dual certificates; and an elementary cactus closed form. Not a novelty claim for bonds, cut design, or fractional packing; not an arbitrary finite-budget integer theorem, adaptive allocation, dependent or unknown-link response theorem, downstream power theorem, behavioral reward-identification theorem, general IRL theorem, or ASMP-9 resolution.
