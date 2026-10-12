# ASMP-8 Qwen0.8B action-probe result v0.1

Status: `qwen_action_probe_control_gate_not_established`

- Rows: 576
- Application-balanced selective-risk AUC improvement: 0.00387834
- Application-cluster bootstrap 95% interval: [-0.00064906, 0.01111617]
- One-sided matched-block permutation p: 0.04441191
- Log-loss improvement: 0.01489775
- Proxy action accuracy: 0.753472
- Probe action accuracy: 0.274306
- Proxy mean regret: 0.132569
- Probe mean regret: 0.437951
- Probe/proxy disagreement rate: 0.756944

## Per-application selective-risk improvement

| Application | Improvement |
|---|---:|
| bitvm_profile | 0.00228795 |
| diplomacy_orders | -0.00093173 |
| memetic_treaty | 0.00346905 |
| moral_story | 0.00000000 |
| oracle_control | 0.03025270 |
| prisoner_dilemma | 0.00000000 |
| secret_route | 0.00493124 |
| strategic_tick | -0.00286867 |
| studio_skill_route | -0.00223552 |

## Claim boundary

Held-out synthetic controller-task result for one constrained Qwen0.8B action distribution. No causal, deployment, scalable-oversight, Goodhart-frontier, recursive-improvement, or ASMP-8 conclusion follows.
