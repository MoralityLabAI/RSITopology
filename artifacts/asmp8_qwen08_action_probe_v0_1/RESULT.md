# Qwen0.8B action-probe control gate v0.1

Status: `qwen_action_probe_control_gate_not_established`

The target-conditioned action distribution produced a positive held-out
application-balanced selective-risk improvement of `0.00387834`. Its
within-stratum permutation p-value was `0.04441191`, but the preregistered
application-cluster bootstrap interval was
`[-0.00064906, 0.01111617]`. Because the lower endpoint did not strictly clear
zero, gate G0 failed exactly as registered.

The mixed secondary result is informative but non-binding:

- baseline-to-augmented validation log-loss improvement: `0.01489775`;
- baseline average precision: `0.76809808`;
- augmented average precision: `0.79216437`;
- baseline ROC AUC: `0.93567859`;
- augmented ROC AUC: `0.93580840`.

The action probe is not itself a competitive controller on this panel. On the
validation half, its selected-action accuracy was `0.274306`, versus
`0.753472` for the proposer-score proxy. Mean regret was `0.437951` for the
probe versus `0.132569` for the proxy, and the two actions disagreed on
`0.756944` of rows. The model distribution may still encode a weak risk
correlate, but the registered primary analysis did not establish that this
correlate generalizes across applications.

All capture preconditions passed before outcome reveal: 1,152 complete
A/B/C/D vectors, exactly two planned cold-start sessions, zero probability
drift across restarts, and target-blind feature liveness well above the frozen
floor.

## Claim boundary

This result rejects one constrained Qwen0.8B action-probe feature block for the
registered cross-application control-gating claim. It does not reject
hidden-state features, larger models, stronger task-conditioned elicitation,
or within-application uses. It provides no causal, deployment,
scalable-oversight, Goodhart-frontier, recursive-improvement, or ASMP-8
resolution evidence.
