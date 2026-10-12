# ASMP-9 finite-MDP access verification v0.10

**Verdict:** `finite_mdp_environment_access_geometry_verified`

## Gates

- **G0_registration_binding:** PASS
- **G1_stochastic_coverage_and_shaping_injectivity:** PASS
- **G2_stochastic_intersection_formula:** PASS
- **G3_deterministic_component_theorem:** PASS
- **G4_deterministic_liveness:** PASS
- **G5_transition_discount_threshold:** PASS
- **G6_deterministic_policy_obstruction:** PASS
- **G7_trajectory_component_theorem:** PASS
- **G8_trajectory_sharpness:** PASS
- **G9_access_separation:** PASS
- **G10_resource_envelope:** PASS

## Deterministic transition census

- kernels: 65536
- connected successor graphs: 27264
- ambiguity distribution: {"1": 27264, "2": 31776, "3": 6240, "4": 256}

## Structured access result

One entropy-regularized policy leaves S shaping dimensions.
A connected second transition environment or a distinct discount
reduces the common ambiguity to one global constant. The matched
deterministic-policy pair remains nonidentifying.

## Claim boundary

Exact finite specialization of established entropy-regularized
IRL identifiability; not finite-sample policy estimation, general
environment design, passive trajectory IRL, or ASMP-9 resolution.
