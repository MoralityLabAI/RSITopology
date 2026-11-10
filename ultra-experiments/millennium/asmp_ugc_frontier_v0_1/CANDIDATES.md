# ASMP-13–16 candidates from Unique Games, holonomy and game-space geometry

**Status:** non-normative scoping draft, 2026-11-09. No ASMP number here has been admitted to a frozen candidate set or designated a prize. The source ASMP-1..7 set is [v0.1](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md), and ASMP-8..12 belong to the [v0.2 expansion draft](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/V0_2_SCOPE_EXPANSION_DRAFT.md). These four entries are **provisional candidate numbers**. Their priority and overlap dispositions are given below.

**Inputs:** [EvalMath UGCS-01/02/03 PR #28](https://github.com/MoralityLabAI/EvalMath/pull/28), [OntologicalProofs Lean PR #35](https://github.com/patrickdugan/OntologicalProofs/pull/35), and the [OpenAI September 2026 Unique Games manuscript](https://github.com/openai/math/tree/main/preprints/The-Unique-Games-Theorem-September-23-2026), whose claim of resolving UGC remains subject to independent mathematical review. The elementary graph identities below do not depend on accepting that claimed resolution.

## Shared mathematical setting and invariance

A registered oriented edge-occurrence multigraph G=(V,E) carries a connection c in C¹(G;K)=K^E with K=F₂^s, q=|K|. A labeling a in K^V satisfies e=(u,v,c_e) when a(v)-a(u)=c_e. Vertex gauge p in K^V transforms c to c+dp. Write

    beta1(G)=|E|-|V|+number_of_components(G),
    phi_G(c)= min_a (1/|E|) sum_e 1[c_e != (da)_e],
    Hol_G(c) in K^beta1

using a frozen spanning forest and ordered fundamental cycle basis. The exact sequence C⁰ --d--> C¹ --Hol--> K^beta1, with ker(Hol)=im(d), shows that full K-valued cycle-return access identifies the gauge class in beta1 independent queries. It does not itself compute the minimizing labeling.

The declared downstream safety predicate is parameterized, e.g. Safe(c)=[phi_G(c)<=epsilon], Unsafe(c)=[phi_G(c)>=delta], with 0<=epsilon<delta<=1, and the input is promised to satisfy one branch. A monitoring/verifier architecture must meet an explicit cost, confidence and non-inertness budget. The graph, alphabet, query interface, encodings, error law and quantifier order must be frozen before results.

---

## ASMP-13 (top-level contender): Gauge-Complete Certification versus Computational Decoding

### Safety question

When a monitor has identified **every gauge-invariant fact encoded by a connection**, which global consistency or safety guarantees can it decide with bounded computation, communication and adversarial proof access?

### Candidate formal object

For a registered family C_n of explicit K_n-valued translation games, a query interface returns exact K_n-valued fundamental-cycle observations. The algorithm may receive an optional untrusted prover transcript pi of at most B(n) bits. Set a time bound T(n), query bound Q(n), and error bounds alpha,beta on the YES/NO promise phi<=epsilon versus phi>=delta. Define the **joint admissible frontier**

    F_C(epsilon,delta)
      ={(Q,T,B,alpha,beta):
           exists a uniformly sound randomized interactive verifier
           for all promised games in C_n, with stated YES completeness,
           NO soundness, and optional prover cost bound}.

Every proposed theorem must distinguish (i) a decision algorithm without a prover, (ii) an NP-style YES witness, (iii) a doubly efficient debate/interactive proof, and (iv) cryptographic commitments and their assumptions. A standard YES witness is the labeling itself; verifying one is linear in |E|. For the NO promise, the verifier's resources and soundness model are separate proof obligations.

### Established boundary

- **Information completeness is easy:** beta1 cycle values determine a gauge class; each query returns a single K symbol.
- **Exact optimization remains hard:** with K=F₂ and c_e=1 for every undirected edge, 1-phi_G(c)=MaxCut(G)/|E|. Exact phi is NP-hard although the full gauge signature is polynomial-time computable.
- **Conditional stronger gap:** if the claimed 2026 UGC theorem holds as stated, it implies fixed-gap hardness for the translation-game output even when full cycle coordinates are supplied, because those coordinates are computable from the explicit instance.
- Providing a proposed high-value labeling (an NP-style witness) changes verification costs. A conjecture that *all* certification is computationally hard would be false.

### Nontrivial frontier to characterize

Freeze a structurally restricted family (bounded treewidth, bounded graph cycle rank, locally expanding complexes, sparse cycle bases, or bounded graph separators), a gap promise and a proof model. Seek matching time/query/communication upper and lower bounds, plus an invariant parameter that predicts when gauge decoding admits efficient *certification* across both promise branches. A classification stated merely as "NP-hard in general" has already been exhausted by MaxCut.

**First falsifier:** compare exact cosystolic values, the signed spectral lower bounds and cycle ranks on small graph families; emit a witnessed example where an intended complexity parameter fails to order decoding difficulty. **First publishable output:** a structurally scoped polynomial-time verifier or parameterized lower bound with bit-complexity and completeness/soundness stated.

### Existing coverage and novelty gate

ASMP-9 asks if a reward gauge quotient is identifiable from behavioral access. ASMP-3 studies noisy weak verification. This candidate begins after **algebraic quotient recovery** and asks for a tight joint complexity/access frontier for one declared predicate. PCP theory, parameterized MaxCut, nearest-codeword decoding and unique-game SDP/SoS relaxations are mandatory comparators. It survives as a new top-level problem only with a theorem beyond these classical bounds.

---

## ASMP-14 (top-level contender): Local-to-Global Holonomy Oversight Capacity

### Safety question

How much nonlocality, persistent shared state or sample coordination must a bounded monitor purchase to distinguish a globally inconsistent agent/world from a locally consistent one?

### Frozen observation grammar

The environment hides the connection shifts c but discloses the graph and K. In each query the monitor chooses an edge set Q with |Q|<=r. An independent fresh uniform labeling a in K^V is sampled, and the oracle returns only the satisfaction bits (1[c_e=(da)_e]) for e in Q. Vertex labels, shifts and sample IDs shared across queries are **not** visible. Queries may depend on previous transcript answers, but fresh labelings prevent cross-query stitching. A more powerful extension explicitly prices (i) persistent-label access, (ii) direct loop-return queries, and (iii) trusted signed commitments to vertex labels.

For promised Safe/Unsafe classes and fixed query grammar A, define the worst-case composite error region under B calls and computational bound T. Require nontrivial completeness and a soundness margin on both classes, with per-call edge locality r, physical cost, and declared noise law. Test the minimal augmentation of A that makes uniform certification possible.

### Exact information-theoretic obstruction

Let ell(c) be the length of a shortest cycle with nonzero K-holonomy. For every Q with |Q|<ell(c), all edge subsets of Q are balanced. The joint law of its satisfaction bits under a uniform random labeling is exactly the same for c and for the flat connection c=0, by counting joint success events and inclusion-exclusion. Thus adaptive monitors in the stated fresh-sample grammar have **identical complete transcript laws**, at every query count B, for these two worlds.

A single frustrated cycle has phi=1/ell and so supplies a small but genuine gap. A **constant-gap, high-girth** existence control is also available for binary games: on any d-regular graph, choose independent uniform binary shifts. For any labeling, each edge is satisfied independently with probability 1/2. A union bound over 2^n labelings and Hoeffding gives

    Pr_exists_a [satisfied_fraction(a)>=3/4]
      <= exp(n log 2 - d n/16).

Hence for d>=12 the bound is <1, so some shifts have phi>1/4. Taking graphs of unbounded girth provides instances with a constant global frustration gap that are indistinguishable under any fixed-size fresh-label projector query. This is a standard probabilistic-method local-consistency phenomenon; the novelty target is the **priced augmented oversight frontier**.

### Nontrivial target and controls

Characterize the tradeoff among r, B, noise/correlation, ability to reuse the *same* labeling, direct holonomy access and attested transport of observations. A genuine positive result must choose one access grammar and achieve a worst-case separation of the Safe and Unsafe law sets. A negative result should give an explicit indistinguishable pair or a TV/deficiency lower bound. Include (1) flat vs frustrated C4, (2) a high-girth graph with large phi, (3) a full-cycle positive control, (4) shared-label reuse that defeats the original lower bound, and (5) correlated-error attacks.

### Existing coverage and novelty gate

ASMP-2 addresses transport of risk-relevant derivatives from source to deployment distributions. ASMP-7 addresses transformation-closed telemetry. Property testing, local-testability of cocycle codes, and SoS local-consistency lower bounds already study much of the mathematical core. The separate top-level contribution would need a **necessary-and-sufficient monitor resource region** for the specific hidden-connection observation grammar, including realistic sample linkage or additive noise. Merely proving forest marginal indistinguishability recovers known reasoning.

---

## ASMP-15 (provisional subproblem of ASMP-7/5): Descent-Safe Compactification

### Safety question

What additional certificate allows a consistency judgment made in a covering/compressed representation to descend soundly to the original system, including across a sequence of graph/model transformations?

### Exact baseline and failure witness

Let p:G'->G be a connected r-sheet graph cover, and let c'=p*c. A base labeling b pulls back to a labeling of G' with identical violated-edge fraction, so phi_G'(c')<=phi_G(c). The cover corresponding to ker(Hol_c) has degree |im(Hol_c)| and makes c' flat, **even when G is frustrated**. Hence perfect consistency after lifting does not by itself certify consistency of the base.

For any lifted labeling a':V'->K define its *fiber descent defect*

    eta_p(a') = min_(b:V->K)
                  #{x in V': a'(x)!=b(p(x))} / |V'|.

This can be computed by per-fiber modal labeling, with a deterministic tie rule. Let G have maximum degree D, n vertices, m>0 edge occurrences. Every lifted vertex disagreement can affect at most D lifted constraint occurrences, yielding the **exact elementary inequality**

    phi_G(c)
      <= bad_fraction_G'(a') + (D*n/m)*eta_p(a').

Together with phi_G'(c')<=phi_G(c), this shows why fiber descent agreement is a load-bearing certificate. On a d-regular base graph the additive coefficient is 2. The bound is nontrivial only when eta is small enough.

### New frontier

For an allowed semigroup of lift, quotient and edit transformations, characterize the *optimal* audit size and degradation law for descent defects across composition, including adaptive transformations and correlated measurement noise. Positive regimes need a shared, verifiable root coordinate and explicitly charged transport artifacts. Negative controls include a flat holonomy cover with large eta and a locally faithful quotient whose base frustration remains positive.

### Disposition

The exact inequality is an immediate counting argument. Since ASMP-7 already concerns transformation-closed attestability and ASMP-5 concerns compositional certificates, **treat ASMP-15 as their named geometry-specific subproblem** pending a sharply novel multi-step theorem.

---

## ASMP-16 (provisional subproblem of ASMP-11): Bounded-Degree Probes and Nonlinear Latent Invariants

### Safety question

Can a latent, equivariant safety-relevant code remain stable under perturbations that every accessible low-degree/high-rank monitor necessarily detects, and how does recursive composition change that separation?

### Frozen model

Let V=K⊕U with K=F₂^s and a K-equivariant latent code C:V->K, C(k+u)=k+q(u) after choosing a splitting. A fixed noise law mu on V is independent of x. Specify degree-d polynomial monitors F:V->F₂^m whose **restriction to K has a registered rank >=r**, and require monotone cost for m, degree and query count. Define

    p_C = Pr_(x uniform,a~mu)[C(x+a)!=C(x)],
    beta_d,r(mu) = inf_(admissible F) Pr[F(x+a)!=F(x)].

Ask for a sharp attainable frontier with p_C<=p and beta_d,r(mu)>=kappa at prescribed p, plus an adaptive repeated-probe version with a declared history/correlation class.

### Necessary negative controls

If deg(C)<=d and the monitor class permits F=C, then beta_d,r<=p_C for r<=s; any claimed fixed positive gap at arbitrarily small p fails. The conjecture therefore needs a latent algebraic degree beyond d or a substantive measurement restriction. For d=1, related nonlinear-noise results appear in the OpenAI UGC manuscript; the general-degree and adaptive-noise claims need independent proofs and hostile optimization over monitor families.

### Disposition

Strong overlap exists with ASMP-11 (interpretability access and conditional defection) and low-degree testing, including Reed–Muller/short-code constructions. **Maintain ASMP-16 as a possible ASMP-11 subproblem**, escalating to a top-level candidate only if a new hierarchy theorem survives counterexamples and yields an interpretable, physically constrained probe-access law.

---

## Admission, quantifier and prior-art gates

| ID | Proposed status | Distinct unknown | First positive/negative artifact |
|---|---|---|---|
| ASMP-13 | Top-level contender | Joint gauge-query, compute and proof-size frontier after quotient access | Bit-complexity-bounded structural theorem or hard counterfamily |
| ASMP-14 | Top-level contender | Sharp resource frontier for nonlocal/shared-label monitoring of hidden gauge systems | Exact indistinguishability plus priced augmented-access design |
| ASMP-15 | Subproblem of ASMP-7/5 | Multi-step robust descent certificate overhead | Counterexample to additive defect composition or optimal theorem |
| ASMP-16 | Subproblem of ASMP-11 | Higher-degree nonlinear observability versus monitored noise | Degree-two/three adversarial monitor search, with rank control |

The criterion for promoting one to a new ASMP is a **closed, nontrivial mathematical object** whose full statement remains after subtracting established MaxCut hardness, classical gauge/cohomology, random-cluster expansion, existing magnetic Cheeger bounds, local testability and the already frozen ASMP statements. Each candidate needs explicit theorem-versus-conjecture status, typed instance grammar with rational margins, finite-precision version, non-inert positive examples, and a fresh independent prior-art review. This draft performs no actual model intervention or training.

### Mandatory prior-art map

- [Lange et al., frustration index and magnetic Cheeger inequalities](https://doi.org/10.1007/s00526-015-0935-x): prevents rebranding a standard signed-Laplacian frustration bound as an ASMP.
- [First and Kaufman, cosystolic expansion of sheaves and locally testable codes](https://arxiv.org/abs/2403.19388): prevents claiming novelty for the existence of local-to-global cosystolic tests.
- [Dikstein and Dinur, degree/dimension-independent cosystolic expansion](https://eccc.weizmann.ac.il/report/2023/043/): relevant to alphabet-independent constants.
- [Lange/Liu/Peyerimhoff/Post; signed graph frustration-index optimization](https://www.sciencedirect.com/science/article/pii/S0166218X16304073): exact signed-graph and magnetic foundations.
- [Unique Games theorem manuscript](https://github.com/openai/math/tree/main/preprints/The-Unique-Games-Theorem-September-23-2026): conditional hardness and nonlinear noise ingredient; independent validation pending.

### Executable exact seed

The co-located Python module and unittest suite deliberately use only the standard library and certify small finite statements: gauge class counts, full versus partial cycle access, forest-observation blindness, the MaxCut embedding, covering flattening and the descent-defect inequality. These controls are mathematical sanity checks and a base for counterexample generation, rather than evidence that any top-level ASMP has been resolved.

## v0.1 sharp-bounds addendum, November 9, 2026

See [SHARP_VISIBILITY_AND_DECODING_BOUNDS.md](SHARP_VISIBILITY_AND_DECODING_BOUNDS.md) for new exact results and corrected candidate scopes. The **holonomy-image rank** is too weak a tractability parameter for ASMP-13: even rank exactly one supports NP-hard MAX-CUT instances. Graph **cycle rank** beta1 is a genuine positive parameter, with an explicit q^(2 beta1) forest/chord decoder.

For ASMP-14, a fresh uniform-label monitor that receives **all** ell Boolean satisfaction bits on a flat versus frustrated q-label cycle has exact total-variation separation (2/q)^(ell-1). This supplies a new alphabet-dependent sample barrier even beyond the original r<ell indistinguishability regime. When q=2 and readout bits suffer iid flips at rate eta, the exact full-cycle TV becomes |1-2eta|^ell. Both are elementary character/parity computations and are registered as negative controls, while the general priced monitoring frontier remains open.

## BM-01/02 observation-quotient and active recovery amendments

The [Boolean-monitor quotient theorem](BOOLEAN_MONITOR_QUOTIENT_BM01.md) characterizes the complete one-episode satisfaction-indicator law exactly: two F₂^s translation connections have identical laws if and only if they have identical families of balanced edge subsets. That information identifies the cosystolic optimum in principle but may leave numerical holonomy and minimal exact flat-cover degree ambiguous.

A connected cactus pair with t triangles has identical passive Boolean laws, yet minimum flat-cover degrees 2 and 2^t. Its graph and target are fixed, yielding a direct ASMP-14/15 zero-TV impossibility under the registered passive monitor. The distinction persists under unlimited adaptive queries on independent fresh uniform labelings.

The [active edge-shift recovery theorem](ACTIVE_PROBE_RECOVERY_BM02.md) introduces a *strictly stronger, charged interface*. A known shift x on one edge of a cycle reveals an exact equality test for the unknown holonomy h once the monitor can decide balance. Ideal balance-query reconstruction needs at most q-1 equality tests. The finite Bernoulli sampling version has an explicit one-sided detection budget, and the smallest cactus pair's Boolean TV rises from 0 to 1/4 after an intervention.

These are mathematical baselines built from classical biased-graph and elementary statistical testing arguments. The potential new ASMP is an adversarial, resource- and intervention-aware transition between passive and active monitoring, with costs for state restoration, tampering, measurement noise and certification of the actual intervention.


## BM-03/04 finite-sample and adaptive policy amendments

- [BM-03 exact noisy-monitor inference](FINITE_SAMPLE_MONITOR_BM03.md) strengthens the fixed-cycle iid sample theory. For binary labels and independent bit flips eta, the full-cycle parity observation has bias t=|1-2eta|^ell. Its exact N-sample Bayes error is a binomial majority tail, and the low-signal sample complexity for fixed confidence is Theta(t^-2). For arbitrary q the number k of failed edges is a sufficient statistic for flat-versus-nonflat testing, including iid BSC noise; exact rational multinomial histograms provide the optimum equal-prior risk.
- [BM-04 adaptive interventions](ADAPTIVE_MONITOR_BM04.md) demonstrates strict feedback value in a *frozen*, fully specified uniform-prior active holonomy search. For q=4 and a 3-cycle, two adaptive independent Boolean observations achieve Bayes identification success 189/512; the best fixed two-shift schedule achieves 183/512. An independent 256-policy exhaustive verifier checks the strict gap 3/256. This is an exact finite instance of established active multihypothesis experimental design.
- Correlated-noise null: a common bit flip on an even binary cycle preserves parity, while independent 50% flips destroy parity. Any generalized ASMP-14 theorem must declare the full error/correlation class.
- Further novelty is conditional on an independently priced intervention and attestation grammar, explicit worst-case error controls, and bounds beyond existing Chernoff/Le Cam/controlled-sensing results. The two new notes remain mathematical baselines rather than a promoted candidate or an empirical safety claim.


## BM-05 correlation-robust and restoration-aware monitoring amendment

[BM-05 exact minimax and audit baseline](ROBUST_MINIMAX_AND_AUDIT_BM05.md) addresses a core gap in the ASMP-14 proposal. A binary full-cycle monitor with arbitrary **within-episode correlated** bit errors of conditional per-edge probability at most eta has sharp least-favorable parity crossover p_star=min(L*eta,1/2), achieved by a zero/one-bit error-mask mixture. With this budget enforced after each history, a parity-majority test is minimax for N episodes. The resulting fixed-confidence sample scale is Theta((1-2Leta)^(-2)) when 0<1-2Leta<1. If the same error budget holds only *marginally* across episodes, a persistent hidden error mask gives a nonvanishing error floor.

Unknown persistent restoration drift d makes active responses depend on h+d rather than h. All chosen-shift experiments are invariant under (h,d)->(h+a,d+a), so a trusted external state anchor or independently justified restoration attestor is mandatory for original-state identification. With conditional false-restoration audit bounds rho_i, authorized false restoration probability is at most sum_i rho_i by the union bound.

A separate **costed Bayesian** active intervention design charges observation, shift-bit and independent restoration-audit units with a hard pathwise budget. Exact rational dynamic programming and an independent exhaustive two-step policy oracle agree on a q=4, L=3 experiment; the best allowed policy changes as the audit budget and unit price change. This Bayes calculation assumes sound audits and iid readout noise; it is an instrument for investigating the joint minimax frontier, not itself a claim of adversarially robust q=4 certification.

This remains a provisional ASMP research candidate with a clear novelty boundary: classical hypothesis testing, robust sensing and authenticated update semantics already cover its component mathematics. The missing theorem concerns their **joint** constrained game-space certification tradeoffs under a frozen, non-inert policy predicate.


### BM-05/T4 conditional certification gate

The [robust root-attestation certificate](robust_certification_gate.py) turns the exact conditional-noise minimax risk into a **two-sided, non-inert** acceptance rule, with independently justified per-step false-restoration-acceptance and genuine-restoration-rejection bounds. It refuses to certify when either the worst-case false-authorization target, the correct-authorization floor, or a hard intervention/audit resource budget fails. The [BM-05 note](ROBUST_MINIMAX_AND_AUDIT_BM05.md) gives a rational positive control: a four-edge binary cycle with conditional 1/16 per-bit error, three observations and three attested shifts has wrong-authorization bound 0.15925, correct-authorization lower bound 0.81375 and worst-case cost nine units. The bounds require a trusted root attestor with measured, conditional error guarantees; they remain a conservative finite certificate under an explicitly registered audit interface.


## BM-06 alphabet-general correlated observation and composite-certification amendment

The [BM-06 exact one-shot theorem](ALPHABET_CORRELATED_MINIMAX_BM06.md) generalizes the parity-error channel identity from binary to arbitrary q=2^s alphabets (the character-count argument also applies to any finite abelian group). The **entire** flat/nonflat Boolean pattern-law difference on one length-L cycle is the single parity Walsh character, so any hypothesis-blind, clean-input-independent XOR mask M contracts the exact total variation by the scalar absolute parity bias |E[(-1)^|M|]|. Under heterogeneous per-edge mask caps eta_i, the exact one-shot equal-prior minimax TV is (2/q)^(L-1) max(0,1-2 sum_i eta_i), attained by a mixture of no error and one-hot errors. The proof and tests explicitly restrict the noise channel to be the same under both hypotheses. A hypothesis-dependent mask counterexample shows why this scope matters.

For *separate* false-positive and false-negative requirements, the equal-prior scalar Bayes bound can be misleading. BM-06 implements an exact rational convex-polygon feasibility oracle for **randomized parity-only** tests under uncertain common mask noise. Its clean q=8,L=3 counterexample requires FP=21/32 and FN=9/32 under the equal-prior-optimal parity rule; the best symmetric parity-only risk is 21/44. Retaining the full failure-count statistic supports a strictly smaller clean symmetric minimax rate 1281/2720, proved by an exact likelihood-ratio policy and dual multiplier 43/85. These are textbook Fourier/Neyman-Pearson identities assembled into the monitoring access contract, and the unresolved ASMP target is the full adaptive/composite risk region for **hypothesis-dependent** correlated channels and independently attested interventions.


## BM-07 state-aware readout symmetrization amendment

[BM-07 hypothesis-aware symmetrization](HYPOTHESIS_AWARE_SYMMETRIZATION_BM07.md) upgrades ASMP-14's monitoring blind spots to an adversary that **knows the hidden flat/nonflat state and the chosen intervention** while remaining independent of the current fresh uniform labeling. This is a stronger channel class than BM-06's common/hypothesis-blind mask assumption.

On a two-edge parallel gain cycle over F2^s (q>=4), the exact one-shot minimax TV is max(0,2/q-2eta) under conditional per-bit readout cap eta, versus the common-channel expression (2/q)max(0,1-4eta). At q=8, eta=1/8, a flat-world one-hot noise mixture and a nonflat-world two-bit-flip mixture produce identical full Boolean output laws. This is the *exact* erasure threshold for that two-edge grammar.

An explicit Fourier construction extends to **simple cycles of every length L>=3**. Under hypothesis-aware readout masks, the full flat and nonflat Boolean laws become exactly equal at per-bit cap

    eta_construct=q*2^(L-2)/[(q-2)^L+c_L 2^L],
    c_L=q-1 (even L), c_L=1 (odd L).

For fixed q>4 this cap decreases exponentially like (q/4)*(2/(q-2))^L. At q=8, it is 1/14 on a simple triangle, 1/44 on a four-cycle and 1/122 on a five-cycle, all far below the common-channel erasure cap 1/(2L). This is a **sufficient constructed erasure cap** for L>=3, with optimality across all legal noise laws still open.

A state-aware readout attacker can choose the appropriate pair of masks after seeing each known intervention x and hidden gain h, giving identical complete conditional output laws for *all* h. Thus every adaptive intervention protocol based solely on those corrupted Boolean indicators has an h-independent transcript distribution, even with perfectly restored interventions. This is a registered asymptotic negative control for the proposed ASMP-14 active-monitoring frontier.

A partial constructive guarantee is also available when the two-edge cap eta<1/q: the number of episodes with mixed Boolean bits provides a robust **two-sided** test under conditional hypothesis-aware readout laws. Its false-positive/negative bounds are exact binomial tails and hold under history-adaptive noise, because each episode's conditional mixed-bit probability stays separated. For q=8 and eta=1/16, 31 fresh episodes and a threshold of six mixed observations give both conditional errors below 20%. The channel still requires independent fresh labeling, readout mask independence from the current clean sample, and independently authenticated shift/restoration actions.

This sharpens the ASMP admission target to a **symmetrizability-resistant oversight theorem** for a declared policy, graph ensemble, monitor channel, attacker knowledge, and priced interventions. Prior art on arbitrarily varying channels and adversarial hypothesis testing is explicitly cited in BM-07. The exact finite statements are an elementary specialization; no claim of a general AI-safety solution is made.


## BM-08 sharp symmetrization threshold: the cycle case is now closed

The [BM-08 exact lower-bound proof](SHARP_ERASURE_OPTIMALITY_BM08.md) completes the adversarial-readout **single-cycle** erasure problem left open after BM-07. For every cycle length L>=2 and q=2^s binary-vector labels, an adversary whose XOR readout mask may depend on flat/nonflat state but is independent of the current fresh uniform labeling can equalize the complete observation laws **if and only if** the uniform per-bit error cap satisfies

    eta >= eta_star(q,L),
    eta_star(2,L) = eta_star(4,L) = 1/(2L),
    eta_star(q,L) = q*2^(L-2) /
       ((q-2)^L + c_L*2^L)          for q>=8,
    c_L=q-1 if L even, else 1.

The old BM-07 parity-class mask construction is exactly optimal for q>=8, while a common unbiased one-hot mask achieves the *smaller* q=4 optimum. The lower bound holds for **all** correlated hypothesis-aware readout-mask distributions under the registered per-bit caps; it uses the full proper-subset Walsh identities to force a parity-character difference between the two mask laws, then charges the unavoidable Hamming weight of their nonoverlapping and shared odd-mask probability mass. Explicit mask witnesses and exact rational tests support the finite proof. The referenced BM-07 paper now carries this correction.

The outstanding ASMP-14 theorem consequently concerns *interacting cycles, costly interventions, adaptive state-aware noise, audit roots and non-inert safety predicates*. BM-08 resolves only this single-cycle statistical symmetrization subproblem and does not assert novelty beyond the existing adversarial-channel theory.


## BM-09 interacting-cycle obstruction: overlap matters beyond cycle rank

The [BM-09 exact theta-graph proof](THETA_CYCLE_INTERACTION_BM09.md) advances ASMP-14 from isolated gain cycles to a two-cycle shared-edge graph. On K_{2,3}, two independent fundamental cycles share edges and generate three four-cycles. In the contrabalanced q=4 connection with path gains (0,1,2), the exact state-aware readout erasure cap rises to **1/6**, versus **1/8** for an isolated frustrated four-cycle. The q=4 lower proof uses six five-edge and one six-edge Walsh constraints to force at least one expected flipped bit among six reports; an explicit common mask reaches the bound. For q=8 the exact cap is **29/630**, more than twice the isolated four-cycle threshold **1/44**, proven by complete integer-arithmetic primal and dual LP certificates. No solver is needed to verify them.

The geometry and gain assignment both matter. On the SAME q=4 theta graph, choosing one balanced four-cycle and two frustrated ones permits erasure at 1/8. A comparison graph consisting of two edge-disjoint frustrated four-cycles joined by a bridge also has cycle rank beta1=2 and erases at exactly 1/8, by factorization of independent cycle residual blocks. Thus beta1 alone does not predict the joint masking budget.

BM-09 introduces a proposed **symmetrization interaction index**
`I_q(G,c)=eta_sym(G,c;q)/max_{unbalanced C} eta_star(q,|C|)`, equal to 4/3 for the q=4 contrabalanced theta and 638/315 for q=8. A candidate next theorem would bound this index through the cycle-edge incidence hypergraph and Fourier weights. This remains a graph-family conjecture requiring prior-art review. The small exact results use a frozen hypothesis-aware clean-input-independent mask model and establish no operational AI safety guarantee.


## BM-10 weighted-Fourier diamond: Fourier zeros alone are insufficient

The [BM-10 five-edge diamond theorem](WEIGHTED_FOURIER_DIAMOND_BM10.md) adds an independently rationally certified third finite interaction example. For the q=4 theta graph with path lengths (1,2,2), three pairwise distinct path gains (0,1,2) and all three cycles frustrated, the sharp full Boolean-readout erasure cap is **eta_sym=1/5**. An explicit common mask law with denominator 20 attains the cap, and a sparse Walsh-domain dual with 17 Fourier multipliers, two normalization multipliers and five negative marginal multipliers proves the universal lower bound. Its interaction index relative to the shortest frustrated isolated triangle is **6/5**.

A proposed simpler lower-bound surrogate that checks only **where frustrated-world Fourier coefficients vanish while flat-world coefficients do not** fails on this same graph. Its exact zero-set is S={30,31}, and the relaxed mask LP has exact optimum **1/8**, with a constructive mask distribution satisfying both zero constraints. The complete output laws remain different under that surrogate mask; full Fourier-weight compatibility is responsible for the 1/5 erasure cost. The underestimation factor is **8/5**. A 64-atom rational dual check and independent full-label enumeration substantiate this result.

BM-10 proposes a more defensible open graph-family question: find sparse analytic or fixed-parameter-size **weighted Fourier dual certificates** for readout-erasure cost with a provable approximation factor in terms of cycle-edge overlap structure. The general finite linear-program dual characterization is elementary. Proving a genuinely structural approximation theorem, or finding a counterfamily to any frozen overlap-width hypothesis, remains the novel research task. The 5-edge diamond, 6-edge K_{2,3}, independent cactus and isolated cycle become mandatory calibration/negative-control instances. Neither rank beta1 nor the locations of Fourier zeros suffice as stand-alone predictors.


## BM-11–13: block decomposition, two-terminal Fourier transfer and sparse exact certificates

The latest ASMP-14 mathematics localizes the difficult part of the symmetrization problem to cyclic graph blocks.

- **[BM-11 articulation theorem](BLOCK_TENSOR_ERASURE_BM11.md):** for a one-vertex sum `G=A vee B`, the flat/frustrated complete Boolean satisfaction laws factor. The exact hypothesis-aware correlated-mask erasure cap is therefore `eta_sym(G)=max(eta_sym(A),eta_sym(B))`. This is proved for the registered fresh uniform-label/readout interface by projection and independent product attaining masks. A 4-label diamond (cap 1/5) glued to a 4-label contrabalanced theta (cap 1/6) gives an **8-vertex, 11-edge, cycle-rank-4** graph with exact cap **1/5**. Independent enumeration of 4^8 vertex assignments verifies all 2048 output law values. The diamond's 17-Walsh-term original lower dual lifts unchanged to all 4096 global mask-atom constraints, with no new multipliers.
- **[BM-12 theta transfer](THETA_FOURIER_TRANSFER_BM12.md):** for k internally disjoint paths meeting at two terminals, each individual Walsh coefficient is computed by conditioning on the terminal label difference and expanding at most **2^k** equal-gain path subsets. The full pattern-law Fourier table depends on path gains only through their equality partition. Independent oracles validate every coefficient on q=4/q=8 theta/diamond examples, plus mixed-length networks. This is a coefficient oracle; the full erasure LP remains exponential in total observed edges.
- **[BM-13 sparse certificates and degree hierarchy](SPARSE_FOURIER_DEGREE_BM13.md):** replace BM-10's 17-term diamond dual by a **new 8-term** exact rational lower certificate for cap 1/5. A **5-term** exact dual with three four-cycle and two five-edge supports certifies the q=4 theta cap 1/6. The exact degree-d Fourier relaxation thresholds are: diamond `(0,0,0,1/6,1/5,1/5)` for d=0..5, and theta `(0,0,0,0,1/8,1/6,1/6)` for d=0..6. Every value has explicit primal masks and either a BM-08 single-cycle lower bound or a sparse exact dual. Eight/five are achieved support sizes, with **no claim of minimum dual sparsity**.

**Revised open ASMP-14 frontier:** On graph families with biconnected blocks of bounded internal cycle-overlap/terminal width, determine whether a weighted Walsh dual with `f(width,1/epsilon)poly(n)` coefficient support can certify an epsilon-approximate erasure bound with stated rational bit complexity and a compatible achieving mask. The BM-11 one-sum theorem removes articulation-block overhead exactly, and BM-12 provides cheap individual Fourier coefficient queries on multi-path blocks. BM-10's zero-location-only failure remains a required hostile control. The three results are classical finite decomposition, transfer, and LP-duality specializations; the general certificate-width theorem has not been established.


## BM-14 fixed-path-width exact certificate-size theorem

The [BM-14 path-orbit LP](PATH_ORBIT_LP_BM14.md) gives an **exact polynomial-size full erasure program** for a nontrivial family of 2-connected gain graphs. Fix k internally vertex-disjoint paths between two terminals, of lengths L_i, with q=2^s labels and fresh uniform vertex-label observations. Each clean Boolean path pattern is invariant under permutations of the L_i edges in its path, even with nonzero total gain. Averaging **hypothesis-aware, correlated and current-sample-independent** adversarial mask distributions under those same permutations preserves their complete-output equality and per-bit error caps. Thus the exact erasure LP admits an optimum constant on mask-weight classes t=(t_1,...,t_k) with **M=product_i(L_i+1)** classes per hypothesis.

Binary Krawtchouk orbit kernels give all complete-output Walsh equality constraints from the BM-12 path Fourier coefficients, yielding **2M+1 LP variables, M+1 equality rows and 2k marginal inequalities**. For fixed k, generic rational LP therefore computes the exact optimum with polynomial bit complexity in edge count m and log q. The dependence grows like O(m^k) when k varies (an XP structural result, **not an FPT theorem** in k). The dual has at most M Walsh *orbit signatures*, which are compact encodings of permutation-averaged full Fourier certificates rather than a statement of sparse individual Walsh support.

A matching code implementation constructs the exact rational matrix, tests primal feasibility using full orbit Walsh constraints, verifies dual feasibility across all 2M mask-orbit atoms, and independently reconstructs output count laws through hypergeometric mask transitions. The earlier BM-09 q=4/q=8 theta and BM-10 diamond optimum witnesses survive exact symmetry averaging; their BM-13 eight/five-term full Walsh duals compress to **six/four orbit signatures** at the same exact objectives. A q=4096, 31-edge three-path example L=(12,10,9) reduces the per-world mask states from 2^31 to **1,430**, giving an LP of **2,861 variables**, **1,431 equalities** and **six marginal constraints**. The large example is a structural cost estimate only; no full numerical LP solution is claimed.

The remaining proposed **ASMP-14 certificate-width theorem** should extend beyond multi-theta blocks to graph families with bounded internal overlap/separator width, with rigorously quantified bit complexity, approximate/optimal dual support and independent root-attestation constraints. BM-14 uses established group averaging, Hamming association schemes and Krawtchouk symmetrization; separate novelty review is mandatory.


## BM-15 and BM-16: Exact Fourier transfer across series-parallel and general small separators

[BM-15 series-parallel gain-spike transfer](SERIES_PARALLEL_GAIN_TRANSFER_BM15.md) extends BM-12's conditional terminal-difference Fourier oracle from parallel u-v paths to **arbitrary nesting of two-terminal series and parallel gain graphs**. Every selected-edge Fourier message is a uniform constant background plus a sparse collection of indicators of exact terminal gain differences, `F(d)=a+sum_g b_g 1[d=g]`. Parallel graph composition multiplies these messages pointwise; series composition takes their normalized K-convolution. The gain-spike class is closed under both operations, and the unconditional Walsh coefficient is `a+sum_g b_g/q`. A targeted nested-network control shows the BM-14 path-permutation symmetry can fail within an outer branch when that branch contains an internal frustrated parallel cycle. The individual coefficient oracle avoids full vertex-label enumeration, with cost charged to the potentially exponential intermediate spike support. It supplies **no polynomial-size full erasure-LP claim**.

[BM-16 general separator Fourier elimination](SEPARATOR_FACTOR_TRANSFER_BM16.md) handles **arbitrary finite gain graphs**, including K4 and a Wheatstone bridge, using exact normalized elimination of uniform vertex labels in a chosen order. For each selected edge subset S, its Fourier coefficient is the expectation of the product of `1-2 1[e satisfied]` factors. Under induced elimination width w, a single coefficient costs `poly(n,m) q^(w+1)` rational operations, with explicit q-dependence and checked boundary-message tables. A min-fill ordering on the q=4 K2,3 theta uses joined scopes of three variables; a deliberately poor order joins four. K4's entire q=4/q=8 64-subset Fourier table, Wheatstone three-boundary conditional tables, and all 32 Fourier subsets of BM-15's nested SP graph match independent full-label enumeration. A q=32 long-chain width-one control demonstrates q^2 temporary state size rather than complete vertex enumeration.

**ASMP-14 refined structural frontier:** BM-11 removes articulation-block erasure costs exactly; BM-14 gives a polynomial-size **full** erasure LP only when an exact gain-path permutation symmetry survives; BM-15 and BM-16 broaden the **coefficient oracle** to arbitrary TTSP and low-treewidth graph structure. The remaining theorem must connect bounded separator/overlap width to verifiable approximate/optimal hostile-mask **primal and dual** representations with explicit alphabet size and error-contract assumptions. A treewidth-bounded Fourier coefficient oracle alone cannot establish the requisite 2^m mask-variable compression. No ASMP prize admission or empirical AI safety claim follows from these finite mathematical primitives.


## BM-17 full Fourier degree obstruction on K4

The [BM-17 exact K4 certificate](K4_FULL_DEGREE_OBSTRUCTION_BM17.md) is a new finite hostile-control instance for the proposed ASMP-14 certificate-width theorem, continuing BM-16 beyond two-terminal series-parallel graphs. Fix the 4-vertex complete graph K4 (six edges, treewidth three, cycle rank three), alphabet K=F2² (q=4), and gain shifts (0,0,0,1,2,1) against the flat connection. All four triangles are frustrated. Define eta_d as the minimum uniform per-bit readout-error allowance needed for hypothesis-aware, current-clean-sample-independent correlated XOR masks to equalize **all Walsh coefficients of degree at most d**, with the same marginal-error constraints for every d.

The **exact** degree profile is

    eta_0=eta_1=eta_2=0,
    eta_3=1/6,
    eta_4=1/5,
    eta_5=4/19,
    eta_6=3/14.

The final degree-six Fourier constraint increases the optimum by **1/266** above degree five. This directly refutes any general shortcut that stops at degree m−1 (which had happened to suffice for the BM-13 diamond and theta instances). The q=4 K4 full erasure interaction index is 9/7 relative to its unbalanced shortest triangle.

New [generic exact primal/dual Fourier erasure checker](generic_fourier_erasure_BM17.py) and [four fully rational K4 primal and dual data sets](k4_high_degree_BM17.py) certify every nonzero degree optimum by exact weak LP duality. The optimized full-degree witness uses an identical mask law under both hypotheses with integer denominator 56 and six marginals each equal to 3/14; the degree-five attaining distributions differ by hypothesis and still leave the complete output six-edge character distinguishable. The independent BM-16 factor-elimination oracle verifies every one of the 64 clean Walsh coefficients for both worlds; the certificate checker verifies all 128 mask-atom dual inequalities at each degree. The finite optimality computation uses standard LP theory and makes no general hardness claim.

**ASMP research consequence:** even a width-three, 2-connected graph can need full-order weighted Fourier constraints to certify the exact hostile-mask erasure optimum. A bounded-separator *coefficient oracle* therefore does not imply a low-degree approximation scheme for the whole erasure LP. Further graph-family work must specify a quantitative degree/certificate-size approximation claim, including algebraic gain relationships, graph size, separator width, and the adversarial readout information model, and test it against BM-17's explicit rational negative control.


## BM-18 universal Fourier completion and sharp radial noise bounds

The [BM-18 general postprocessing theorem](UNIVERSAL_FOURIER_COMPLETION_BM18.md) gives a graph-independent **quantitative** completion guarantee for the ASMP-14 hostile-readout erasure LP. If eta_d is the least per-bit corruption allowance that equalizes *all* flat/nonflat Walsh moments up to degree d among m Boolean edge reports, then

    eta_m <= eta_d + (m-d)/(2m) * (1-2eta_d).

Constructively, after any attaining pair of hypothesis-aware degree-d mask laws, apply the **same independent common mask** formed by choosing m-d random coordinates uniformly and flipping those coordinates with independent fair coins. Every remaining high-degree Walsh character intersects the chosen subset and is annihilated; all previously matched low-degree characters remain matched. The extra per-coordinate error probability is (m-d)/(2m), and its XOR composition with the original mask establishes the formula. This upper bound is **sharp** for q=4 isolated m-cycles with d=m−1: eta_(m-1)=0 while eta_m=1/(2m).

The optimal universal higher-degree annihilator itself has a polynomial-size exact rational Krawtchouk LP: by full coordinate permutation symmetrization, use **m+1 Hamming-weight orbit masses** w_t with high-character equalities at degrees d+1..m and objective sum_t(t/m)w_t. A matching **m+1-inequality dual** certifies its optimum. Exact closed forms include r*_(m,m−1)=1/(2m) and r*_(m,m−2)=1/m, proved by parity moments and matching random-subset masks. Small nontrivial exact primal/dual fixtures improve the uniform construction, including r*_(5,2)=1/4 (versus 3/10), r*_(6,3)=5/24 (versus 1/4), and r*_(8,4)=5/26 (versus 1/4).

The [executable BM-18 verifier](fourier_completion_BM18.py) checks radial Krawtchouk primal/dual feasibility, produces polynomial-size samplers for the universal masks, and independently convolves the **actual BM-17 K4 / BM-13 diamond and theta** partial masking witnesses into complete-erasure mask laws with exact probability checks. It also checks matching single-cycle sharpness and failed certification for malformed inputs. The strongest general bound uses the exact radial optimum r* in place of the uniform construction's (m-d)/(2m).

**Research consequence:** the absence of high Fourier constraints has a bounded additional *masking cost*, and that cost has its own efficient graph-independent auxiliary LP. This does **not** prove the desired width-parameterized algorithm for computing graph-specific eta_d: to make the simple additive upper gap <=epsilon one typically needs d>=m(1−2epsilon), and the truncated erasure LP may still be exponentially large. The next structural problem is **support-aware completion**, where one annihilates only the graph-specific remaining Fourier discrepancies and seeks explicit small-width primal/dual certificates. The theorem uses classical Boolean Fourier and Delsarte/Krawtchouk techniques, with no independent novelty or empirical AI-safety claim.


## BM-19 exact support-aware common-mask completion after frozen monitoring policies

The [BM-19 support-specific Fourier completion theorem](SUPPORT_AWARE_COMPLETION_BM19.md) strengthens BM-18 for an actual graph/partial-mask pair. Given two already masked observation laws `F0=P0*Q0`, `F1=P1*Q1`, freeze their **nonzero residual Fourier discrepancy support** `D={S:hatF0(S) != hatF1(S)}`. Applying an additional **common independent** XOR mask R exactly equalizes the complete laws iff `hatR(S)=0` for every S in D. The optimal additional maximum per-edge flip rate `r*(D)` is a rational LP with `2^m+1` variables, `1+|D|` equalities and m marginal inequalities. A matching exact dual is checked over all `2^m` mask atoms. This LP optimizes the *postprocessor for the frozen original Q0,Q1*, and its optimality is distinct from globally reoptimizing the full erasure LP.

A sharp analytic example is the q=4 six-edge K4 after its BM-17 degree-four partial mask. The actual residual support is **D={47,61,63}**. A remaining size-five character forces additional per-bit error at least **1/10** by a parity union bound; an eight-mask common channel with denominator 20 erases all three remaining characters at **exactly 1/10**, with a one-character rational dual proof. The optimal **universal** BM-18 degree-four completion costs 1/6. Because the original partial mask has per-bit rate 1/5, the support-aware completed readout cap is **13/50** versus the universal **3/10**; BM-17's globally reoptimized full-erasure optimum remains **3/14**. Keeping these three optimization scopes separate is a required claim boundary.

Five exact rational primal and dual postprocessor certificates are committed: K4 degree 3 has `r*(D)=7/38` (strictly below universal `5/24`), K4 degree 4 has `1/10` (below universal `1/6`), K4 degree 5 has `1/12`, diamond degree 3 has `1/5` and theta degree 4 has `1/6`. The last three match their universal completion rates and serve as negative controls. Independent exact tests reconstruct D from complete output convolution, check each LP matrix and dual, and verify complete final Boolean output equality after applying the common postprocessor.

**New ASMP-14 structural target:** exploit the residual *hypergraph* of Fourier character supports. Column generation for the support-aware LP requires separating a weighted parity polynomial on Boolean mask choices. A meaningful bounded-width theorem should bound that separation problem using a frozen width parameter of **D**, produce both a valid attaining mask and rational lower certificate, and state its approximation/bit complexity. The original graph treewidth alone has not been shown sufficient to control the support-hypergraph separation cost. BM-19 uses classical Fourier convolution, hypergraph parity and LP duality; no empirical AI safety conclusion is claimed.


## BM-20 residual-support treewidth: exact dual separation and sparse primal theorem

[BM-20 weighted parity separation](PARITY_WIDTH_SEPARATION_BM20.md) closes a **restricted, explicit-support version** of the ASMP-14 certificate-width problem. After freezing an existing partial readout-mask pair, the residual Fourier support D determines the BM-19 common-postprocessor LP. Its dual feasibility requires `y0+sum_(S in D) y_S (-1)^|S∩x|+sum_i z_i x_i<=0` for every Boolean mask x. This is a weighted parity-CSP on the m reported-bit indices, where each Fourier support S is a hyperedge.

An exact max-sum variable-elimination oracle over the D interaction hypergraph, with a supplied induced-width-w order, finds the **maximal dual violation and an attaining Boolean mask** in `poly(m,|D|)2^(w+1)` rational arithmetic. Existing BM-19 duals, random signed parity programs and adversarially falsified witnesses are tested against direct 2^m enumeration. A 128-bit chain of 127 active parity factors, plus a 256-bit chain, have two-bit maximum factor scopes under a linear elimination order. The code reports exact maximum slack, witness mask, actual width and assignment work, aborting if factors exceed a declared cap.

Combined with classical Grötschel–Lovász–Schrijver rational optimization/separation equivalence, this establishes a **theoretical FPT-in-w exact LP optimization algorithm** for *explicitly supplied* support D with a width-w decomposition. The committed code implements the **separation oracle and direct finite certificate checks**, not the ellipsoid optimizer/recovery pipeline. The general finite LP has 2^m mask columns but only m+|D|+1 dual scalar variables. Independently, rational Carathéodory support reduction proves and constructively checks that every feasible postprocessing mask law admits an equivalent law on **at most 1+|D|+m atoms**, preserving all registered Fourier zeros and **every individual flip marginal**. A dense 64-atom finite mask is compressed to <=10 atoms with exact moment controls.

A solved infinite family supplies a nontrivial positive benchmark: if D contains all consecutive pair characters of an m-bit path, its interaction graph has width one and the exact postprocessing optimum is **r*=1/4 for every m>=2**. Choose zero mask with probability 1/2, flip the even-index color class with probability 1/4, or flip the odd-index class with probability 1/4. A one-character rational dual matches the elementary two-bit union-bound lower proof. The construction works for any nonempty bipartite graph of pair-character supports, even where its treewidth is larger, showing width is sufficient but not necessary for a compact certificate.

**Research boundary:** the width in this theorem is the treewidth of the **explicit residual Fourier support hypergraph**, not the original gain graph. Efficiently deriving D from an implicit large monitoring system, coordinating the *original* hypothesis-aware masks, and incorporating independently authenticated costly intervention/restoration remain open. This is classical parity-CSP and LP oracle mathematics specialized to BM-19's frozen postprocessing channel, not an admitted ASMP solution or demonstrated model safety.


## BM-21: Implicit Fourier support circuits and an exponential-output obstruction at graph treewidth two

The new [BM-21 cactus support theorem and independent tests](IMPLICIT_CACTUS_SUPPORT_BM21.md) address the unresolved **Fourier-support extraction** step before BM-20's explicit-support parity separation oracle. For any finite F2^s gain graph and edge subset S, exact inclusion/exclusion over constrained subgraphs gives

    W_c(S) = sum_(T subset S, gain-balanced T)
                    (-2)^|T| q^(-rank(T)),
    Delta_c(S)=W_0(S)-W_c(S)
              =sum_(T subset S, gain-unbalanced T)
                    (-2)^|T| q^(-rank(T)).

Consequently every nonzero clean residual Fourier character contains an unbalanced cycle, and each simple unbalanced cycle C is itself a minimal nonzero character with `Delta_c(C)=(-2)^|C|/q^(|C|-1)`. Cycle containment is **necessary but not generally sufficient**, since larger terms can cancel. A weighted-union-find implementation of this standard rank identity independently reproduces BM-17's entire q=4 K4 Walsh table.

On **cactus graphs**, whose simple cycles meet at articulation vertices and have disjoint edge sets, the full Boolean satisfaction law factors over cycles and bridges. Its Walsh coefficients have an exact **linear-size product circuit** in terms of selected-edge counts on each cycle. For q=4, residual membership has the closed Boolean rule: a discrepancy occurs if some **frustrated even cycle** is fully selected, or the number of **fully selected frustrated odd cycles** is odd. The number of residual Fourier characters has an explicit closed-form product/count formula, evaluated without listing their supports. For two frustrated triangles joined at a vertex, selecting both full cycles yields **zero** discrepancy because their odd-cycle sign reversals cancel; the six-edge graph has exactly **14** residual support indices.

A single frustrated triangle with t attached bridge edges has graph treewidth **two**, but at q=4 its exact residual-support family is `D={S:C subset S}` and **|D|=2^t**. Its largest hyperedge is the entire edge set, making the Fourier-support interaction hypergraph a clique of size **t+3** and treewidth **t+2**. A symbolic **253-edge fixture with 250 bridges** returns the support count `2^250` and exact full-edge coefficient `-1/2^251` without any Fourier-table or vertex-label enumeration. For q=2 the bridge coefficient vanishes and this family's support reduces to the single cycle character. This is a rigorous negative control against assuming that bounded **original graph** treewidth implies small **explicit** residual support or small residual-support interaction width.

For a cactus, the optimal **common independent postprocessor** has exact per-edge cap `max_(unbalanced cycles C) 1/(2|C|)`. Independent one-hot half-probability masks on the disjoint frustrated cycles attain it; a single cycle-character parity union bound proves sharpness even against arbitrary correlated common masks. A symbolic full-erasure proof checks each local Fourier factor without enumerating D. The sharp lower certificate uses just the shortest cycle character, with a dual that BM-20 verifies at **active width two** for the 253-edge triangle fixture, despite the full residual hypergraph having width 252. More strongly, by BM-08's sharp hypothesis-aware cycle result and BM-11 block tensorization, the exact fully hypothesis-aware cactus erasure cap is `max_(C unbalanced) eta_star(q,|C|)`. Explicit world-specific masks for **two q=8 frustrated triangles** attain **1/14** per edge, compared with the common-mask optimum **1/6**; independent full Boolean output tests verify equality.

**Revised ASMP-14 frontier:** a useful complexity measure should distinguish original-graph separator width, explicit residual-support size/width, **compressed support grammar size**, and **active primal/dual certificate width**. BM-21 supplies a complete positive algorithmic benchmark for cactus supports and an exponential-output counterexample at treewidth two. The open challenge is extending symbolic support extraction and optimizing the *joint* hypothesis-aware masking/intervention problem on genuinely overlapping-cycle 2-connected blocks, with external trusted-root audit constraints kept explicit. These are finite applications of established gain-graph, graphic-matroid and Fourier facts, with no independently verified new UGC or AI-safety theorem.


## BM-22: 2-connected theta support circuits and a sharp even-path adversarial erasure formula

[BM-22's theorem and independently tested implementation](IMPLICIT_THETA_SUPPORT_BM22.md) extend BM-21 beyond cactus graphs to **2-connected theta networks with overlapping frustrated cycles**, while retaining a compact implicit Fourier support representation.

For a theta of k internally vertex-disjoint paths with lengths L_i, denote by J(S) the paths entirely included in a selected Fourier edge set S, and by b(S) the number of selected edges on remaining proper paths. Conditional terminal-difference independence yields **exactly** `W_h(S)=(1−2/q)^b(S) * F_h(J(S))`, where F_h(J) is a gain-grouped terminal average over only fully selected paths. Because F_h(J) can be evaluated in O(k²) rational operations for each of 2^k subsets J, the **clean residual Fourier support** is represented by at most 2^k path-classes. For q>2 its exact size is `sum_(J:F0(J)!=F1(J)) product_(i notin J)(2^Li−1)`. The q=2 case has a simple modification because properly selected path characters vanish whenever a positive number of proper edges is selected. This gives polynomial-time support-count/membership for fixed k without enumerating 2^m Fourier subsets, even with overlapping cycles.

For **q=4 and three pairwise distinct frustrated path gains**, every Fourier subset containing **exactly two complete paths** has nonzero clean discrepancy, while complete selection of all three cancels precisely when *one path is even and two are odd*. Thus `|D|=sum_i(2^Li−1)+1[not exactly one even]`. This holds regardless of path lengths. A 266-edge odd/even cancellation fixture has zero full-edge discrepancy while its D interaction hypergraph is still a complete clique through pairwise full-path supports.

**New exact erasure theorem:** if the three path lengths are **even**, the q=4 flat-versus-three-distinct-path-gains **fully hypothesis-aware** erasure threshold is
`eta_sym=max(1/(L0+L1+L2), 1/(2*min_{i<j}(Li+Lj)))`.
Its lower proof combines BM-08 projection with zero frustrated Walsh coefficients for the entire theta and each *complement-of-one-edge* subset, forcing the flat-world mask to flip at least one edge on average. Its upper proof constructs a **common** readout-mask law from only eight path activation patterns, then chooses one uniformly random edge on each activated path. The activation distribution's order≥2 Walsh moments vanish, erasing every clean discrepancy. Exact rational tests verify direct full Boolean output equality on small theta graphs and symbolically check this sharp formula for arbitrary even lengths.

A **360-edge 2-connected treewidth-two theta** with path lengths (120,120,120) has clean discrepancy support of size `3*(2^120−1)+1`, full residual-interaction hypergraph width **359**, yet sharp common and state-aware complete-erasure cap **1/360**, with an eight-state sampler and closed-form lower certificate. This extends BM-21's exponential-output obstruction to a genuine overlapping-cycle graph with **no articulation point**. BM-22 also implements exact post-readout residual-membership queries under arbitrary finite explicit mask pairs, and exact **counting** under BM-14 pathwise exchangeable mask-orbit channels in `product_i(L_i+1)` signature work for fixed k. BM-19 diamond/theta partial-residual counts and BM-09 q8 fully erasing state-aware masks are registered controls.

**Remaining ASMP-14 frontier:** symbolic support/certificate algorithms for multi-terminal 2-connected cyclic blocks without theta path exchangeability, with honest separator/gain-width resource accounting and matched verified hostile-mask upper/lower certificates. The specialized theta theorem uses established gain-graph and Fourier methods and is not an independent UGC, model alignment, or authenticated intervention result.


## BM-23 fixed-core subdivision: exact polynomial-size LP beyond theta networks

The [BM-23 fixed-core erasure theorem](FIXED_CORE_SUBDIVISION_BM23.md) extends BM-14's exact Krawtchouk orbit LP beyond two-terminal theta networks to **subdivisions of any fixed gain-graph core H**, including biconnected non-series-parallel K4 networks with three or more terminal vertices. Each of H's k edges is replaced by an internally vertex-disjoint path of length L_e. Conditional on core labels, each replacement path's residuals are uniform under a fixed XOR sum, so the full clean Boolean law is invariant under `product_e S_(L_e)` edge-coordinate permutations. Averaging arbitrary hypothesis-aware, current-clean-independent correlated error masks under this symmetry preserves complete output erasure and uniform per-edge budgets. The exact full erasure LP therefore has `M=product_e(L_e+1)` path-count mask classes per world, `2M+1` primal variables, `M+1` Walsh equalities, and `2k` per-path marginal constraints.

The exact clean Walsh coefficient at selected edge set S is `(1−2/q)^b(S)*F_h(J(S))`, where J(S) is the set of **fully selected** replacement paths and b(S) is the number of selected edges on proper paths. Expanding each full-path factor in its endpoint-gain indicator yields an exact **gain-balanced core-subgraph rank sum** over T⊆J, involving at most `3^k` balanced-subgraph terms across all J, with no q^vertices uniform-label census. This gives a concise exact **clean Fourier support count**: for q>2, `|D|=sum_(J:F0(J)!=F1(J))product_(e notin J)(2^Le−1)`. For fixed core size k the resulting full rational LP is polynomial in total edge count m and log q. The direct construction scales like m^k for varying k and hence carries an **XP rather than FPT** parameterization claim.

A sharp worked nonseries-parallel family improves the benchmark: use BM-17's four-label K4 core with gains `(0,0,0,1,2,1)` and replace its edge 01 by an L-edge path. The exact hypothesis-aware erasure cap is **3/14 at L=1** and **1/5 for every L>=2**. The projected K4-minus-edge **contrabalanced five-edge diamond** from BM-10 forces the universal lower 1/5. For L=2, a 21-orbit exact rational **common-mask** witness with denominator 40 attains it; for all L>=3, the BM-10 diamond eraser with cap 1/5 composed with an independent fair one-hot parity mask on the long path at cap 1/(2L) achieves the same threshold. Every Walsh character is erased by the long-path mask if it selects the entire long path, or by the diamond mask after the proper-path forest factorization otherwise. Independent q4 full output-law checks validate small L.

For L=120, this K4 subdivision is still **2-connected and treewidth three**, with 123 vertices and 125 observed edges. Its clean Fourier support exceeds `2^120` indices while the exact state-aware threshold remains **1/5** and its common eraser has a compact sampler. The full erasure LP has 3,872 orbit classes per world rather than `2^125` masks, and an available rational matrix with 7,745 primal variables; its sharp optimum is established symbolically without solving the large matrix. BM-23 validates the original K4 BM-17 exact primal **and dual** inside its generalized orbit code, checks every small q4/q8 subdivided K4 and Wheatstone coefficient against independent full-label census, and includes BM-12 parallel-path recovery controls.

**Revised open ASMP-14 frontier:** the fixed-core polynomial-size theorem has moved beyond theta to non-series-parallel multi-terminal networks. The remaining structural question concerns **variable-size cores**, where k grows with graph size, and the fully joint hypothesis-aware mask-and-audit optimization may have no small path-orbit representation. BM-23 is finite gain-graph and Krawtchouk/LP mathematics; no new UGC proof, empirical oversight result or independent novelty certification follows from the exact statements.


## BM-24: Exact full erasure LP with a variable-size, repeated-type theta core

The [BM-24 theorem and exact code](WREATH_THETA_SYMMETRY_BM24.md) extend the BM-23 fixed-core LP to a nontrivial family where the **number of core paths k grows**. Whenever several internally vertex-disjoint u-v paths have the same joint type `(length L, hidden-gain pair g0/g1)`, their complete Boolean satisfaction laws are invariant under **both** edge permutations within paths and permutations of whole paths of that joint type. Each type of multiplicity n has a wreath-product orbit indexed by the histogram of per-path Hamming counts 0..L, with **binomial(n+L,L)** mask classes. The complete hypothesis-aware correlated but current-clean-independent erasure LP reduces exactly to `M=product_types binomial(n_type+L_type,L_type)` orbit classes per world, `2M+1` variables, `M+1` Fourier and normalization equalities, and `2r` per-type marginal constraints. Multivariate Krawtchouk orbit coefficients are evaluated with exact rational hypergeometric assignment DP. A grouped endpoint-difference Fourier calculation avoids q^vertices uniform-label enumeration.

For **fixed number r of joint types and bounded maximum path length**, this yields a polynomial-size full rational LP and standard exact LP optimization polynomial in the number of growing core paths and log q. With fixed q and all paths length L, the maximum number of joint gain types is q². The direct complexity grows as k^(r L_max) when those parameters vary, so the result is **XP rather than FPT** in r/L_max. It requires full within-type exchangeability and equal per-edge error budgets; per-edge identity-sensitive interventions can break the quotient.

A sharp analytic positive benchmark uses **n ordinary length-L paths with gains (0,0)** and **one exceptional length-L path with gains (0,gamma)**, where gamma!=0. A compact two-branch common mask either independently activates each ordinary path with probability 1/2 (leaving the exceptional path untouched), or activates only the exceptional path with probability 1/2, flipping one uniformly selected edge on every activated path. The initial branch choice is equiprobable. Every edge flips with probability **1/(4L)**. Any clean Fourier distinction needs the exceptional path fully selected and at least one ordinary path fully selected; one of those requirements is annihilated in each mask branch, giving complete output-law equality. The common-channel cap **1/(4L) is sharp for every q** by the odd-parity union bound on any frustrated 2L-cycle. For q=2 and q=4, the BM-08 single-cycle state-aware lower bound is also 1/(4L), so **the fully hypothesis-aware optimum equals 1/(4L) for all n>=1**. An independent **one-Fourier-character rational LP dual** proves the q4 lower bound directly: its support is the 2L-cycle formed by one ordinary path and the exceptional path, with flat Walsh coefficient `2^(2−2L)` and frustrated coefficient zero; checking the 2L+1 parity cases proves every mask inequality.

For q>=4 with L=2, the exact **clean Fourier discrepancy support count** is `4^n−3^n`. A registered q4 example with **250 ordinary paths plus one exceptional path** has 253 vertices, 502 edges, cycle rank 250, clean support `4^250−3^250`, and **94,878** histogram mask classes per hidden world. This improves BM-14's `3^251` separate-path classes and the raw `2^502` full mask states. The **attaining mask has only n+2=252 nonzero histogram orbit classes** and a linear-size sampler; its exact fully state-aware q4 cap is **1/8**, certified by a one-character dual. This is a symbolic proof, not a measured 189,757-variable LP solve. Exact small-instance tests compare the histogram Krawtchouk kernel with complete mask enumeration, all clean coefficients with independent vertex-label census, BM-09 q4/q8 mask witnesses, BM-13 q4 theta dual, and the new family against BM-17's full rational primal/dual checker.

**ASMP-14 frontier:** the exact tractable family now includes a *growing core with repeated joint gain types*, beyond the fixed-core BM-23 theorem. The harder general case is a variable core with heterogeneous path gains/lengths and few automorphisms. Prior art on wreath-product symmetries and generalized Krawtchouk LPs applies; these are mathematical specializations under a frozen readout attacker model, with no operational model safety or new UGC claim.


## BM-25: sharp q=8 replication penalty and a constant-support dual on a growing theta core

The [BM-25 q8 repeated-path theorem](REPLICATED_GAIN_Q8_BM25.md) resolves the first q>=8 fully hypothesis-aware instance left open by BM-24. Fix the growing theta family with **n ordinary length-two u-v paths of gain zero under both hypotheses** and one exceptional length-two path changing from gain zero to a fixed nonzero gain in K=F2³. Under fresh uniform labels and arbitrary correlated, hypothesis-aware XOR readout masks independent of the current clean pattern, the exact erasure threshold increases **strictly** when a second ordinary path is added:

    eta_sym(n=1;q=8,L=2)=1/44         [BM-08]
    eta_sym(n=2;q=8,L=2)=5/118        [BM-25].

The factor increase is exactly **110/59**. The n=2 instance is the same six-edge theta topology as BM-09, but its gains (0,0,1) leave one four-cycle balanced while BM-09's distinct (0,1,2) make all three frustrated. BM-09's q8 exact cap is 29/630, compared with BM-25's 5/118, establishing a controlled balance-pattern distinction under identical graph topology.

An exact hypothesis-aware attaining primal has **18 BM-24 path-histogram classes**, with flat/nonflat mask probability numerators over **13,216**, and each of its six bit marginals equals 5/118. A matching dual needs only **three Fourier orbit signatures**, or **seven full-cube Walsh multipliers**. Independent verification checks all 18 quotient Fourier equations, the rational LP matrix, every one of 64 complete output probabilities after expanding the orbit masks, and all **128 full-mask dual inequalities**. The clean discrepancy support has exactly seven Fourier subsets `{51,55,59,60,61,62,63}`, while the dual uses `{31,47,55,59,61,62,63}`. Thus some dual constraints have **equal clean coefficients under the two hypotheses** yet remain essential to control compatibility of their *different adversarial mask laws*. A discrepancy-support-only search is insufficient for proving the optimal fully hypothesis-aware mask budget.

For **any n>=2**, projecting onto two ordinary paths and the exceptional path proves the rigorous monotone lower bound `eta_sym(n)>=5/118`. BM-24's common mask gives the universal upper bound `eta_sym(n)<=1/8`. A direct **seven-character rational dual lift** has the same coefficients on the retained six edges and zero elsewhere, and BM-24's gain-grouped Fourier oracle confirms all seven clean coefficients are unchanged by adding ordinary paths. Every one of the `2^(2n+2)` dual mask inequalities reduces to the original **128** six-bit checks. This is verified symbolically for n up to **250 ordinary paths (502 reported edge bits, clean support `4^250−3^250`)**. The n>=3 sharp optimum is explicitly left open. The fully q>=8 infinite-family theorem remains open, with BM-25 supplying a new exact calibration point, a strict replication effect and a size-independent lower certificate.

The BM-25 result is a classical finite Fourier/LP duality and channel-symmetrizability application under the registered readout threat model. It carries no new UGC, operational AI alignment or independently authenticated intervention guarantee.


## BM-26: exact q=8 third-replica optimum and monotone convergence bracket

The [BM-26 exact three-replica theorem and numerical pilot](THREE_REPLICA_Q8_BM26.md) extend BM-25's hypothesis-aware erasure sequence for q=8, two-edge ordinary and exceptional paths. The sharp optimum under the registered **current-clean-independent correlated XOR readout adversary** is

    eta_1=1/44, eta_2=5/118,
    eta_3=751225/13956626 ≈ 0.053825688242989.

The strict n2-to-n3 increase is exactly `4715355/411720467`. At n=3 there are four paths, eight reported edges, 30 repeated-path histogram mask orbits per world, and a reduced rational LP with 61 primal variables, 31 equality rows and 4 per-type error cap constraints. A complete exact attaining mask pair uses **16 positive orbit masses in each world**, integer numerators over **27,913,252**, with every bit marginal exactly eta_3. Its rational lower dual has **29 nonzero Fourier histogram multipliers** and 4 signed marginal multipliers. The independent generic BM-17 oracle expands these into **255 full-cube Fourier dual coefficients**, verifies all **512 individual mask-atom inequalities**, enumerates both 8^6 fresh-label clean distributions and checks **every one of the 256 complete reported-pattern equalities**. The proof uses only Fraction/integer arithmetic and contains no runtime numerical solver.

Adding an ordinary path cannot reduce the minimum hostile masking budget: projection from n+1 to n retains the uniform labeling marginal and mask admissibility. BM-24's common-channel construction supplies the n-independent upper `1/(4L)`. Thus for every q,L the monotone sequence eta_n(q,L) has a **well-defined limit**. For q=8,L=2, the new provable bound is `751225/13956626 <= eta_n <= 1/8` for all n>=3 and therefore the same limit bracket. The 29-orbit/255-full-character lower dual lifts to arbitrary n>=3 by retaining three ordinary paths and the final exceptional path; all global dual inequalities reduce to the 512 local checks. The lift is exactly tested on n=3,4,5,10,250, with a 502-edge large fixture. For q=2/4 the limit is already exactly the common 1/(4L).

A separate SciPy/HiGHS quotient-LP scan returned **uncertified exploratory** rates rising from about 0.063875 at n=4 to 0.094878 at n=16. The scan gives no sharp rational primal/dual beyond n=3 and **does not establish the asymptotic value or convergence rate**; these remain open. The structural challenge is now to derive a uniform-in-n analytic lower or upper certificate for q>=8 and to determine whether the limit equals the common-channel 1/(4L). The BM-26 computation belongs to classical Fourier/LP symmetrization theory and establishes no live AI model oversight guarantee, new UGC theorem or independently attested intervention.


## BM-27: A uniform q=8 hypothesis-aware erasure upper below the common-mask limit

The [BM-27 five-component convolution construction](UNIFORM_Q8_REPLICATION_UPPER_BM27.md) provides an exact **uniform-in-n UPPER** on the full hypothesis-aware masking threshold left open by BM-26:

    eta_n(q=8,L=2) <= 5/52 ≈ 0.0961538462,   ALL n>=1.

This is strictly lower than BM-24's exact **common-channel** cost 1/8, an absolute improvement **3/104** and relative decrease **3/13**. The theorem uses a four-state pair distribution identity, not a numerical LP extrapolation. Conditional on the shared terminal difference, an ordinary two-edge path is distributed as `A=(7/8,0,0,1/8)` when its total gain matches, and `B=(3/4,1/8,1/8,0)` otherwise. Define identity mask `I=(1,0,0,0)` and the legal one-hot parity eraser `E=(1/2,1/4,1/4,0)`. The exact signed-measure equality `E=2B-I` and XOR convolution relation `A*E=B*E` hold.

For n ordinary paths, put `A_n=A^(tensor n)` and `B_n=B^(tensor n)`. The clean laws are `P0=(A_n⊗A+7B_n⊗B)/8` and `P1=(A_n⊗B+B_n⊗A+6B_n⊗B)/8`. The **legal world-specific masks** are

    Q0=[3 I_n⊗E + A_n⊗I + A_n⊗E
                       +6 B_n⊗I +2 B_n⊗A]/13,
    Q1=[3 I_n⊗E +2 A_n⊗A
                       +6 B_n⊗I +2 B_n⊗B]/13.

Each individual edge has mask marginal **exactly 5/52 in both worlds**. Expanding the convolutions by the five ordinary output categories `A_n, B_n, (A*A)^tensor n, (A*B)^tensor n, (B*B)^tensor n` gives **identical exact four-state exceptional coefficients in both worlds** by the two pair identities above. This proves complete masked output-law equality for **every n**, without enumerating Fourier subsets or relying on finite numerical pilots. A legal O(n) sampler implements the mixtures. The new pure-stdlib tests independently compare the uniform vertex-label census with the clean conditional mixture (n=1..3), check every complete output probability and per-edge marginal (n=1..4), cross-check the BM-24 exact histogram-orbit Fourier equalities, and exercise symbolic n=250 and n=1000 cases.

**Improved limiting-value bracket:** BM-26 proves the monotone limit `eta_infinity(8,2)` exists. Its registered exact n=3 lower plus BM-27's all-n upper give

    751225/13956626 <= eta_infinity(8,2) <= 5/52.

The earlier exploratory LP values through n=16, reaching about **0.094878**, lie below and approach **5/52**. This motivates **BM-27/C1: eta_infinity=5/52**, with only the upper direction established. A uniform-in-n **lower** certificate, perhaps via de Finetti ordinary-mask mixtures and compatible conditional exceptional-mask couplings, is still missing. The five-component witness is classical XOR convolution/channel symmetrization mathematics specialized to the frozen gain-graph interface and carries no empirical model safety or new UGC claim.


## BM-28: certified q8 n=16 lower narrows the replication limit near BM-27's 5/52

The [BM-28 exact integer rational dual certificate](RATIONAL_N16_LOWER_BM28.md) sharply strengthens the lower endpoint of BM-27's open q=8, two-edge repeated-path limiting-value conjecture. For **n=16 ordinary paths plus one exceptional path**, with 34 Boolean readouts and q=8, a **fully hypothesis-aware correlated-mask erasure** requires at least

    eta_16 >= 4743879/50000000 = 0.09487758.

The rational dual was discovered by a numerical HiGHS LP and rounded to a *conservatively feasible* certificate. The 459 Walsh-orbit dual coefficients are losslessly stored as signed int64 integers at scale 10^8 in [a checksum-pinned archive](BM28_N16_RATIONAL_DUAL.b64), with 441 nonzero terms. The [independent pure-stdlib verifier](n16_rational_lower_BM28.py) rebuilds the exact BM-24 ordinary-path multivariate Krawtchouk kernel from integer polynomial coefficients, reconstructs all q=8 clean Fourier weights as rational powers of two, and checks **every one of 2*459=918 rational dual mask-orbit inequalities** using an integer common denominator. The signed marginal multipliers `(-29001113,-37951043,-33047844,0)/100000000` sum to -1; the normalization objective `(9487759-1)/100000000` is the asserted lower bound. Every mask-orbit inequality is nonpositive exactly, proving the same bound against the entire **2^34 underlying full-mask space per hypothesis** by BM-24's orbit symmetrization theorem. Tests cross-check the integer kernel and clean signal formula against independent BM-24 oracles on small n. **This is a lower certificate only**, with no exact n=16 optimum or attaining n=16 primal claimed.

BM-26's monotonic projection theorem promotes the certified n=16 lower to every n>=16 and the limit. Paired with BM-27's exact all-n upper `5/52`, the current **rigorous** interval is

    4743879/50000000 <= eta_infinity(8,2) <= 5/52,

with exact width `829573/650000000 ≈ 0.001276266154` (about **0.1276 percentage points**). The earlier exploratory n=16 numerical optimum `≈0.0948776078` was used only to generate the dual candidate; it is not a certified sharp value. The new lower almost reaches the candidate limit 5/52, which **remains unproved** without a uniform-in-n analytic lower family or equivalent infinite-exchangeability argument. The math is a finite Fourier/LP certificate under the frozen current-clean-input-independent world-aware masking contract, without an operational AI alignment or new UGC implication.


## BM-29: exact de Finetti/dyadic-overlap theorem settles the q8 replication limit

The new [BM-29 asymptotic theorem and full proof](INFINITE_REPLICATION_LIMIT_BM29.md) **settle BM-27/C1 in the registered full-Boolean, fresh-uniform-label, hypothesis-aware but current-clean-independent correlated-readout model**:

    lim_(n->infty) eta_sym(n;q=8,L=2) = 5/52.

BM-27's legal all-n **upper** at 5/52 was already exact. The new lower argument applies to a subsequential limit of the optimal finite-n masks after BM-24's ordinary-path/within-path exchangeability averaging. The finite **marginal-rigidity lemma** first shows that complete output equality forces the adversarial worlds to have identical *entire joint ordinary-noise marginals* and identical marginals including **either individual exceptional noise bit**, because all their common clean Walsh coefficients are strictly positive:
`W_ord(b,r)=(3/4)^b[1+7*2^(−r)]/8>0`. A diagonal compactness limit, the classical de Finetti–Hewitt–Savage representation and the strong law yield a common directing measure `mu` over symmetric two-bit ordinary mask distributions. Write `u` for each ordinary noise bit's Fourier character and `w` for their joint parity character. Physical nonnegativity forces `w>=2u−1`. Each infinite ordinary output empirical pair law has Fourier coordinates `(3u/4,3u/4,w)` in the clean-matched mode and `(3u/4,3u/4,w/2)` in the unmatched mode.

Let `nu_0,nu_1` be the exceptional-noise **pair-parity signed measures** conditional on this common directing state and `v` the common signed single-exception-bit measure. Equality of the masked infinite outputs gives the exact pushforward identity under `S(u,w)=(u,w/2)`:

    (2I+7S_*)nu_0=(I+8S_*)nu_1.

The sharp **dyadic-overlap lemma** states `H=integral min(dnu0,dnu1) <=(16/5)integral(1-u)dmu`. Its proof splits on u: for `u<=11/16`, absolute measure domination is enough; for `u>3/4`, physical w>1/2 makes the dyadic supports disjoint and forces zero exceptional parity; in the remaining `11/16<u<=3/4` regime, `w>3/8` means only **two dyadic levels** can interact. The signed masses on an interacting high/low chain satisfy the rigid ratio **(nu0H,nu1H,nu0L,nu1L)=(1,2,8,7)c**; domination forces total directing mass at least `10|c|`, and the positive overlap is at most `8|c|`. This yields the global 16/5 bound.

Nonnegativity of the exceptional `11` noise atom and marginal rigidity give special-bit cost `C_s >=(1-H)/4`. Ordinary-bit noise cost is `C_o=integral(1-u)dmu/2`. Hence

    8 C_o + 5 C_s >= 5/4,

and because both costs are bounded by `eta_infty`, necessarily `eta_infty>=5/52`. BM-27's all-n channel **attains equality in every inequality**: its ordinary directing law has mass **3/13 on I**, **2/13 on A**, **8/13 on B**, with the two A/B dyadic parity states at `(u,w)=(3/4,1)` and `(3/4,1/2)`, signed overlap exactly **8/13**, and both per-bit costs **5/52**. Thus the bound is sharp, proving the exact limit.

The new [pure-stdlib exact algebra verifier](infinite_replication_rigidity_BM29.py) and [independent tests](test_infinite_replication_rigidity_BM29.py) check all finite Fourier positivity identities, exact finite-world noise-marginal rigidity for BM-25/BM-26/BM-27, physical mask coordinates, signed 1:2:8:7 chain recurrences including negative masses, and equality of BM-27's 8:5 weighted cost. The **infinite exchangeability/measure disintegration steps are proved in prose and are not machine-formalized in Lean**. The mathematical statement is exact within its declared threat model, while independent expert review and novelty examination remain appropriate before publication.

**Remaining ASMP-14 frontier:** finite-n q8 sharp optima for n>=4, a quantitative approach-to-limit bound, extension to q>=16 and longer paths, and integration with independently attested and costed interventions. BM-29 is a model-specific exchangeability/Fourier/signed-measure theorem, with no claim of live AI-control performance, a new UGC proof, or generalized agent-alignment safety.


## BM-30: rigidity of the q8 optimal limiting readout channel and quantitative infinite stability

The [BM-30 equality-case theorem and independent verifier](OPTIMAL_CHANNEL_RIGIDITY_BM30.md) sharpen BM-29's exact `eta_infinity(8,2)=5/52` result from a scalar threshold to a **unique symmetrized optimal infinite-channel law**. The theorem characterizes **ALL** infinite exchangeable channels attaining equality in the BM-29 weighted Fourier lower inequality `8 C_ordinary+5 C_exceptional>=5/4`: their de Finetti directing measure is concentrated on the three ordinary two-bit mask laws `I=(1,0,0,0)`, `A=(7/8,0,0,1/8)`, `B=(3/4,1/8,1/8,0)`. They form a one-parameter equality family, with `0<=c<=1/10` and

    mu(I,A,B)=(1-10c,2c,8c),
    nu0(I,A,B)=(0,c,8c), nu1(I,A,B)=(0,2c,7c).

Saturation of the exceptional-mask nonnegativity inequality additionally determines the shared special one-bit signed measure `v=((1-10c)/2,3c/2,15c/2)`, hence the **unique conditional special mask distributions** on every positive-mass atom: I mode uses `E` in both worlds; A mode uses `(I+E)/2` flat and `A` frustrated; B mode uses `(3I+A)/4` flat and `(3I+B)/4` frustrated. Every `c` in the interval is realized by an exact **all-n finite legal readout eraser** obtained as a convex combination of the trivial `I_n tensor E` channel and BM-27's active non-I branches. Its ordinary and exceptional bit costs satisfy

    C_o=5c/4, C_s=1/4-2c,
    8 C_o+5 C_s=5/4.

The minimax cap `max(C_o,C_s)` has the **unique** minimum at `c=1/13`, recovering BM-27's directing masses `(3,2,8)/13` and cap `5/52`. The equality proof strengthens BM-29's dyadic analysis: on ordinary one-bit Fourier parameter `u>5/8`, physical `w>=2u-1>1/4` allows at most **two** feasible dyadic levels, so the signed exceptional parity overlap is at most **4/5 of the directing measure**; for `u>3/4` the signed measures vanish. The sharp global overlap defect vanishes only for directing mass at `u=3/4` and `u=1`, and equality localizes their `w` and parity flows to the three modes.

**Finite-n qualitative convergence:** any sequence of complete-output equalizing finite-n mask pairs whose budgets tend to `5/52`, after averaging ordinary path and within-pair permutations, has distributions on **every fixed k ordinary paths plus the exceptional pair** converging in total variation to the BM-27 mask projection. Compactness/de Finetti gives subsequential infinite limits; uniqueness forces all limits to coincide. This proves structural convergence **without an explicit n-rate**.

**Quantitative infinite near-optimal stability:** for any infinite exchangeable equalizer with error cap <=`5/52+delta`, define `J=integral(1-u)dmu`, signed-overlap `H=integral min(dnu0,dnu1)`, `G=16J/5-H>=0`, and nonnegative exceptional-atom slack measure `T=(mu+nu0 wedge nu1)/2-v`. The exact weighted dual defect decomposes as `8C_o+5C_s-5/4=(5/4)G+(5/2)T(total)`. Consequently `G<=52delta/5` and `T(total)<=26delta/5`. A piecewise dyadic fiber inequality gives the explicit localization bound

    mu{dist(u,{3/4,1})>=eps} <= min(1,52delta/min(1,16eps)).

This controls **infinite** directing-measure mass away from the optimum's two ordinary single-bit Fourier values; it does not assert total-variation distance to the entire optimal channel at finite `delta`. The [BM-30 exact Python verifier](optimal_channel_rigidity_BM30.py) and [9 independent tests](test_optimal_channel_rigidity_BM30.py) check the whole rational equality frontier, signed parity flow, exceptional conditional mask laws, complete finite-n output equality for multiple parameters, uniqueness of the minimax intersection and stability algebra. The de Finetti measure-theory proof is in prose, **not formalized in Lean**; independent expert review remains appropriate.

**Remaining ASMP mathematical frontier:** derive an explicit quantitative convergence rate for finite `eta_n(8,2)` and fixed-coordinate optimal masks using finite-exchangeability approximation and robust dyadic overlap; generalize the unique-limit-channel method to q>=16 and variable graph-core structures. BM-30 concerns the frozen hostile readout channel and does not establish deployed model safety, authenticated interventions or a new UGC proof.


## BM-31: quantitative finite de Finetti approximation preserving exceptional noise rigidity

The new [BM-31 finite-exchangeability theorem and exact tests](FINITE_EXCHANGEABILITY_RATE_BM31.md) provide the missing **quantitative finite sampling ingredient** for deriving a future rate of convergence to the BM-29/30 q8 erasure limit. Under the registered hypothesis-aware correlated XOR readout model with **n ordinary two-edge paths and one exceptional pair**, average any exactly equalizing world-specific mask pair under ordinary-path permutations and within-path bit swaps. Its exact finite empirical state is a histogram `c=(c0,c1,c2)` of ordinary pair mask flip counts (0,1,2) plus the full exceptional mask pair `Z_h`. BM-29's strict positivity of the shared clean ordinary and ordinary-plus-one-exception Fourier coefficients forces the two worlds to have **identical empirical histogram laws** and identical joint laws of that histogram with **either individual exceptional noise bit**.

Given any such n-path law, construct a **genuine infinite exchangeable mask extension** by drawing the empirical histogram and exceptional pair from their original joint law and, conditional on them, drawing ordinary pair masks i.i.d. from the physical empirical pair distribution `lambda_c=(c0/n,c1/(2n),c1/(2n),c2/n)`. This preserves every per-edge flip rate, each world-specific exceptional-pair marginal, the common directing law across hypotheses and the special-single-bit rigidity constraints. The first k ordinary masks of the true finite law sample the histogram *without replacement*, while the infinite extension uses *with replacement*. A direct index coupling gives the exact total-variation bound
`dTV(Q_h^[k],Qtilde_h^[k]) <= 1-(n)_k/n^k <= k(k−1)/(2n)`.
An elementary **three-category KL/chi-square/Pinsker proof** improves this to

    dTV(Q_h^[k],Qtilde_h^[k])^2
        <= k(k−1)/[2(n−1)(n−k+1)], n>=2.

This is `O(k/n)` in TV for `k=o(n)`. Thus even a growing window `k=floor(n^(2/3))` admits an exact `O(n^(−1/3))` approximation. For n=1,000,000,000 and k=1,000,000, the rigorous mask-TV bound is below **0.000708** (0.071%), calculated symbolically without materializing masks. The exceptional pair and conditional one-flip orientations are included as shared stochastic kernels, preserving the entropy bound. Complete-output equality of the original worlds passes by contraction to an **approximately equalizing infinite extension** on k paths, with output TV at most twice the mask-TV bound and every Walsh discrepancy at most four times that bound.

The [pure-standard-library exact verifier](finite_empirical_extension_BM31.py) and [independent tests](test_finite_empirical_extension_BM31.py) compare the true hypergeometric projection with a separate full-mask bit projection, construct the with-replacement de Finetti extension, verify exact marginal rigidity on actual BM-25, BM-26, BM-27, BM-30 world-specific mask pairs, check complete Boolean output-TV and Fourier bounds, and exercise a sharp n=2 fixed-histogram collision counterexample. The rational entropy bound is independently verified against all registered finite mask witnesses and includes symbolic million-path sample-size controls. The proof is an application of classical finite de Finetti/Diaconis-Freedman and hypergeometric KL covariance analysis with an additional distinguished exceptional mask.

**Crucial remaining open step:** BM-31 gives an explicit **finite-window distribution approximation**; it does not by itself give a scalar convergence rate for `5/52−eta_n`. To obtain that, prove a **robust finite-observation version** of BM-29's signed dyadic-overlap inequality: when two infinite exchangeable output mixtures differ by at most epsilon on k observed ordinary paths, establish an explicit error term `R(k,epsilon)` in `8C_o+5C_s>=5/4−R(k,epsilon)`. Combining that result with BM-31's `O(k/n)` window error would yield a quantitative finite-n threshold rate. BM-29's exact limit and BM-30's unique asymptotic mask remain intact; no AI-control deployment or UGC result is claimed.


## BM-32: robust finite-observation dyadic equation and O(1/n) fixed Fourier moment rate

The new [BM-32 quantitative observable theorem](ROBUST_DYADIC_OBSERVABILITY_BM32.md) advances BM-31's finite exchangeability program toward an explicit finite-n rate for BM-29's q8 erasure threshold. Take any **exact full-output equalizing** hypothesis-aware readout mask pair on n ordinary q8 length-two paths plus one exceptional pair. Symmetrize it as in BM-24 and pass to BM-31's **infinite empirical replacement extension**, retaining the common ordinary directing histogram law and world-dependent exceptional pair coupling. Let `mu` be its common ordinary directing measure, `nu0,nu1` its world-dependent signed exceptional **pair-parity measures**, and let the BM-29 dyadic pushforward defect be

    D=(2I+7S_*)nu0-(I+8S_*)nu1,
    S(u,w)=(u,w/2).

The exact infinite BM-29 proof has D=0. For BM-31's finite-n approximant D may be nonzero. **BM-32/T1** gives an explicit finite-observation bound: for any `f(u,w)` with `sup|f|<=B` and `l1-Lipschitz<=L`, if the two approximating infinite channel output laws on k ordinary pairs plus the exceptional pair have total variation epsilon, then

    |int f dD| <=32*B*epsilon +224*L/(3 sqrt(k)).

Proof: estimate the latent ordinary mask's one-bit Fourier parameter `u` by `clip[(2/(3k))sum(X_i+Z_i)]` and pair parity `w` or `w/2` by `(1/k)sum X_i Z_i` on the observed ordinary path bits encoded as ±1. The conditional expected l1 estimation error is <=7/(3 sqrt(k)). Multiplying `f` of the empirical estimates by the observed **exceptional pair parity** produces an observable bounded by B. The two worlds' observable expectations differ by at most 2B epsilon, while their corresponding latent expectations differ by `D[f]/16`. The two estimation errors give the remaining term.

Using BM-31's uniform `epsilon<=2*sqrt(v)` for `v=k(k−1)/[2(n−1)(n−k+1)]`, the resulting **exact rational squared** bound is

    |D[f]|² <=2*[4096 B² v + (224L/3)²/k].

Choosing `k=floor(n^(2/3))` yields an explicit **O(n^(−1/3)) bounded-Lipschitz dyadic-defect rate**, even though the original readout masks may correlate all 2n+2 bits.

**BM-32/T2 is stronger for fixed-degree polynomial tests:** for a,b>=0 and d=a+b<=n, build the observable `G_(a,b)` from a distinct ordinary reported **first-bit parity** characters, b distinct ordinary **pair parities**, the exceptional pair parity, and a normalization factor `(4/3)^a`. Its expectation equals the corresponding latent signed monomial `u^a w^b` *exactly*, without empirical estimator variance, and

    D[u^a w^b] =16*(E0 G_(a,b)-E1 G_(a,b)),
    |D[u^a w^b]| <=32*(4/3)^a*d(d−1)/n.

The rate is **O(1/n) for every fixed polynomial degree** and improves the BL bound on that explicit test subspace. The equalities and upper bounds are independently verified by [BM-32 exact Python tests](test_robust_dyadic_observables_BM32.py) against BM-25 n2, BM-26 n3, BM-27 legal all-n masks and BM-30 equality frontier channels, including sample-character unbiasedness and real complete reported-output TV. Large n examples are checked only by symbolic rational bound calculations.

**Precise unresolved bridge:** the scalar `5/52−eta_n(8,2)` still lacks an explicit n-rate. The BM-29 weighted lower theorem controls the **minimum of two signed measures**, a nonlinear operation that is generally unstable under mere low-degree moment approximation. To use BM-32 for the scalar threshold, construct a **polynomial or Lipschitz dual approximation** to BM-29's signed dyadic-overlap certificate, with independently verified uniform approximation error and coefficient norm or Lipschitz complexity, then combine it with the exact BM-32 rates. No scalar convergence-rate or new UGC/operational AI control claim is made.
