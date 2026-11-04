# ASMP-9 finite cactus-design result v0.19.2

## Verdict

```text
finite_budget_cactus_dp_established_in_frozen_model_v0_19_2
```

## Gates

- `G0_registration_binding`: **PASS**
- `G1_fresh_registry`: **PASS**
- `G2_cached_cycle_engine_reproduces_burned_v0_19_1`: **PASS**
- `G3_exact_cactus_factorization`: **PASS**
- `G4_bridge_irrelevance_and_floor`: **PASS**
- `G5_dp_equals_cached_independent_exhaustive_totals`: **PASS**
- `G6_dp_equals_all_edge_census`: **PASS**
- `G7_nonconcavity_and_comparator_certificates`: **PASS**
- `G8_fresh_comparator_classification`: **PASS**
- `G9_resource_and_scope`: **PASS**

## Exact finite allocations

- `fresh_19_2_quad_5_8_10_12`: `133496652361611450330010315975129549415914877747200000/35370553733215749514562618584237555997034634776827523327290883`, totals `[[5, 9, 11, 23], [5, 9, 13, 21], [5, 9, 17, 17], [5, 9, 19, 15], [5, 11, 11, 21], [5, 11, 15, 17], [5, 11, 17, 15], [5, 11, 19, 13], [5, 13, 13, 17], [5, 13, 15, 15], [5, 13, 17, 13], [5, 15, 11, 17], [5, 15, 13, 15], [5, 15, 15, 13]]`
- `fresh_19_2_triple_4_7_10`: `55553714877639234763248790192979932483155/950861228634244120709413908010198374010585088`, totals `[[7, 7, 20]]`
- `fresh_19_2_triple_6_9_11`: `4523065407059473964391925549763528707182428160/5567468501746134532846058029734065138452687762629169`, totals `[[8, 9, 22]]`

The memoized checker still exhausted every feasible vector of cycle totals
and every endpoint-label assignment needed for each distinct one-cycle
value. It only removed duplicate evaluation of the same local value.

## Full edge census

The fresh labelled all-edge census evaluated
`330` positive allocations.
Its value and complete induced optimizer-total set matched Bellman; every
optimizer balanced counts within each cycle and left bridges at count one.

## Outcome-neutral comparators

- `fresh_19_2_equal_seven_cycles`: greedy gap `0/1`, global-balance gap `0/1`
- `fresh_19_2_pair_5_7`: greedy gap `0/1`, global-balance gap `0/1`
- `fresh_19_2_pair_8_11`: greedy gap `343289123313566807313790374519763891/87912465665148309976831907175499110023168`, global-balance gap `0/1`

Comparator gap signs were not gates.

## Resources

- elapsed: `50.568574` seconds
- peak resident memory: `24293376` bytes
- GPU used: `False`

## Claim boundary

Exact finite-budget maximin allocation on cactus cyclic cores inside the frozen independent-binomial, known symmetric-interior, positive-count conditional-access model inherited from ASMP-9 v0.16-v0.18. Version 0.19.2 is a computation-only successor to the v0.19 and v0.19.1 wall-time failures. It preserves complete independent endpoint-label and cycle-total enumeration but memoizes the repeated one-cycle minima diagnosed after v0.19.1. All scientific cells are new and the 180-second cap is unchanged. The ASMP-9-specific result is the reduction to a classical series-product integer resource-allocation problem. Dynamic programming, redundancy allocation, and greedy criteria are not claimed as new. This is not an arbitrary-graph every-budget theorem, adaptive allocation theorem, dependent-response theorem, unknown-link theorem, downstream policy-estimation theorem, behavioral reward-identification theorem, general IRL theorem, or ASMP-9 resolution.
