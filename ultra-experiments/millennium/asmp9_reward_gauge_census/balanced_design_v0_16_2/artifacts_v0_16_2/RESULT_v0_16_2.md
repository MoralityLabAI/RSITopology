# ASMP-9 balanced maximin design v0.16.2 result

## Verdict

`registered_exact_result_passed`

## Gates

- `G0_registration_binding`: **PASS**
- `G1_registry_completeness`: **PASS**
- `G2_pair_reduction`: **PASS**
- `G3_same_branch_smoothing`: **PASS**
- `G4_opposite_branch_smoothing`: **PASS**
- `G5_global_balanced_optimum`: **PASS**
- `G6_compact_value_formula`: **PASS**
- `G7_total_budget_threshold`: **PASS**
- `G8_negative_boundaries`: **PASS**
- `G9_resource_and_scope`: **PASS**

## Fresh exact cells

- pairwise games: 504
- global allocation cells: 16
- compact-value cells: 12
- total-budget thresholds: 36
- negative-boundary cells: 6

All quantities are exact rational values. Decimals are display aids.

## Exact total-budget thresholds

| `k` | `epsilon` | target | minimum total trials |
| ---: | ---: | ---: | ---: |
| 11 | 1/30 | 0.979167 | 1160 |
| 11 | 1/30 | 0.994792 | 1396 |
| 11 | 1/30 | 0.998698 | 1626 |
| 11 | 7/30 | 0.979167 | 149 |
| 11 | 7/30 | 0.994792 | 179 |
| 11 | 7/30 | 0.998698 | 208 |
| 11 | 11/30 | 0.979167 | 87 |
| 11 | 11/30 | 0.994792 | 105 |
| 11 | 11/30 | 0.998698 | 121 |
| 11 | 7/15 | 0.979167 | 69 |
| 11 | 7/15 | 0.994792 | 81 |
| 11 | 7/15 | 0.998698 | 93 |
| 16 | 1/30 | 0.979167 | 1864 |
| 16 | 1/30 | 0.994792 | 2207 |
| 16 | 1/30 | 0.998698 | 2542 |
| 16 | 7/30 | 0.979167 | 238 |
| 16 | 7/30 | 0.994792 | 283 |
| 16 | 7/30 | 0.998698 | 325 |
| 16 | 11/30 | 0.979167 | 140 |
| 16 | 11/30 | 0.994792 | 165 |
| 16 | 11/30 | 0.998698 | 190 |
| 16 | 7/15 | 0.979167 | 110 |
| 16 | 7/15 | 0.994792 | 127 |
| 16 | 7/15 | 0.998698 | 144 |
| 19 | 1/30 | 0.979167 | 2308 |
| 19 | 1/30 | 0.994792 | 2716 |
| 19 | 1/30 | 0.998698 | 3114 |
| 19 | 7/30 | 0.979167 | 296 |
| 19 | 7/30 | 0.994792 | 348 |
| 19 | 7/30 | 0.998698 | 398 |
| 19 | 11/30 | 0.979167 | 172 |
| 19 | 11/30 | 0.994792 | 203 |
| 19 | 11/30 | 0.998698 | 232 |
| 19 | 7/15 | 0.979167 | 134 |
| 19 | 7/15 | 0.994792 | 156 |
| 19 | 7/15 | 0.998698 | 177 |

## Interpretation

Counts differing by at most one were the unique maximin allocation up to edge
permutation in every fresh global cell. More importantly, the registered
pairwise identities verify the analytic Robin-Hood proof rather than inferring
the theorem from this census.

## Resources

- elapsed seconds: 41.790217
- peak resident bytes: 25538560
- GPU used: false

## Claim boundary

Fresh exact verification of the balanced integer maximin theorem, compact optimal value, and logarithmically searched total-budget threshold for one independent Bernoulli cycle experiment; not adaptive allocation, multi-cycle optimal design, behavioral validation, a general RL rollout policy, general IRL identifiability, or ASMP-9 resolution.

## Threshold-search implementation

The 36 exact thresholds used exponential bracketing plus binary search, with 495 exact value evaluations in total. The largest selected total was 3114.
