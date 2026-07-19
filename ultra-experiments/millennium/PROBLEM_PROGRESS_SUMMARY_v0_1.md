# AI Safety Millennium Problems: peer-review summary and progress map

## Status of this document

This is a non-normative review aid for `ASMP-CANDIDATE-SET-v0.1`. The canonical definitions, quantifiers, and resolution rules remain in [AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md](AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md). If this summary conflicts with that document, the canonical document controls.

The set contains seven proposed long-horizon mathematical problems for AI safety. They are candidate research problems, not Clay Mathematics Institute prizes, and have not yet received the external field review required for public-prize status.

## Progress accounting as of 2026-07-19

- **Formally addressed under an exact ASMP problem ID:** 1 of 7 (`ASMP-1`).
- **Resolved at the full frozen Millennium-problem scope:** 0 of 7.
- **Closed theorem or exact-enumeration seeds inside an addressed problem:** 2.
- **Completed real-model falsification experiments inside an addressed problem:** 1.
- **Remaining problems without a problem-ID-bound seed in this suite:** 6.

“Addressed” means that work was explicitly registered against an exact ASMP problem and its claim boundary. Related portfolio work is not counted merely because it resembles part of a problem. “Resolved” requires the complete two-sided resolution standard in the canonical document; no current experiment or bounded theorem meets that standard.

## The seven problems

| ID | Problem | Core question | Current ASMP-bound status |
|---|---|---|---|
| ASMP-1 | Mechanistic Identifiability Modulo Functional Symmetry | When do measurements and interventions identify a real causal mechanism, after quotienting permitted symmetries? | **Addressed, unresolved.** Two closed finite theorem seeds and one completed Qwen falsification experiment sharpen the target. |
| ASMP-2 | Shift-Spanning Safety Certification | When do finitely many evaluations justify a uniform claim over a declared family of deployment shifts? | **Not yet formally addressed.** Context-shift findings elsewhere in the repository are motivating evidence only. |
| ASMP-3 | The Weak-Verifier Soundness Frontier | Which superhuman work can a weaker, noisy semantic verifier judge soundly? | **Not yet formally addressed.** Evaluator-sufficiency counterexamples are adjacent but are not an ASMP-3 resolution seed. |
| ASMP-4 | Two-Port Evaluator-Relative Confinement | What separate read and write information rates are necessary and sufficient for evaluator-relative control? | **Not yet formally addressed in this suite.** The Confinement Width theory and CPU validation work are direct precursors but have not been registered as an ASMP-4 seed. |
| ASMP-5 | Reflective Safety under Open-Ended Self-Modification | When do local safety certificates compose through recursive replacement of the system and its evaluators? | **Not yet formally addressed.** The recursive-improvement protocol measures a bounded empirical proposal channel and explicitly cannot resolve the reflective frontier. |
| ASMP-6 | Adaptive Semantic Collusion Capacity | How much strategic coordination can agents hide in allowed communication under active auditing? | **Not yet formally addressed.** Steganographic-collusion and covert-channel eval concepts remain candidate instruments. |
| ASMP-7 | Capability Attestability under Compression and Decomposition | Which governance predicates remain verifiable after capability is compressed, decomposed, or migrated? | **Not yet formally addressed.** Identity attestation, compactification false positives, and loop-closure audits are substantial precursor tools, not an ASMP-7 theorem seed. |

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
