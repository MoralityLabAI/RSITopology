# ASMP-9 finite-sample coherence verification v0.9

**Verdict:** `finite_sample_cycle_coherence_certificate_verified`

## Gates

- **G0_registration_binding:** PASS
- **G1_graph_and_bound_arithmetic:** PASS
- **G2_forest_nonvacuity:** PASS
- **G3_probability_floor_admission:** PASS
- **G4_certificate_safety:** PASS
- **G5_sufficient_bound_liveness:** PASS
- **G6_low_budget_inconclusiveness:** PASS
- **G7_high_budget_decisiveness:** PASS
- **G8_sign_mirror:** PASS
- **G9_status_closure:** PASS

## Graph-dependent sufficient bounds

| graph | beta_1 | k_max | samples per edge |
|---|---:|---:|---:|
| cycle_3 | 1 | 3 | 42556 |
| cycle_4 | 1 | 4 | 80201 |
| cycle_6 | 1 | 6 | 194868 |
| cycle_8 | 1 | 8 | 364615 |
| theta_4 | 2 | 4 | 83727 |
| complete_5 | 6 | 3 | 53258 |

## Interpretation

The registered simultaneous certificate distinguishes a declared
near-coherent region, a separated circulation alternative, and
an inconclusive region without turning non-rejection into scalar
coherence. Forests and probability-boundary violations remain
unavailable by construction.

## Claim boundary

Independent fixed-count Bernoulli comparisons on six planted
finite graphs; not minimax sample complexity, adaptive allocation,
human-response modeling, general IRL, or an ASMP-9 resolution.
