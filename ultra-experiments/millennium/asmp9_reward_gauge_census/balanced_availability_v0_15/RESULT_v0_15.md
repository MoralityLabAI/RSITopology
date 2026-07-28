# ASMP-9 sharp interior availability v0.15 result

## Verdict

`registered_exact_result_passed`

All quantities are exact rationals; decimals are display aids.

## Gates

- `G0_registration_binding`: **PASS**
- `G1_registry_completeness`: **PASS**
- `G2_exact_minimax_formula`: **PASS**
- `G3_balanced_endpoint_witness`: **PASS**
- `G4_bound_and_drift_controls`: **PASS**
- `G5_exact_trial_threshold`: **PASS**
- `G6_zero_interior_control`: **PASS**
- `G7_finite_allocation_falsification`: **PASS**
- `G8_resource_and_scope`: **PASS**

## Fresh exact registry

- theorem cells: 36
- threshold cells: 48
- zero-interior controls: 6
- unequal-allocation cells: 32

## Exact threshold table

| cycle length | epsilon | target availability | minimum trials/edge |
| ---: | ---: | ---: | ---: |
| 11 | 1/16 | 0.995000 | 67 |
| 11 | 1/16 | 0.975000 | 54 |
| 11 | 1/16 | 0.937500 | 47 |
| 11 | 1/16 | 0.875000 | 40 |
| 11 | 3/20 | 0.995000 | 27 |
| 11 | 3/20 | 0.975000 | 22 |
| 11 | 3/20 | 0.937500 | 19 |
| 11 | 3/20 | 0.875000 | 16 |
| 11 | 3/10 | 0.995000 | 13 |
| 11 | 3/10 | 0.975000 | 10 |
| 11 | 3/10 | 0.937500 | 9 |
| 11 | 3/10 | 0.875000 | 8 |
| 11 | 7/20 | 0.995000 | 11 |
| 11 | 7/20 | 0.975000 | 9 |
| 11 | 7/20 | 0.937500 | 7 |
| 11 | 7/20 | 0.875000 | 7 |
| 13 | 1/16 | 0.995000 | 70 |
| 13 | 1/16 | 0.975000 | 57 |
| 13 | 1/16 | 0.937500 | 49 |
| 13 | 1/16 | 0.875000 | 43 |
| 13 | 3/20 | 0.995000 | 28 |
| 13 | 3/20 | 0.975000 | 23 |
| 13 | 3/20 | 0.937500 | 20 |
| 13 | 3/20 | 0.875000 | 17 |
| 13 | 3/10 | 0.995000 | 13 |
| 13 | 3/10 | 0.975000 | 11 |
| 13 | 3/10 | 0.937500 | 9 |
| 13 | 3/10 | 0.875000 | 8 |
| 13 | 7/20 | 0.995000 | 11 |
| 13 | 7/20 | 0.975000 | 9 |
| 13 | 7/20 | 0.937500 | 8 |
| 13 | 7/20 | 0.875000 | 7 |
| 16 | 1/16 | 0.995000 | 73 |
| 16 | 1/16 | 0.975000 | 60 |
| 16 | 1/16 | 0.937500 | 52 |
| 16 | 1/16 | 0.875000 | 46 |
| 16 | 3/20 | 0.995000 | 29 |
| 16 | 3/20 | 0.975000 | 24 |
| 16 | 3/20 | 0.937500 | 21 |
| 16 | 3/20 | 0.875000 | 19 |
| 16 | 3/10 | 0.995000 | 14 |
| 16 | 3/10 | 0.975000 | 11 |
| 16 | 3/10 | 0.937500 | 10 |
| 16 | 3/10 | 0.875000 | 9 |
| 16 | 7/20 | 0.995000 | 11 |
| 16 | 7/20 | 0.975000 | 9 |
| 16 | 7/20 | 0.937500 | 8 |
| 16 | 7/20 | 0.875000 | 7 |

## Unequal allocation

Balanced integer allocation was an optimizer in
32 of
32 fresh finite cells.

This is a finite falsification result only. It does not prove that balanced
allocation is optimal for arbitrary cycle length, interior, or total budget.

## Resources

- elapsed seconds: 2.780078
- peak resident bytes: 20938752
- GPU used: false

## Claim boundary

Fresh exact verification of the equal-count minimax identity and threshold, plus a finite unequal-allocation falsification registry; not a general allocation theorem, behavioral result, general IRL result, or ASMP-9 resolution.
