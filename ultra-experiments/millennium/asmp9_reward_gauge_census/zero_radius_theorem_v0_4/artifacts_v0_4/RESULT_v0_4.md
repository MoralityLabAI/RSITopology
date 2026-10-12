# ASMP-9 exact-tie width theorem verification v0.4

**Verdict:** `sharp_exact_tie_width_theorem_implementation_verified`

## Gates

- **G0_registration_binding:** PASS
- **G1_distinct_exact_signs:** PASS
- **G2_constructed_width_bound:** PASS
- **G3_lower_witness_validity:** PASS
- **G4_lower_witness_sharpness:** PASS
- **G5_fresh_grid_complete:** PASS

## Fresh full-pair cells

| dimension | bound | rays | pairs | theorem width | maximum used | failures |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 9 | 224 | 24976 | 8 | 8 | 0 |
| 2 | 10 | 256 | 32640 | 9 | 9 | 0 |
| 2 | 11 | 336 | 56280 | 10 | 10 | 0 |
| 2 | 12 | 368 | 67528 | 11 | 11 | 0 |
| 2 | 13 | 464 | 107416 | 12 | 12 | 0 |
| 2 | 14 | 512 | 130816 | 13 | 13 | 0 |
| 2 | 15 | 576 | 165600 | 14 | 14 | 0 |
| 2 | 16 | 640 | 204480 | 15 | 15 | 0 |
| 3 | 7 | 2882 | 4151521 | 6 | 6 | 0 |
| 6 | 1 | 728 | 264628 | 1 | 1 | 0 |

## Interpretation

Exact ties reduce the sharp width from `2B-1` under any positive sub-unit
threshold ambiguity to `B-1` for `B>=3`. The proof is a Farey-sequence
corollary; this run checks the constructor and lower witnesses.

## Claim boundary

This verifies a finite cycle-coordinate theorem. It is not finite-sample
preference learning, behavioral IRL, discounted shaping, or a novelty claim.
