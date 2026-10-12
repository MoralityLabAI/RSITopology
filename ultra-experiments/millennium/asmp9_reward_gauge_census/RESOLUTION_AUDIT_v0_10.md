# ASMP-9 resolution audit after v0.10

Date: 2026-07-28

## Verdict

**ASMP-9 is not resolved.**

Version v0.10 materially improves the finite-MDP policy-access row. It gives
an exact shaping-subspace intersection formula, a sharp two-environment
criterion for a structured intervention family, a two-discount criterion for
a cyclic family, and a matched deterministic-policy obstruction. It remains
an exact finite specialization beneath established entropy-regularized IRL
identifiability theory.

## New evidence

| Layer | Authoritative evidence | What is proved | Resolution status |
|---|---|---|---|
| Exact finite soft-policy access | [v0.10 public summary](finite_mdp_access_v0_10/PUBLIC_SUMMARY_v0_10.md) | One known-environment soft policy leaves `S` shaping dimensions. Against a self-loop reference, a second kernel leaves `S-rank(A_P)` dimensions; for deterministic kernels this is successor-difference component count. A connected cyclic kernel or a distinct discount reduces common ambiguity to a global constant. | Complete for the registered known finite entropy-regularized families only. |
| Observation-class separation | [v0.10 matched witness](finite_mdp_access_v0_10/PUBLIC_SUMMARY_v0_10.md#matched-deterministic-policy-obstruction) | The same two environments that close soft-policy ambiguity retain a non-gauge reward pair under deterministic action identities. | Exact finite counterexample; not a full deterministic-policy invariance classification. |
| Direct one-step return comparison | [v0.10 verification](finite_mdp_access_v0_10/verification_v0_10.json) | Ambiguity is query-graph component count, and `SA-1` comparisons are sharply necessary and sufficient for constant-only ambiguity. | Complete for the registered direct comparator, not passive trajectories. |

## Effect on the five obligations

### 1. Maximal invariance groups

**Improved but partial.** Version v0.10 computes exact potential-shaping image
intersections for the declared soft-policy access and shows that action
identity has a strictly larger local ambiguity. It does not classify unknown
temperature, non-entropy regularization, constraints, history-dependent
rewards, or response misspecification.

### 2. Necessary and sufficient access

**Improved but partial.** Two environments are necessary and sufficient in the
registered self-loop-plus-connected-successor grammar; two discounts are
necessary and sufficient in the registered cyclic grammar. The theorem is not
a global optimum over all environment families or all observation types.

### 3. Sharp query, sample, and intervention-order bounds

**Improved but partial.** The structured soft-policy environment count is
sharp, and the direct-return comparator has the sharp `SA-1` tree threshold.
Finite-sample policy estimation, adaptive environment selection, and matching
minimax lower bounds remain open.

### 4. Behavioral misspecification robustness

**Still not established at resolution scope.** The deterministic-policy arm
proves that weakening the observation changes the quotient, but no theorem
propagates policy-estimation or response-model error into reward uncertainty.

### 5. No-go classification

**Improved but incomplete.** Version v0.10 gives a clean matched no-go for
deterministic action identities. The broader contextual, dependent,
history-sensitive, non-expected-utility, and inconsistent-demonstrator
classification remains open.

## Highest-value remaining sequence

### v0.11: contextual/history-sensitive no-go

Freeze a finite response family with:

- a scalar utility in every context separately;
- no shared context-independent scalar;
- a context-indexed utility representation that does exist;
- exact shared-scalar and context-indexed reconstruction maps;
- a sharp access threshold for detecting the incompatibility; and
- matched controls in which a shared scalar exists.

The load-bearing target is a two-sided theorem: characterize exactly when
context-local preferences glue to one global scalar and provide a minimal
incompatibility witness when they do not.

### Later statistical closure

After v0.11, remaining work includes:

- minimax bounds matching the conservative v0.9 certificate;
- adaptive comparison and environment allocation;
- finite-sample soft-policy estimation;
- unknown-temperature normalization or calibration;
- dependent and sequential observations; and
- robustness under broader demonstrator models.

## Completion criterion

Current results now cover direct linear comparisons, finite noisy pairwise
choices, discounted shaping, exact soft policies, and a deterministic-policy
counterexample. A defensible resolution still requires a unified maximal
invariance classification, matched upper and lower access bounds across a
materially broad source family, finite-sample misspecification guarantees,
and a two-sided contextual/history-sensitive scalar-existence theorem.
