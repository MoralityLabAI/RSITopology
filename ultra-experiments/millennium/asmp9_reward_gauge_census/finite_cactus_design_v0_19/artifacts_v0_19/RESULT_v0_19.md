# ASMP-9 v0.19 finite cactus-design result

## Verdict

`finite_budget_cactus_dp_not_established`

## Gates

- `G0_registration_binding`: **PASS**
- `G1_fresh_registry`: **PASS**
- `G2_exact_cactus_factorization`: **PASS**
- `G3_bridge_irrelevance_and_floor`: **PASS**
- `G4_dp_equals_independent_exhaustive_totals`: **PASS**
- `G5_dp_equals_all_edge_census`: **PASS**
- `G6_nonconcavity_and_comparator_certificates`: **PASS**
- `G7_fresh_comparator_classification`: **PASS**
- `G8_resource_and_scope`: **FAIL**

## Exact finite-budget cells

- `fresh_quad_4_7_9_10`: value `714410158221023058504117451348325360107421875/4387973218983880062613640699796470064178461935665152`, totals `[[7, 7, 10, 20], [7, 8, 9, 20]]`
- `fresh_triple_5_6_8`: value `36369625460969034269214113792/284075643307976424694061279296875`, totals `[[5, 10, 15], [5, 11, 14]]`
- `fresh_triple_6_7_11`: value `275216350330873001959622361245169/464861112684148108864643443379413188608`, totals `[[7, 7, 22]]`

The full positive edge-allocation census evaluated
`330` allocations. Its exact value
and optimizer-induced cycle totals match the Bellman recursion, every
optimizer leaves the bridge at its mandatory floor, and every cycle is
internally balanced.

## Fresh comparator classifications

- `fresh_equal_four_cycles`: greedy gap `0/1`, globally-balanced gap `0/1`
- `fresh_equal_three_cycle_blocks`: greedy gap `0/1`, globally-balanced gap `0/1`
- `fresh_unequal_cycle_pair`: greedy gap `0/1`, globally-balanced gap `0/1`

These gap signs were not gate directions. The gate required exact,
independently reproduced classifications.

## Interpretation

On a cactus cyclic core, full conditional quotient availability is a series
product of independent cycle-block availabilities. The finite design problem
therefore separates into balanced within-cycle counts and an exact integer
allocation over cycle totals.

That outer allocation is not licensed for one-step greedy optimization:
`log f_k(N)` lacks discrete concavity. Nor can v0.18's asymptotically uniform
cyclic-edge design be promoted to an every-budget rule. The exact finite
replacement is the registered Bellman recurrence.

Dynamic programming and reliability allocation are classical. The
ASMP-9-specific result is the reduction from conditional comparison-fiber
liveness to that classical object.

## Claim boundary

Exact finite-budget maximin allocation on cactus cyclic cores inside the frozen independent-binomial, known symmetric-interior, positive-count conditional-access model inherited from ASMP-9 v0.16-v0.18. The ASMP-9-specific result is the reduction to a classical series-product integer resource-allocation problem. Dynamic programming, redundancy allocation, and greedy criteria are not claimed as new. This is not an arbitrary-graph every-budget theorem, adaptive allocation theorem, dependent-response theorem, unknown-link theorem, downstream policy-estimation theorem, behavioral reward-identification theorem, general IRL theorem, or ASMP-9 resolution.
