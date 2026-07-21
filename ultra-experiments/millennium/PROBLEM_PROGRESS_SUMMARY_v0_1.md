# AI Safety Millennium Problems: peer-review summary and progress map

## Status of this document

This is a non-normative review aid for `ASMP-CANDIDATE-SET-v0.1`. The canonical definitions, quantifiers, and resolution rules remain in [AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md](AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md). If this summary conflicts with that document, the canonical document controls.

The set contains seven proposed long-horizon mathematical problems for AI safety. They are candidate research problems, not Clay Mathematics Institute prizes, and have not yet received the external field review required for public-prize status.

## Progress accounting as of 2026-07-20

- **Formally addressed under an exact ASMP problem ID and prospectively frozen
  claim boundary:** 6 of 7 (`ASMP-1`, `ASMP-2`, `ASMP-3`, `ASMP-4`,
  `ASMP-5`, and `ASMP-7`).
- **Additional problems beyond ASMP-1 with bounded registered experimentation
  attempted:** 5 of 7 (`ASMP-2`, `ASMP-3`, `ASMP-4`, `ASMP-5`, and
  `ASMP-7`).
- **Additional problems beyond ASMP-1 with completed bounded results:** 4 of 7
  (`ASMP-2`, `ASMP-3`, `ASMP-4`, and `ASMP-7`).
- **Formally registered execution attempts ending unavailable before a
  scientific result:** 1 of 7 (`ASMP-5`, frozen resource-cap stop).
- **Resolved at the full frozen Millennium-problem scope:** 0 of 7.
- **Closed theorem or exact-enumeration seeds inside an addressed problem:** 4.
- **Completed real-model falsification experiments inside an addressed problem:** 1.
- **Problems remaining at proposal, review, or precursor-tool stage:** 1 of 7
  (`ASMP-6`).

“Formally addressed” means that work was prospectively registered against an
exact ASMP problem and a frozen claim boundary. It does not require a positive
result: `ASMP-5` counts as addressed because its protocol was frozen before
execution, even though execution stopped unavailable before producing a
scientific outcome. “Completed bounded result” requires a valid result rather
than a registration or run attempt. Related portfolio work is not counted merely
because it resembles part of a problem. “Resolved” requires the complete
two-sided resolution standard in the canonical document; no current experiment
or bounded theorem meets that standard.

## The seven problems

| ID | Problem | Core question | Current ASMP-bound status |
|---|---|---|---|
| ASMP-1 | Mechanistic Identifiability Modulo Functional Symmetry | When do measurements and interventions identify a real causal mechanism, after quotienting permitted symmetries? | **Addressed, unresolved.** Two closed finite theorem seeds and one completed Qwen falsification experiment sharpen the target. |
| ASMP-2 | Shift-Spanning Safety Certification | When do finitely many evaluations justify a uniform claim over a declared family of deployment shifts? | **Formally addressed, unresolved.** The [registered crossed-shift result](asmp2_crossed_shift/RESULT.md) validates an exact forced counterexample shape. The [active-design census](asmp2_active_design_census/RESULT_v0_2_2.md) exhaustively rejects the registered myopic minimax selector as an efficient multi-step policy in one finite polynomial class. Neither is a uniform shift-spanning certification theorem. |
| ASMP-3 | The Weak-Verifier Soundness Frontier | Which superhuman work can a weaker, noisy semantic verifier judge soundly? | **Formally addressed, unresolved.** The [registered correlated-noise result](asmp3_weak_verifier_frontier/RESULT_v0_1.md) gives an exact finite correlation/diversity frontier after a refuting semantic atom has already been located, and proves that atom-averaged accuracy does not imply uniform soundness on challenger-selected refutations. It does not test refutation search or real weak judges. |
| ASMP-4 | Two-Port Evaluator-Relative Confinement | What separate read and write information rates are necessary and sufficient for evaluator-relative control? | **Formally addressed, unresolved.** The [registered two-port result](asmp4_two_port_game/RESULT.md) gives an exact 108-cell phase map for one finite rational architecture and separates read- and write-deficient controls. It does not establish necessary and sufficient confinement conditions in the canonical scope. |
| ASMP-5 | Reflective Safety under Open-Ended Self-Modification | When do local safety certificates compose through recursive replacement of the system and its evaluators? | **Formally addressed, unresolved; first execution unavailable.** The [registered verifier-drift census](asmp5_verifier_drift/RESULT.md) reached its frozen wall-time cap before emitting a scientific result. The resource-cap stop is evidence that the instrument needs a versioned implementation or budget repair, not evidence for or against reflective safety. |
| ASMP-6 | Adaptive Semantic Collusion Capacity | How much strategic coordination can agents hide in allowed communication under active auditing? | **Not yet formally addressed.** Steganographic-collusion and covert-channel eval concepts remain candidate instruments. |
| ASMP-7 | Capability Attestability under Compression and Decomposition | Which governance predicates remain verifiable after capability is compressed, decomposed, or migrated? | **Formally addressed, unresolved.** The [registered finite attestation result](asmp7_attestability_frontier/RESULT_v0_1.md) proves trace-law overlap for one 3,145,728-state execution/representation registry and computes an exact charged-audit privacy/cost frontier. It assumes trusted-meter coverage and does not establish real-model or transformation-universal attestability. |

## ASMP-1 evidence chain

### 1. Finite-chain identifiability seed

The [finite-chain result](asmp1_chain_seed/RESULT_v0_1.md) proves an elementary deterministic theorem and verifies exact counterexamples to two insufficient heuristics:

- touching or crossing a causal cut does not by itself identify downstream state; and
- singleton interventions can leave higher-order mechanism directions in an exact kernel.

It replaces raw intervention coverage with a sharper candidate object: intervention-design tomography modulo functional symmetry. It does not solve the generic analytic, noisy, or finite-sample ASMP-1 problem.

### 2. Interaction-order tomography

The [interaction-tomography result](asmp1_interaction_tomography/RESULT_v0_1.md)
registers an executable consolidation of classical finite Boolean Fourier,
design-of-experiments, and Mobius-inversion facts:

- designs containing interventions through order `r` identify exactly the interaction coordinates through order `r`;
- the sharp threshold for uniform recovery of degree-`k` Boolean mechanisms is `r = k`; and
- minimum-cardinality exact designs can be substantially less well-conditioned than redundant designs; and
- labelled and signed-parent-gauge identifiability differ by one intervention order in the registered full Boolean class.

The exact census covers all registered Boolean functions through four variables. The
[prior-art audit](asmp1_interaction_tomography/PRIOR_ART_v0_1.md) identifies the
Fourier recovery, rank, zeta/Mobius, and conditioning ingredients as classical
or direct corollaries. The `6/22/402` orbit census is Harrison's classical
NP-equivalence sequence. The exact labelled-versus-signed-parent-gauge
threshold remains a candidate-new elementary lemma, not an established novelty
claim and not a transformer theorem.

### 3. Qwen-0.8B real-model falsification

The [Qwen projector result](asmp1_qwen_projector_tomography/RESULT.md) applied the complete four-site, 16-mask design to lineage-certified rank-one projectors:

- the selected intervention was causally live and had roughly four times the matched-random full-cube magnitude;
- degree-two terms worsened held-out prediction in all nine graph-reachability subconditions; and
- a context-stable global interaction algebra was therefore not established.

The result narrows the empirical object toward context-conditioned interaction coefficients. Its frozen S0 specificity fraction was later recognized as scale-confounded; the [audit addendum](asmp1_qwen_projector_tomography/AUDIT_ADDENDUM.md) limits the interpretation, and the [v0.2 successor draft](../../protocols/qwen08_projector_tomography_v0_2.json) prospectively introduces magnitude matching and absolute higher-order energy.

## What would count as resolving ASMP-1

The current chain does not satisfy the canonical four-part resolution obligation. A complete ASMP-1 resolution still requires:

1. a maximal or explicitly justified symmetry/equivalence quotient;
2. necessary and sufficient intervention and environment conditions;
3. a constructive recovery procedure with finite-sample stability bounds; and
4. matching indistinguishability or query-complexity lower bounds when those conditions fail.

A counterexample to the frozen Cut-Separation Conjecture can resolve that conjecture as false, but it resolves the broader classification program only if accompanied by a complete replacement criterion or an impossibility theorem for criteria of the declared form.

## Recommended peer-review order

1. Read this progress map for scope and status.
2. Review the [canonical problem statements](AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md), especially quantifier order and resolution obligations.
3. Read the [hostile referee audit](REFEREE_AUDIT_v0_1.md) for known definition debt and reasons the set is not yet prize-ready.
4. For ASMP-1, review the finite-chain theorem, interaction-tomography theorem, and real-model negative in that order.
5. Check the [machine-readable registry](problem_set_v0_1.json) and [validation receipt](VALIDATION_RECEIPT_v0_1.json) for structural consistency. The validation receipt checks document integrity, not mathematical truth or novelty.

## Questions for external reviewers

- Are any candidates already equivalent to, subsumed by, or contradicted by established theorems?
- Are the adversary, quantifier order, liveness condition, and performance floor closed enough to support a durable problem statement?
- Does each negative resolution rule refute the entire frozen statement rather than one proposed method?
- Are the robust and computability versions genuine mathematical obligations rather than informal aspirations?
- Does each stated property imply the declared safety consequence, or only correlate with it?
- Should any candidates be merged, split, or demoted before a v0.2 problem set?
