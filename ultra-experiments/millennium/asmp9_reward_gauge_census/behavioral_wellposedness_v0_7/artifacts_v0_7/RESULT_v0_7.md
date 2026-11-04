# ASMP-9 behavioral well-posedness verification v0.7

**Verdict:** `behavioral_reconstruction_model_checking_split_verified`

## Gates

- **G0_registration_binding:** PASS
- **G1_simple_graph_access:** PASS
- **G2_multigraph_access:** PASS
- **G3_hodge_projection:** PASS
- **G4_cycle_bounds:** PASS
- **G5_inconsistent_control:** PASS
- **G6_adaptive_policy_width:** PASS
- **G7_nonadaptive_policy_width:** PASS
- **G8_finite_policy_ambiguity:** PASS

## Access ledger

| family | graphs | ledger mismatches | reconstruction mismatches | non-bridge misses | bridge false alarms |
|---|---:|---:|---:|---:|---:|
| simple_graphs | 32768 | 0 | 0 | 0 | 0 |
| multigraphs | 8192 | 0 | 0 | 0 | 0 |

## Interpretation

A spanning forest reconstructs a scalar only under a coherence
promise. Non-bridge edges are the exact coherence-only audit
universe; querying the remaining chords after a forest adds
beta_1 model checks. Deterministic policy observations retain a
positive ambiguity interval at every finite query count.

## Claim boundary

Classical finite graph/Hodge and threshold-search specialization;
not finite-sample Bradley-Terry estimation, general IRL, a human
model, or a complete ASMP-9 resolution.
