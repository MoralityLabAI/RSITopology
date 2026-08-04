# ASMP attempt-coverage audit - 2026-08-03

## Criterion

For this audit, an ASMP is **unexhausted** only when no genuine experiment,
proof attempt, or negative-proof attempt has been made.  A bounded or failed
attempt is enough to establish attempt coverage; it does not resolve the
mathematical problem.  "Exhausted" below therefore means only
`attempt_exists_under_this_criterion`.

The audited universe is the frozen ASMP-1--7 candidate set, the proposed
ASMP-8--12 expansion, and the named ASMP-5A subproblem.  Nonfrozen successor
formulations are tracked separately and are not silently promoted into that
universe.

## Whole-problem coverage

| Area | Genuine attempted lane | Authoritative evidence | Attempt coverage |
|---|---|---|---|
| ASMP-1 | Exact theorem, finite census, and uniform negative boundary | [`asmp1_resolution_boundary_v0_2/RESULT_v0_2.md`](asmp1_resolution_boundary_v0_2/RESULT_v0_2.md) | exhausted (attempt coverage only) |
| ASMP-2 | Exact forced crossed-shift counterexample | [`asmp2_crossed_shift/RESULT.md`](asmp2_crossed_shift/RESULT.md) | exhausted (attempt coverage only) |
| ASMP-3 | Exact positive/negative frontier work plus correction of an overclaimed impossibility | [`asmp3_normative_closure_reassessment_v2_19/REASSESSMENT_AND_CORRECTION_v2_19.md`](asmp3_normative_closure_reassessment_v2_19/REASSESSMENT_AND_CORRECTION_v2_19.md) | exhausted (attempt coverage only) |
| ASMP-4 | Long exact theorem/counterexample chain and a single-root operational stop | [`asmp4_single_root_stop_v0_36/RESULT.md`](asmp4_single_root_stop_v0_36/RESULT.md) | exhausted (attempt coverage only) |
| ASMP-5 | Transition-derived all-depth rooted-safety induction with liveness control | [`asmp5_verifier_drift/v0_3_inductive_root/RESULT_v0_3.md`](asmp5_verifier_drift/v0_3_inductive_root/RESULT_v0_3.md) | exhausted (attempt coverage only) |
| ASMP-6 | Exact one-shot balanced-cover parity theorem | [`asmp6_semantic_collusion_frontier/v0_2_balanced_cover/RESULT_v0_2.md`](asmp6_semantic_collusion_frontier/v0_2_balanced_cover/RESULT_v0_2.md) | exhausted (attempt coverage only) |
| ASMP-7 | Exact finite attestability, fixed selective-suppression censuses, and verified causal adaptive-suppression theorem/grid | [`asmp7_attestability_frontier/artifacts_v0_4_adaptive_suppression/RESULT_v0_4.md`](asmp7_attestability_frontier/artifacts_v0_4_adaptive_suppression/RESULT_v0_4.md) | exhausted (attempt coverage only) |
| ASMP-8 | Exact full pointwise/adaptive deterministic-audit census | [`asmp8_goodhart_frontier_census/v0_6_adaptive_reuse/RESULT_v0_6.md`](asmp8_goodhart_frontier_census/v0_6_adaptive_reuse/RESULT_v0_6.md) | exhausted (attempt coverage only) |
| ASMP-9 | Prospectively frozen real-model transport test with a reproduced negative gate | [`asmp9_reward_gauge_census/out_of_family_transport_v0_82/RESULT_v0_82.md`](asmp9_reward_gauge_census/out_of_family_transport_v0_82/RESULT_v0_82.md); [`AUDIT_v0_82.md`](asmp9_reward_gauge_census/out_of_family_transport_v0_82/AUDIT_v0_82.md) | exhausted (attempt coverage only) |
| ASMP-10 | Exact bounded-polynomial prefix-obstruction theorem | [`asmp10_capability_transition/prefix_obstruction/RESULT_v0_1.md`](asmp10_capability_transition/prefix_obstruction/RESULT_v0_1.md) | exhausted (attempt coverage only) |
| ASMP-11 | Exact transparent-parity access-ladder and multistage crossover evidence | [`asmp11_access_ladder/covering_frontier_v0_2_1/artifacts_v0_2_1_2/synthesis_receipt_v0_2_1_2.json`](asmp11_access_ladder/covering_frontier_v0_2_1/artifacts_v0_2_1_2/synthesis_receipt_v0_2_1_2.json) | exhausted (attempt coverage only) |
| ASMP-12 | Exact finite constructible-survival correspondence | [`asmp12_program_equilibrium/v0_3_constructible_survival/RESULT_v0_3_1.md`](asmp12_program_equilibrium/v0_3_constructible_survival/RESULT_v0_3_1.md) | exhausted (attempt coverage only) |
| ASMP-5A | Exact finite proof-tree census and resource-ranking reversal | [`asmp5a_bounded_tiling/RESULT_v0_1.md`](asmp5a_bounded_tiling/RESULT_v0_1.md) | exhausted (attempt coverage only) |

No whole problem in the audited universe is untouched under the stated
criterion.  This finding must not be paraphrased as "all ASMPs are resolved."
Every top-level problem remains subject to its own much stronger resolution
rule.

## Successor-obligation queue and dispositions

At audit time, the next useful work was on successor obligations for which the
repository had not yet run an experiment or supplied a proof/negative proof.
Completed rows remain in the queue for chronology but cease to be untouched.

| Priority | Area and untouched obligation | Evidence of the gap | Disposition |
|---:|---|---|---|
| 1 | ASMP-6 multiletter/tensorization and correlated block encoders | The v0.2 protocol is explicitly one-shot and excludes block codes/history; prior design prose had no executed experiment or theorem result. | **Completed attempt.** The source-frozen v0.3 theorem/grid found four finite odd-alphabet block advantages and passed independent replay; see [`RESULT_v0_3.md`](asmp6_semantic_collusion_frontier/artifacts_v0_3_multiletter_tensorization/RESULT_v0_3.md). This does not resolve ASMP-6. |
| 2 | ASMP-10 disjoint-seed held-out transition predictor | `PREDICTOR_PROTOCOL_DRAFT_v0_5_2.md` is explicitly unregistered and unauthorized. | **Completed negative feasibility attempt for the fixed eight-cluster design.** Exact sign-gate and optimistic lower-bound power calculations show that the proposed conjunction is underpowered absent implausibly low cluster variance; see [`HELDOUT_PREFIX_PREDICTOR_REGISTRATION_REVIEW_20260803.md`](asmp10_capability_transition/HELDOUT_PREFIX_PREDICTOR_REGISTRATION_REVIEW_20260803.md). No held-out target run was authorized. A target-free joint-power simulation with a selected larger cluster count remains a successor, not an untouched fixed-design obligation. |
| 3 | ASMP-7 adaptive history-dependent suppression | The v0.3 protocol covers fixed selective suppression and places adaptive masks outside scope. | **Completed attempt.** Source-frozen v0.4 proves the registered finite causal endpoint theorem, transfers all 48 inherited statuses/minima, passes 72 quotient rows, 144 upper-tail rows, 11,520 generic-terminal checks, two scope breakers, and import-independent verification; see [`RESULT_v0_4.md`](asmp7_attestability_frontier/artifacts_v0_4_adaptive_suppression/RESULT_v0_4.md). This does not resolve ASMP-7. |
| 4 | ASMP-11 real-model/obfuscation access ladder | Existing evidence is transparent Boolean parity, not learned conditional defection. | Freeze estimator, replicate unit, confidence rule, and access interventions before any model run. |
| 5 | ASMP-12 mixed strategies or equilibrium-selection dynamics | The current correspondence is finite and pure/constructible only. | Register one selection dynamic or finite mixed-equilibrium class with encoding robustness. |
| 6 | ASMP-5 dynamic trusted-anchor replacement, learned-checker error, or infinite distinct-state progress | V0.3 keeps the trusted root fixed, although it already tests successor-checker replacement and a static root-permission mutation; arbitrary time comes from a repeated two-cycle. | Require a dynamic root/anchor safety theorem, stochastic checker-learning error, or infinitely many distinct safe states. |
| 7 | ASMP-4 full source-faithful capacity/support theorem beyond the existing finite boundary audit | The local nonfrozen v2 work already contains an exact eight-row source-factorization boundary, but no full capacity or support theorem. | Any new assignment must be self-contained and exploratory; do not bind or promote the dirty v2/v2.1 drafts. |

## Operating rule

New assignments begin on untouched lanes with a prospective source freeze,
explicit controls and falsifier, independent verification, and a bounded
claim; assigned work then continues to its registered bounded stop. Where a
lane already has a real attempt, further work requires a materially new
obligation rather than another cosmetic parameter sweep.
