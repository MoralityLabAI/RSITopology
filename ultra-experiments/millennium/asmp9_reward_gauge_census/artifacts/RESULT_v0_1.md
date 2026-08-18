# ASMP-9 reward-gauge graph census — Result

**Verdict:** `exact_finite_reward_gauge_access_threshold_seed_established`

## Gates

- **G0_registration_binding:** PASS
- **G1_complete_graph_census:** PASS
- **G2_cycle_rank_identity:** PASS
- **G3_gauge_annihilation:** PASS
- **G4_exact_access_threshold:** PASS
- **G5_tree_and_forest_negative_control:** PASS
- **G6_ordinal_access_counterexample:** PASS

## Exact census

All 33,866 labelled simple graphs on two through six vertices were checked.
The census contained 30,596 graphs with loop access and 3,270 forests with beta_1=0.

For exact real-valued loop returns, the fundamental-cycle query count equals `beta_1 = m-n+c`. The full query kernel has dimension `n-c`, exactly the potential-shaping subspace; removing one independent loop query leaves one additional unidentified quotient direction.

## Access-model counterexample

On the triangle, rewards `[1, -1, 1]` and `[2, -2, 2]` have exact loop returns [3, 6] but identical ordinal signs [1, 1]. Their difference has nonzero loop return 3, so it is not a potential-shaping coboundary.

Therefore the exact-query threshold may not be transferred to ordinal preferences without an additional theorem.

## Claim boundary

For exact real-valued loop-return queries on the registered graph class, a fundamental cycle basis identifies the edge-reward quotient modulo potential shaping and the query-count threshold is beta_1.

Not established:

- the same threshold for noisy or ordinal human preferences
- discounted potential shaping
- reward recovery in an MDP from behavior
- practical dominance of shaping ambiguity
- novelty of the underlying graph-cohomology identity
- ASMP-9 resolution
