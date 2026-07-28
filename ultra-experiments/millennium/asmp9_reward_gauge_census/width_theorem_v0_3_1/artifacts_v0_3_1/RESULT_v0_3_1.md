# Corrected ASMP-9 sharp-width verification v0.3.1

**Verdict:** `corrected_sharp_query_width_theorem_implementation_verified`

## Gates

- **G0_registration_binding:** PASS
- **G1_strict_opposite_scores:** PASS
- **G2_constructed_width_bound:** PASS
- **G3_lower_witness_validity:** PASS
- **G4_lower_witness_sharpness:** PASS
- **G5_fresh_grid_complete:** PASS
- **G6_zero_endpoint_discontinuity:** PASS

## Fresh full-pair cells

| dimension | bound | rays | pairs | theorem width | maximum used | failures |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 25 | 1600 | 1279200 | 49 | 49 | 0 |
| 2 | 26 | 1696 | 1437360 | 51 | 51 | 0 |
| 2 | 27 | 1840 | 1691880 | 53 | 53 | 0 |
| 2 | 28 | 1936 | 1873080 | 55 | 55 | 0 |
| 2 | 29 | 2160 | 2331720 | 57 | 57 | 0 |
| 2 | 30 | 2224 | 2471976 | 59 | 59 | 0 |
| 2 | 31 | 2464 | 3034416 | 61 | 61 | 0 |
| 2 | 32 | 2592 | 3357936 | 63 | 63 | 0 |
| 3 | 6 | 1730 | 1495585 | 11 | 11 | 0 |
| 5 | 2 | 2882 | 4151521 | 3 | 3 | 0 |

The corrected theorem applies only to `0<delta<1`. Endpoint controls confirm
that a narrower tie-producing query separates the lower witness at `delta=0`
but ceases to separate it at `delta=1/2`.

## Claim boundary

This verifies the implementation and fresh witnesses for the corrected
finite-lattice theorem. The written proof carries the theorem. It neither
establishes novelty nor resolves the behavioral, discounted, finite-sample, or
inconsistent-demonstrator parts of ASMP-9.
