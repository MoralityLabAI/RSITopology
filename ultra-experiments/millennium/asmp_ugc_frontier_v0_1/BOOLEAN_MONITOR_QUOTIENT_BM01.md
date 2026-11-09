# ASMP-14/15: the Boolean-monitor quotient and an unobservable cover-degree gap

**2026-11-09 | mathematical addendum BM-01.**

**Claim level:** elementary finite theorems with independent exact rational controls. This refines the provisional [ASMP-13..16 candidates](CANDIDATES.md). It is a target-specific information impossibility for a frozen monitoring interface. It makes no claim to new biased-graph foundations or behavioral AI-safety validation.

## 1. Frozen observation interface

Fix a finite oriented edge-occurrence graph G=(V,E), alphabet K=F₂^s with q=2^s, and hidden connection c in K^E. During an independent episode choose a fresh uniform vertex labeling a in K^V. The monitor receives only the binary satisfaction indicators

    X_e = 1[a(v_e)-a(u_e)=c_e], e in E.

The monitor knows G and q and may observe the entire Boolean vector X or adaptively choose subsets of its coordinates across independent episodes. It does not observe a, c, nonzero group residuals, or persistent labels reused between episodes. Equality of the *complete one-episode law* implies equality of every adaptive transcript law in this interface, regardless of how many independent samples are made.

## 2. Exact observable-quotient theorem BM-01/T1

For each F subset E let k(F) be the number of connected components of (V,F), including isolated vertices, and define Balanced_c(F) to mean that every cycle in F has zero additive holonomy. Integrating edge shifts along a spanning forest gives the exact moment formula

    M_c(F) := E[prod_(e in F) X_e]
            = Pr[all e in F are satisfied]
            = 1[Balanced_c(F)] * q^(k(F)-|V|).                 (1)

The positive factor depends only on the known graph. All mixed moments determine the complete joint law of the Boolean vector by inclusion-exclusion (Möbius inversion), and the law determines those moments.

**Theorem.** For two connections c,d on the same graph and alphabet:

    Law(X | c) = Law(X | d)
       iff Balanced_c(F) = Balanced_d(F) for every F subset E. (2)

The information quotient of the entire Boolean-monitor experiment is precisely the family of balanced edge subsets, equivalently the **biased graph** specified by its balanced simple cycles. This is classical gain-graph structure (Zaslavsky 1989). It can be strictly coarser than vertex-gauge orbits and even coarser than global GL(s,2) orbits.

### Target-specific sufficiency

The optimum and balanced random-cluster partition polynomial depend only on this quotient:

    phi_G(c) = 1 - max_{F:Balanced_c(F)} |F|/|E|,            (3)

    Z_c(z) = sum_{F:Balanced_c(F)} z^|F| q^(k(F)-|V|).      (4)

For (3), the satisfied edges of every labeling form a balanced subset, while a potential exists to satisfy every edge in any balanced subset. Formula (4) is the existing [EvalMath UGCS-02 finite expansion](https://github.com/MoralityLabAI/EvalMath/blob/research/ugc-game-space-20261109/paper/game_space_partition_bridge_2026_11.md). Thus perfect knowledge of the Boolean observation **law** identifies phi and every partition coefficient in principle, although computing those targets can be hard. It can fail to identify numeric holonomy and the minimal connected flat-cover degree.

For q=2, a Boolean edge indicator reveals the residual itself, because the only nonzero element is 1. One complete edge-pattern sample therefore reveals the affine cut-space coset of c, and distinct gauge classes have disjoint supports. For q>2, coarsening all nonzero residuals to a single bit loses that property.

## 3. Connected cactus family: exponential unobservable cover gap BM-01/T2

Choose t>=1, s>=t. Connect t vertex-disjoint triangles by t-1 bridges into a connected cactus graph with

    n=3t, m=4t-1, beta1=t, K=F₂^s.

Put zero shift on each triangle's first two edges and on every bridge. Assign a nonzero holonomy h_j to the closing edge of triangle j.

- **Aligned A:** h_1=...=h_t=e_1. Its holonomy image has order 2.
- **Independent B:** h_j=e_j for j=1..t. Its holonomy image has order 2^t.

Each triangle is frustrated in both cases, and the *only* simple cycles are those triangles. A subset F is balanced in either instance precisely when it omits at least one edge from every triangle. By theorem (2), the complete Boolean pattern laws are equal:

    TV(Law(X|A),Law(X|B))=0.                              (5)

Any adaptive monitor obtaining arbitrary subsets of fresh Boolean patterns has identical transcript laws in the two worlds. The exact minimum degree of a connected cover flattening the pulled-back connection is the holonomy-image cardinality:

    deg_min(A)=2, deg_min(B)=2^t.                          (6)

Hence a Boolean monitor cannot distinguish a factor 2^(t-1) difference in minimum flat-cover degree, even with unbounded samples and computation. The two instances cannot be related by a global invertible K-coordinate change, since their holonomy-image dimensions differ.

Their optimization and partition statistics nevertheless coincide:

    phi_G(A)=phi_G(B)=t/(4t-1),                            (7)

    Z_A(z)=Z_B(z)
         = [(1+z/q)^3-(z/q)^3]^t * (1+z/q)^(t-1).         (8)

Every frustrated triangle requires one failed constraint; each bridge can always be satisfied. The partition factorization follows from the exact frustrated-cycle formula and independent tree-bridge residuals.

**Smallest nontrivial witness:** t=2, s=2 gives 6 vertices, 7 edges, triangle holonomies (1,1) versus (1,2), cover degrees 2 and 4, and exact game optimum 5/7 in both. Exhaustive independent enumeration over all 4^6=4096 vertex labelings confirms identical complete Boolean laws.

### Implication for ASMP-15

Freeze a safety/attestability predicate requiring existence of an exactly flat connected cover of degree at most r. With 2<=r<2^t, A and B have opposite policy labels and identical Boolean observation laws. Under equal priors, the best monitor in the stated interface succeeds with probability 1/2 for any adaptive budget. A complete group-valued cycle-return interface can recover the missing holonomy-image dimension; its physical access, noise, and cost must be independently specified.

This gives a concrete separation between *frustration certification* and *cover-cost certification* under the same monitoring channel.

## 4. Finite independent checks

- [Pure-Python oracle](biased_graph_observability.py): enumerates balanced subsets, computes exact mixed moments, and recovers the joint Boolean law by Möbius inversion, without vertex-label enumeration.
- [Independent tests](test_biased_graph_observability.py): all 256 F₂² four-cycle connections compared to exhaustive direct label sampling; the t=2 cactus pair compared against 4^6 labelings; image/cardinality and exact cosystolic optimum checks; t=1..4 exponential cover-degree controls; a binary one-sample gauge-identification control; loop/parallel/empty-graph cases.
- The earlier [ASMP-14 cycle TV bound](SHARP_VISIBILITY_AND_DECODING_BOUNDS.md) has **positive** but exponentially small TV when comparing flat with frustrated cycles for q>2. The new cactus pair gives **zero** TV between two different nonflat gauge classes with a substantial cover-cost gap.

## 5. New preregistration target

**ASMP-14/15 monitoring-lift frontier.** For a bounded-degree graph family and a frozen policy target (cosystolic threshold or flat-cover degree), classify the uniform hypothesis-testing error region and minimal audit cost for (i) Boolean edge satisfactions, (ii) noisy K-valued residual sketches, (iii) authenticated cycle-return queries, and (iv) linked observations sharing a persistent labeling.

The cactus pair is the mandatory negative control for holonomy-image rank under Boolean access. Binary coset observations are a positive control. A new mathematics contribution would be a *costed noisy/adaptive monitoring transition* beyond the classical gain-graph quotient identity.

### Prior art

- Thomas Zaslavsky, [Biased graphs. I. Bias, balance, and gains](https://doi.org/10.1016/0095-8956(89)90063-4), Journal of Combinatorial Theory B 47 (1989), 32–52.
- Thomas Zaslavsky, [gain-graph lecture notes on balanced chromatic polynomials](https://people.math.binghamton.edu/zaslav/Tpapers/gaingraphs-lecture-notes.pdf).
- [RSITopology historical ASMP-9 exact reward-gauge census](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/asmp9_reward_gauge_census/README.md).
