# ASMP-13/14 sharp finite bounds: exact cycle visibility and bounded-cycle-rank decoding

**2026-11-09 | v0.1 addendum.** This refines the [provisional ASMP candidate packet](CANDIDATES.md). The statements below are elementary finite mathematics, checked by a separate exact Python test suite. They do not establish a novel complexity class, physical AI monitoring result, UGC proof, or prize-level resolution.

## ASMP-14 / Theorem V: exact Boolean cycle observation law

Fix a single oriented cycle with length ell>=1 and K a finite abelian group of cardinality q>=2. Fix an edge-translation connection c and draw a uniformly random vertex labeling a. Define residuals r_e = a(v_e)-a(u_e)-c_e. Around the oriented cycle,

    sum_e r_e = -Hol(c).

For every residual vector satisfying that sum, exactly q vertex labelings realize it. Consequently the residual vector is uniform on a single affine codimension-one subgroup of K^ell. The monitor receives **only** Boolean bits X_e=1[r_e=0] for all ell edges.

For any particular Boolean pattern with k unsatisfied edges, the number of compatible residual vectors, with each of its k nonzero residuals constrained to have sum h, is

    N_k(h=0)  = ((q-1)^k + (q-1)*(-1)^k)/q,
    N_k(h!=0) = ((q-1)^k - (-1)^k)/q.

This follows by finite-character orthogonality: the sum of a nontrivial additive character over K\{0} is -1. In particular,

    N_k(0)-N_k(h!=0)=(-1)^k.

Every matching pattern therefore has signed probability difference (-1)^k / q^(ell-1). There are 2^ell Boolean patterns, so the **exact total variation** between flat and nonzero-holonomy cycle observations is

    TV(P_0,P_h)= 2^(ell-1)/q^(ell-1) = (2/q)^(ell-1).            (V1)

For q=2 the supports are disjoint and a full-cycle observation identifies parity perfectly. For q=4 and ell=4, TV=1/8; for q=8 and ell=4, TV=1/64. Their respective optimal one-shot Bayes successes at equal priors are 1, 9/16 and 65/128.

If the monitor gets N independent **freshly resampled full-cycle patterns**, tensorization of a coupling gives TV(P_0^N,P_h^N)<=N*(2/q)^(ell-1), hence Bayes success at least 2/3 requires

    N >= (1/3)*(q/2)^(ell-1).                                (V2)

This is a valid **necessary** sample bound, not a tight formula for minimax N in every regime. An independent K-valued cycle-sum query identifies h at once, emphasizing the role of the observation alphabet. If full edge residual values or shared vertex labels are visible, the observation grammar changes and the result must be re-derived.

### Binary symmetric monitor noise

For K=F₂, the clean joint satisfaction patterns are uniform over opposite parity cosets of F₂^ell. Apply a binary symmetric channel independently to each reported bit with flip probability eta. The new distributions differ only in their output parity bias, with exact TV

    TV(P_0*BSC_eta^ell, P_1*BSC_eta^ell)=|1-2*eta|^ell.        (V3)

At eta=0 this is one, and at eta=1/2 it is zero. The formula treats **independent per-edge readout errors**. Correlated and adaptive errors, a live-model monitor, or a different access channel require separate assumptions. For N independently resampled noisy observations, the same coupling gives a necessary N>=1/(3*|1-2*eta|^ell) for >=2/3 success when the denominator is positive.

### Relation to the earlier ASMP-14 local-oracle obstruction

If the monitor sees only r<ell bits on each fresh labeling, every queried edge subset is acyclic (or has zero holonomy), and the complete joint local observation law matches the flat game. Equation (V1) describes the first **nonlocal** query that can see the cycle, and shows it can still carry exponentially weak statistical information as q and ell grow. Equations (V2)-(V3) are the concrete sample-budget constraints missing from the original conceptual candidate.

**Novelty audit:** These are elementary coding/character-orthogonality identities, related to parity testing under BSC noise, gain-graph cycle constraints and locally testable code theory. They are a precise seed for the *priced access frontier*, not independent mathematical novelty on their own. Mandatory comparisons: Dinur et al., *Good Locally Testable Codes*, Annals of Mathematics (2026); First–Kaufman, *Cosystolic Expansion of Sheaves on Posets*, STOC (2024).

## ASMP-13 / Theorem D: FPT decoding by cycle rank

The proposed candidate initially listed **residual-holonomy image rank** as a possible tractability parameter. That is inadequate: over K=F₂ the holonomy image rank is always at most one, yet c_e=1 on every edge encodes MAX-CUT. To force image rank exactly one on any instance, append a disjoint triangle with unit shifts; its MAX-CUT contribution is exactly 2. Thus exact decoding is NP-hard even when the holonomy-image rank is exactly one. A connected version attaches that triangle by a bridge; MAX-CUT then increases by 3.

The **graph cycle rank** beta1=m-n+c is different and supports an exact parameterized algorithm. Choose a spanning forest T and identify the beta1 chord edge occurrences. Let S be the set of all chord endpoints; |S|<=2*beta1. For each of q^|S| assignments to the boundary labels, every chord's violation cost is determined. Minimize forest-edge violations with standard tree dynamic programming, which costs O((n+m)*q²) per boundary assignment. Return the minimum along with a witness labeling.

    time <= O(q^(2 beta1) (n+m) q²)                           (D1)

The bound is **fixed-parameter tractable in the pair (q,beta1)**. In a representation where q=2^s is supplied implicitly by s, it is exponential in s and makes no claim of polynomial time in bit-length alone. The algorithm also handles loops, parallel edges and disconnected components. When beta1=0, every forest translation game is satisfiable.

This is an elementary application of bounded-feedback-edge-number/treewidth dynamic programming, hence prior art in algorithm design. A new ASMP-13 must seek a joint verifier/query/interaction frontier **beyond** (D1), for instance under noisy cycle observations, untrusted proofs, bounded message size and explicit YES/NO gap promises. The image-rank negative control prevents a misleading structural conjecture.

## Proposed next ASMP statements

**ASMP-13 next frozen slice:** classify the information-communication-computation frontier for approximate frustration certification on bounded-degree, large-beta1 graphs under precisely priced K-valued holonomy queries and small untrusted proofs. Require an honest-prover efficiency bound and compare treewidth/feedback-edge-number/SoS/MaxCut baselines. The simple FPT case D1 is a positive control.

**ASMP-14 next frozen slice:** fix r, B, q, ell, eta, whether labelings persist across queries, and what each oracle returns. Establish or refute a simultaneous constant-gap frontier that interpolates among (i) fresh r-local Boolean projection queries with exact indistinguishability below the holonomy girth, (ii) fresh full-cycle Boolean queries with TV in (V1), (iii) noisy full-cycle binary queries with TV in (V3), and (iv) exact K-valued holonomy access. Report the complete composite testing error region before using any scalar success or sample metric.

## Reproducibility

- [Finite controls](finite_seed.py), [original tests](test_finite_seed.py).
- [Exact TV formulas and FPT decoder](frontier_bounds.py).
- [New independent tests](test_frontier_bounds.py) check the closed character sums against exhaustive uniform-label enumeration, TV exactness, BSC-noise convolution, the iid lower-bound calculation and the cycle-rank decoder against full exhaustive assignment optimization. All tests are CPU-only and use rational arithmetic except for integer-combinatorial bookkeeping.
- Workflow: [ASMP UGC frontier seed](../../../.github/workflows/asmp-ugc-seed.yml).

### Sources

- [UGCS-03 ASMP-9 gauge bridge](https://github.com/MoralityLabAI/EvalMath/blob/research/ugc-game-space-20261109/paper/asmp9_game_space_bridge_2026_11.md)
- [Provisional ASMP-9 expansion](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/V0_2_SCOPE_EXPANSION_DRAFT.md)
- [Good Locally Testable Codes, Annals 203 (2026)](https://annals.math.princeton.edu/2026/203-2/p03)
- [Cosystolic Expansion of Sheaves on Posets, First–Kaufman](https://arxiv.org/abs/2403.19388)
