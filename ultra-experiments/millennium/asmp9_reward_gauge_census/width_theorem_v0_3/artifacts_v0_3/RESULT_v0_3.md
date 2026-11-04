# ASMP-9 sharp query-width theorem verification v0.3

**Verdict:** `sharp_query_width_theorem_implementation_verified`

## Gates

- **G0_registration_binding:** PASS
- **G1_strict_opposite_scores:** PASS
- **G2_constructed_width_bound:** PASS
- **G3_lower_witness_validity:** PASS
- **G4_lower_witness_sharpness:** PASS
- **G5_disjoint_grid_complete:** PASS

## Disjoint full-pair verification

| dimension | bound | rays | pairs | theorem width | maximum used | failures |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 17 | 768 | 294528 | 33 | 33 | 0 |
| 2 | 18 | 816 | 332520 | 35 | 35 | 0 |
| 2 | 19 | 960 | 460320 | 37 | 37 | 0 |
| 2 | 20 | 1024 | 523776 | 39 | 39 | 0 |
| 2 | 21 | 1120 | 626640 | 41 | 41 | 0 |
| 2 | 22 | 1200 | 719400 | 43 | 43 | 0 |
| 2 | 23 | 1376 | 946000 | 45 | 45 | 0 |
| 2 | 24 | 1440 | 1036080 | 47 | 47 | 0 |
| 3 | 5 | 1154 | 665281 | 9 | 9 | 0 |
| 4 | 3 | 2240 | 2507680 | 5 | 5 | 0 |

The full claim grid was disjoint from the construction-development grid. The
lower-witness search separately exhausted every narrower two-dimensional
integer query for bounds 33 through 64. High-dimensional seeded checks covered
4096 distinct pairs in each of dimensions 5, 8, and 16.

## Claim boundary

This verifies the implementation and extremal witnesses for the written sharp
finite-lattice theorem. The proof, not the census, carries the theorem. It does
not establish novelty or solve reward recovery from behavior, discounted
shaping, finite-sample preference learning, or inconsistent-demonstrator
identifiability.
