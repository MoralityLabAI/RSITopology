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
