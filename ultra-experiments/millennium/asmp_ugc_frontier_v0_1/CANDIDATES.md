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
