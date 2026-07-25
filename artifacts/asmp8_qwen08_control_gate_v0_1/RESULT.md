# ASMP-8 Qwen0.8B control-gating result v0.1

Status: `qwen_confidence_control_gate_not_established`

- Rows: 576
- Validation proxy-failure rate: 0.246528
- Validation mean regret: 0.132569
- Application-balanced selective-risk AUC improvement: -0.00031074
- Application-cluster bootstrap 95% interval: [-0.00087434, 0.00009901]
- One-sided within-stratum permutation p: 0.94143485
- Log-loss improvement: -0.00027228

## Per-application selective-risk improvement

| Application | Improvement |
|---|---:|
| bitvm_profile | -0.00230464 |
| diplomacy_orders | -0.00093173 |
| memetic_treaty | 0.00000000 |
| moral_story | 0.00000000 |
| oracle_control | -0.00001172 |
| prisoner_dilemma | 0.00000000 |
| secret_route | 0.00045139 |
| strategic_tick | 0.00000000 |
| studio_skill_route | 0.00000000 |

## Claim boundary

Held-out synthetic controller-task selective-risk prediction for one Qwen0.8B first-token probability. No causal, deployment, scalable-oversight, Goodhart-frontier, or recursive-improvement conclusion follows.
