# AI Safety Millennium Problems: peer-review summary and progress map

## Status of this document

This is a non-normative review aid for `ASMP-CANDIDATE-SET-v0.1`. The canonical definitions, quantifiers, and resolution rules remain in [AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md](AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md). If this summary conflicts with that document, the canonical document controls.

The set contains seven proposed long-horizon mathematical problems for AI safety. They are candidate research problems, not Clay Mathematics Institute prizes, and have not yet received the external field review required for public-prize status.

## Progress accounting as of 2026-07-21

- **Formally addressed under an exact ASMP problem ID and prospectively frozen
  claim boundary:** 7 of 7.
- **Additional problems beyond ASMP-1 with bounded registered experimentation
  attempted:** 6 of 7 (`ASMP-2` through `ASMP-7`).
- **Additional problems beyond ASMP-1 with completed bounded results:** 6 of 7
  (`ASMP-2` through `ASMP-7`).
- **Historical registered execution attempts ending unavailable before a
  scientific result:** 1 (`ASMP-5` v0.1); its versioned v0.2 repair now has a
  completed bounded result.
- **Self-contained candidate mathematical resolutions at the full frozen
  Millennium-problem scope:** 1 of 7 (`ASMP-4`); independent external review
  remains pending.
- **Externally peer-reviewed resolutions:** 0 of 7.
- **Closed theorem or exact-enumeration seeds inside an addressed problem:** 7.
- **Completed real-model falsification experiments inside an addressed problem:** 1.
- **Problems remaining only at proposal, review, or precursor-tool stage:** 0
  of 7.

“Formally addressed” means that work was prospectively registered against an
exact ASMP problem and a frozen claim boundary. It does not require a positive
result: `ASMP-5` counts as addressed because its protocol was frozen before
execution. Its first execution stopped unavailable before producing a
scientific outcome, while a separately registered optimized implementation
subsequently completed the same finite grid. “Completed bounded result” requires a valid result rather
than a registration or run attempt. Related portfolio work is not counted merely
because it resembles part of a problem. “Resolved” requires the complete
two-sided resolution standard in the canonical document; no current experiment
or bounded theorem meets that standard. The ASMP-4 serial-collapse theorem is
the first package to claim every frozen mathematical obligation; this summary
labels it a candidate resolution until independent review challenges or
confirms the proof.

## The seven problems

| ID | Problem | Core question | Current ASMP-bound status |
|---|---|---|---|
| ASMP-1 | Mechanistic Identifiability Modulo Functional Symmetry | When do measurements and interventions identify a real causal mechanism, after quotienting permitted symmetries? | **Candidate negative resolution of the uniform representation-independent program; external scope review pending.** The representation-boundary theorem proves uniform undecidability for arbitrary computable-real analytic encodings without a certified gap, decidability for rational semialgebraic encodings, and a complete constructive linear-gauge lane. |
| ASMP-2 | Shift-Spanning Safety Certification | When do finitely many evaluations justify a uniform claim over a declared family of deployment shifts? | **Formally addressed, unresolved.** The [registered crossed-shift result](asmp2_crossed_shift/RESULT.md) validates an exact forced counterexample shape. The [active-design census](asmp2_active_design_census/RESULT_v0_2_2.md) exhaustively rejects the registered myopic minimax selector as an efficient multi-step policy in one finite polynomial class. Neither is a uniform shift-spanning certification theorem. |
| ASMP-3 | The Weak-Verifier Soundness Frontier | Which superhuman work can a weaker, noisy semantic verifier judge soundly? | **Exact protocol-quantifier fork; authoritative scope review pending.** The [v0.3 `Refute`-interface result](asmp3_resolution_boundary_v0_3/NEGATIVE_RESOLUTION_CANDIDATE_v0_3.md) proves the parity-channel obstruction conditionally. The [v0.7 complete-game successor](asmp3_protocol_quantifier_v0_7/PROTOCOL_QUANTIFIER_THEOREM_v0_7.md) closes the game-specification gap and certifies both readings: frozen semantic encodings give optimal gap `(3/5)^floor(log2 n) -> 0`, while existential protocol encodings admit an `O(log n)` vector-disagreement protocol with one semantic query and constant gap `3/5`. The remaining question is which encoding quantifier v0.1 intended; another parity grid cannot decide that normative scope issue. |
| ASMP-4 | Two-Port Evaluator-Relative Confinement | What separate read and write information rates are necessary and sufficient for evaluator-relative control? | **Candidate negative resolution with positive replacement characterization; external review pending.** The [metric-robust bilateral theorem](asmp4_metric_robust_collapse_v0_3/RESULT.md) proves a diagonal-quadrant region for every shared relabel-invariant transcript-tree cost. The [v0.4 heterogeneous-cost boundary](asmp4_heterogeneous_port_costs_v0_4/RESULT.md) proves that unit rescaling preserves rectangularity but expected-read versus worst-write semantics can yield an exact nonrectangular frontier. The [v0.2 theorem](asmp4_serial_collapse_theorem_v0_2/RESULT.md) supplies exact finite corrections; the earlier [108-cell game](asmp4_two_port_game/RESULT.md) remains a frozen memoryless-grammar result. |
| ASMP-5 | Reflective Safety under Open-Ended Self-Modification | When do local safety certificates compose through recursive replacement of the system and its evaluators? | **Formally addressed, unresolved; repaired bounded result complete.** The [v0.1 verifier-drift census](asmp5_verifier_drift/RESULT.md) correctly stopped at its frozen wall-time cap. The separately registered [v0.2 repair](asmp5_verifier_drift/v0_2_repair/RESULT_v0_2.md) exhaustively finds depth-two unsafe paths when a successor checker becomes active, while a frozen-root refinement blocks them and retains an eight-step, nine-state safe chain. This is one finite counterexample/control pair, not an open-ended composition theorem. |
| ASMP-6 | Adaptive Semantic Collusion Capacity | How much strategic coordination can agents hide in allowed communication under active auditing? | **Formally addressed, unresolved.** The [registered finite semantic-collusion frontier](asmp6_semantic_collusion_frontier/RESULT_v0_1.md) exactly separates message-averaged from per-message covertness over a four-symbol registry and measures the effect of a charged active auditor. It is neither an asymptotic capacity theorem nor evidence of language-model collusion. |
| ASMP-7 | Capability Attestability under Compression and Decomposition | Which governance predicates remain verifiable after capability is compressed, decomposed, or migrated? | **Formally addressed, unresolved.** The [registered finite attestation result](asmp7_attestability_frontier/RESULT_v0_1.md) proves trace-law overlap for one 3,145,728-state execution/representation registry. The [excluded-band successor](asmp7_attestability_frontier/RESULT_v0_2_1.md) computes 40 exact nonzero-gap audit minima and calibrates how cost grows as the policy boundary narrows. Both assume trusted-meter coverage and establish neither real-model nor transformation-universal attestability. |

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

### 4. Cut-separation well-posedness audit

The [exact cut-separation audit](asmp1_cut_separation_audit/RESULT_v0_1.md)
tests both directions of the proposed iff:

- a coarse nonconstant abstraction is exactly identified without excitation
  sufficient to recover the full local mechanism class, so the necessity
  condition must be `Q`-relative;
- full replacement access to a typed analytic cut can leave a
  positive-dimensional upstream fiber through a dimension-reducing downstream
  mechanism; and
- full environment support plus a singleton intervention hypergraph that
  covers, pair-separates, and has full incidence rank on every parent still
  leaves an exact higher-order interaction kernel.

These witnesses refute literal full-class and purely structural readings. If
cut separation or `kappa>0` is instead defined as positive separation of every
distinct `Q/G` pair, the condition assumes quotient identifiability and is
circular. The audit therefore supplies a stopping argument for the v0.1 iff as
written, not a resolution of the broader classification program.

### 5. Representation-sensitive resolution boundary

The [representation-boundary theorem](asmp1_resolution_boundary_v0_2/RESULT_v0_2.md)
supplies a replacement classification:

- every identifiable `Q/G` must factor through the registered observation
  experiment, making the observation-fiber quotient the universal
  maximum-information identifiable abstraction;
- exact quotient identifiability is decidable for compact rational
  semialgebraic mechanism classes with rational polynomial maps and a finite
  rational gauge;
- no total uniform criterion exists when analytic coefficients may be named by
  arbitrary computable-real Cauchy programs without a certified nonzero gap;
  the proof is a direct halting reduction using degree-one entire functions,
  with an equivalent program-generated `{0,1}` rational Taylor encoding;
  and
- linear analytic mechanisms with a frozen translation gauge are identifiable
  exactly at full quotient row rank, with pseudoinverse recovery, an explicit
  Gaussian finite-sample bound, exact collision and minimum-query lower bounds,
  and a matching two-point stability lower bound.

The exact harness classified all 21,300 `{-1,0,1}` designs through quotient
dimension three: 12,516 full-rank designs received checked rational left
inverses, while 8,784 deficient designs received checked nonzero nullspace
collisions. The [resolution audit](asmp1_resolution_boundary_v0_2/RESOLUTION_AUDIT_v0_2.md)
labels this a candidate negative resolution of the uniform program. Full
canonical closure depends on whether v0.1 intended arbitrary computable-real
encodings or only a fixed decidable rational/algebraic grammar.

## What would count as resolving ASMP-1

The representation-boundary result now addresses all four obligations in the
linear-gauge lane and supplies a uniform impossibility theorem at the
computable-real encoding boundary:

1. a maximal or explicitly justified symmetry/equivalence quotient;
2. necessary and sufficient intervention and environment conditions;
3. a constructive recovery procedure with finite-sample stability bounds; and
4. matching indistinguishability or query-complexity lower bounds when those conditions fail.

A counterexample to the frozen Cut-Separation Conjecture can resolve that conjecture as false, but it resolves the broader classification program only if accompanied by a complete replacement criterion or an impossibility theorem for criteria of the declared form.

The remaining closure question is now one scope fork rather than a missing
bounded experiment. If arbitrary program-named computable-real coefficients
are admitted by `F`, the no-uniform-criterion theorem is a candidate negative
resolution under the canonical rule. If `F` was intended to be a fixed
decidable rational/algebraic grammar with certified margins, the theorem
proves decidability and completely resolves the linear-gauge subclass but does
not provide a polynomial recovery theorem for every nonlinear semialgebraic
SCM. External review must adjudicate that encoding quantifier before this
summary changes `candidate resolution` to `resolved`.

## Recommended peer-review order

1. Read this progress map for scope and status.
2. Review the [canonical problem statements](AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md), especially quantifier order and resolution obligations.
3. Read the [hostile referee audit](REFEREE_AUDIT_v0_1.md) for known definition debt and reasons the set is not yet prize-ready.
4. For ASMP-1, review the finite-chain theorem, interaction-tomography theorem,
   cut-separation audit, representation-boundary theorem and audit, then the
   real-model negative.
5. Check the [machine-readable registry](problem_set_v0_1.json) and [validation receipt](VALIDATION_RECEIPT_v0_1.json) for structural consistency. The validation receipt checks document integrity, not mathematical truth or novelty.

## Questions for external reviewers

- Are any candidates already equivalent to, subsumed by, or contradicted by established theorems?
- Are the adversary, quantifier order, liveness condition, and performance floor closed enough to support a durable problem statement?
- Does each negative resolution rule refute the entire frozen statement rather than one proposed method?
- Are the robust and computability versions genuine mathematical obligations rather than informal aspirations?
- Does each stated property imply the declared safety consequence, or only correlate with it?
- Should any candidates be merged, split, or demoted before a v0.2 problem set?
