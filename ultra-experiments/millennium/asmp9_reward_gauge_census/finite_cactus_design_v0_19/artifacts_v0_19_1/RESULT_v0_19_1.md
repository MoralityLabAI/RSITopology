# ASMP-9 v0.19.1 finite cactus-design result

## Verdict

`finite_budget_cactus_dp_not_established_v0_19_1`

## Gates

- `G0_registration_binding`: **PASS**
- `G1_fresh_registry`: **PASS**
- `G2_cached_engine_reproduces_burned_v0_19`: **PASS**
- `G3_exact_cactus_factorization`: **PASS**
- `G4_bridge_irrelevance_and_floor`: **PASS**
- `G5_dp_equals_independent_exhaustive_totals`: **PASS**
- `G6_dp_equals_all_edge_census`: **PASS**
- `G7_nonconcavity_and_comparator_certificates`: **PASS**
- `G8_fresh_comparator_classification`: **PASS**
- `G9_resource_and_scope`: **FAIL**

## Fresh exact cells

- `fresh_19_1_quad_4_6_8_11`: `1784242466624825025217269721687130112000000/16517976926780506002833800829531584028976727363201`, totals `[[7, 11, 15, 11]]`
- `fresh_19_1_triple_5_7_9`: `832899499959286220891443022811279433333/12234282055380537726133143836491621280514048`, totals `[[5, 10, 18], [8, 7, 18]]`
- `fresh_19_1_triple_7_8_10`: `20496458147796818250853515264000000000000/10842505080063916320800450434338728415281531281`, totals `[[7, 12, 19], [7, 13, 18], [7, 14, 17], [7, 15, 16]]`

The cached integer residual engine first reproduced the complete burned v0.19
factorization-row hash and bridge equalities. On the wholly new cells it then
matched the cycle product exactly.

The fresh full edge census considered
`495` positive labelled
allocations. Its value and induced cycle totals equal the Bellman result; all
optimizers balance inside cycles and leave the bridge at count one.

## Outcome-neutral comparator cells

- `fresh_19_1_equal_six_cycles`: greedy gap `0/1`, global-balance gap `0/1`
- `fresh_19_1_pair_4_5`: greedy gap `310030563468288/168377826559400929`, global-balance gap `0/1`
- `fresh_19_1_pair_6_9`: greedy gap `246171252847443553280000000/4898762930960846817716295277921`, global-balance gap `0/1`

Gap signs were not pass conditions.

## Interpretation

For cactus cyclic cores in the frozen comparison model, finite-budget
availability factors by cycle. Counts balance within cycles, while exact
cycle-total allocation is a classical separable integer dynamic program.
Nonconcavity prevents promoting a one-step greedy rule, and v0.18's
asymptotically uniform allocation remains only asymptotic.

## Claim boundary

Exact finite-budget maximin allocation on cactus cyclic cores inside the frozen independent-binomial, known symmetric-interior, positive-count conditional-access model inherited from ASMP-9 v0.16-v0.18. Version 0.19.1 is a computation-only successor to the v0.19 wall-time failure: it caches graph liveness by ternary residual state and contracts exact integer status numerators, while using wholly new scientific cells. The ASMP-9-specific result is the reduction to a classical series-product integer resource-allocation problem. Dynamic programming, redundancy allocation, and greedy criteria are not claimed as new. This is not an arbitrary-graph every-budget theorem, adaptive allocation theorem, dependent-response theorem, unknown-link theorem, downstream policy-estimation theorem, behavioral reward-identification theorem, general IRL theorem, or ASMP-9 resolution.
