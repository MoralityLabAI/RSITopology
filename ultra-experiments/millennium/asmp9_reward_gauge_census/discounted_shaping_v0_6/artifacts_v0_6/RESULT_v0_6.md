# ASMP-9 discounted-shaping verification v0.6

**Verdict:** `discounted_shaping_gain_quotient_implementation_verified`

## Gates

- **G0_registration_binding:** PASS
- **G1_simple_rank:** PASS
- **G2_multigraph_rank:** PASS
- **G3_endpoint_ranks:** PASS
- **G4_trajectory_telescoping:** PASS
- **G5_matched_boundary:** PASS
- **G6_unequal_horizon_witness:** PASS
- **G7_planted_access_controls:** PASS

## Rank checks

| family | graphs | vertices | rational-rank mismatches | endpoint mismatches |
|---|---:|---:|---:|---:|
| simple_rank | 32768 | 6 | 0 | 0 |
| multigraph_rank | 8192 | 7 | 0 | 0 |

## Trajectory checks

- exact telescoping mismatches: `0`
- matched-boundary mismatches: `0`
- unequal-horizon missing witnesses: `0`

## Interpretation

Discounting replaces the ordinary cycle quotient with a
gain-graph quotient. Unbalanced components lose one invariant
dimension, and finite trajectory comparisons require matching
discounted boundary signatures.

## Claim boundary

Classical gain-graph and potential-shaping specialization; not
policy-based IRL, all reward invariances, a human model, or a
complete ASMP-9 resolution.
