# BM-09: interacting cycles change the exact adversarial erasure threshold

**10 November 2026 | finite theorem plus two independent exact certificates.**

This is the first graph-level step after [BM-08's sharp single-cycle theorem](SHARP_ERASURE_OPTIMALITY_BM08.md). The graph is the simple theta graph K_{2,3}, with three internally disjoint length-two paths between two endpoints. Each pair of paths forms a four-cycle, giving three interlocking cycles and cycle rank beta1=2. Its gain-graph theta property has established prior art in [Zaslavsky, *Biased Graphs I* (1989)](https://doi.org/10.1016/0095-8956(89)90063-4).

**Scope:** binary-vector translation labels K=F2^s, fresh independent uniform vertex labelings, full Boolean satisfaction-vector observations, and a hypothesis-aware XOR readout mask chosen independently of the current clean observation. The mask can be arbitrarily correlated within the six reported bits and can differ between flat and frustrated worlds, subject to one uniform per-edge flip-probability cap eta. No physical agent intervention or root-state attestations are inferred.

## 1. Frozen theta graph and minimax definition

Let the vertices be two endpoints u=0,v=1 and three intermediate vertices A=2,B=3,C=4. Use six directed edge occurrences

    e0=(0,2), e1=(1,2), e2=(0,3), e3=(1,3),
    e4=(0,4), e5=(1,4).

The XOR gain along each u-v path is the sum of its two edge shifts. Compare the flat connection with all shifts zero to the **contrabalanced theta** connection

    (c0,...,c5)=(0,0,0,1,0,2).

Its three path gains are (0,1,2). For K=F2^s with s>=2 they are pairwise distinct, so each of the three four-cycles is frustrated. The graph has n=5,m=6,beta1=2.

For the two worlds, let P0 and P1 be the exact one-episode probability distributions of the full 6-bit satisfied-edge vector. For h=0,1 the adversary selects a normalized probability law Qh on 6-bit XOR masks. Each bit has marginal flip probability <=eta. Define the erasure threshold

    eta_sym(G,c;q) =
      inf{eta: exists Q0,Q1 satisfying P0*Q0=P1*Q1
                    and max_(h,i) Pr_Qh[M_i=1]<=eta}.

Projection to any unbalanced four-cycle implies the elementary general lower bound

    eta_sym(G,c;q) >= eta_star(q,4),                   (1)

where eta_star is BM-08's single-cycle threshold. The question is whether the simultaneous, shared-edge constraints force a larger cost.

## 2. BM-09/T1: a short exact theorem for q=4

**Theorem.** For q=4, the contrabalanced theta's full-pattern erasure threshold is

    eta_sym(theta, (0,1,2);4) = 1/6.                  (2)

### Lower proof

Write X_e for an edge-satisfaction indicator, and chi_S(X)=(-1)^(sum_(e in S) X_e). Fix the endpoint label difference d. Along a complete two-edge u-v path with gain g, integrating over its independent middle vertex gives

    E[chi_{path}(X) | d]
      = 1 - 4/q + (4/q)*1[d=g].

At q=4 this simplifies exactly to 1[d=g].

For the flat connection, the three path gains are equal. For the contrabalanced connection, they are pairwise distinct. Consequently:
- For the full six-edge set S=E, the flat expectation E chi_E=1/4, while the contrabalanced expectation is zero.
- For every five-edge set S=E\{i}, the two complete paths and one remaining edge give flat expectation E chi_S=1/8, while the contrabalanced expectation is zero. The incomplete path contributes a factor 1-2/q=1/2.

If the masked worlds are equal, Fourier convolution forces the **flat-world mask law Q0** to satisfy hat Q0(E)=0 and hat Q0(E\{i})=0 for each of the six edges. These constraints hold regardless of the adversary's chosen Q1.

Let K=number of flipped bits under Q0 and let B=1[K odd]. The full-set Fourier equation gives Pr(B=1)=1/2. The six complement-Fourier equations say that the expected number T of complements with odd parity is 3. Pointwise,

    T=K if K even;  T=6-K if K odd.
    T <= K+4 B                                  (for every K=0..6).

Hence

    3=E[T] <= E[K]+4*(1/2)=E[K]+2,
    E[K] >= 1.

Since E[K]=sum_(i=0)^5 Pr[M_i=1], some bit has flip probability >=1/6. This proves the universal lower bound under arbitrary correlated, hypothesis-aware masks.

### Explicit attaining distribution

Use the **same** mask distribution under both hypotheses:

    Q(000000)=1/4,
    Q(mask)=1/12 for each singleton mask
      {1,2,4,8,16,32}
    and each paired mask {10,17,36}.

The paired masks join edges of different u-v paths. There are six singles and three pairs, so the probabilities sum to one. Every edge participates in one singleton and one paired mask: its marginal error is exactly 1/6.

For every set of edge indices on which P0 and P1 have different Walsh coefficients (the three four-cycle supports, the six five-edge supports and the full six-edge support), hat Q(S)=0. The other clean coefficients coincide. Hence P0*Q=P1*Q by Fourier inversion. The [code's independent exact convolution check](theta_shared_cycle_erasure.py) verifies all 64 output probabilities directly, without relying on Fourier reasoning.

This proves (2). The ratio to an isolated frustrated four-cycle is

    (1/6)/(1/8)=4/3.

### A balance-pattern control on the same graph

Changing the path gains to (0,1,0) leaves one balanced four-cycle and two frustrated ones. The isolated-cycle lower bound is now **attainable** by a different common-mask distribution:

    Q(0)=6/16; Q(4)=Q(8)=2/16;
    Q(mask)=1/16 for mask in {1,2,16,17,32,34}.

Every bit has marginal error 2/16=1/8. Exact convolution confirms output-law equality. Thus the same underlying K_{2,3} graph at q=4 has erasure thresholds **1/8 with one balanced cycle** and **1/6 with no balanced cycle**, under the two registered flat-versus-nonflat pairs. The biased-cycle structure, including the theta relation, matters.

## 3. BM-09/T2: exact q=8 finite linear-program certificate

**Theorem (finite rational primal/dual certificate).** For the same contrabalanced theta graph with q=8,

    eta_sym(theta,(0,1,2);8)=29/630 = 0.0460317460...       (3)

The isolated frustrated four-cycle threshold is 1/44, so

    eta_sym(theta;8)/eta_star(8,4) = 638/315 > 2.        (4)

This result has a complete **integer-arithmetic checkable certificate** rather than a short handwritten inequality such as the q=4 argument.

### Primal program and attaining witness

Index the 64 possible six-bit readout masks by integers m=0..63. The decision variables are two nonnegative probability vectors Q0,Q1 in R^64 and a scalar eta>=0. Minimize eta subject to

    sum_m Q0(m)=sum_m Q1(m)=1,
    sum_m P0(y XOR m)*Q0(m) = sum_m P1(y XOR m)*Q1(m)
         for every y=0..63,
    sum_{m:bit_i(m)=1} Qh(m) <= eta
         for h=0,1 and i=0..5.

An LP search gave an explicit exact witness. The committed module stores each Qh as 64 **integer numerators over 10080**, with Q0(0)=8736/10080 and Q1(0)=8895/10080. Its normalization and nonnegativity are checked independently. Every full Boolean output numerator agrees after convolution with the exact q^5=32768 vertex-label counts. The maximum per-bit mask numerator is 464, yielding 464/10080=29/630.

### Independent dual lower certificate

Assign equality multipliers y=(y_0,...,y_65), where the first 64 correspond to the output-equality equations and the last two to the normalizations. Assign 12 nonpositive multipliers z=(z_0,...,z_11) to the six per-edge marginal inequalities for each world.

The file stores exact rational numerators y over 37800 and z over 300. Direct integer checks confirm

    y_64+y_65 = 29/630,
    -sum_i z_i = 1,
    z_i<=0.

For every mask m, the dual feasibility inequalities are verified exactly:

    sum_y y_y P0(y XOR m) + y_64 + sum_{i:bit_i(m)} z_i <=0,
    -sum_y y_y P1(y XOR m) + y_65 + sum_{i:bit_i(m)} z_(6+i) <=0.

Here the sums over y use y=0..63, and P0,P1 are their exact rational clean distributions. Weak LP duality then proves eta>=29/630 for every possible pair of legal mask channels. The primal witness attains it, completing (3) without any numerical rounding dependency. No SciPy or optimizer is required by the submitted verification code.

The certificate is larger than the q=4 paper proof. The next symbolic goal is to compress its 64-output dual into a small number of gain-graph Fourier/cut inequalities.

## 4. Control: edge-disjoint cycles have no analogous overhead

Take two vertex-disjoint four-cycles connected by a bridge, with one frustrated cycle gain on each, q=4. This graph has beta1=2, the same cycle rank as the theta graph. The satisfaction residuals on the two cycle blocks and on the bridge factorize under uniform vertex labels because the cycle constraints are edge-disjoint.

Apply the single-cycle common one-hot mask law independently to each four-cycle and never flip the bridge bit. This legal readout erases both components with maximum edge error **1/8**, while projection onto either frustrated cycle proves no smaller cap works. The independent [cactus control](cactus_erasure_control.py) enumerates all 4^8=65536 labelings on its eight vertices and checks the full 512-outcome convolution equality.

More generally, for cactus graphs with edge-disjoint cycles attached by bridges, the same argument shows that the erasure cap of the flat-versus-specified connection pair is the maximum of the sharp BM-08 caps over the individually unbalanced cycle blocks, when the gain constraints are independent in this way. This is a factorization statement for the specified statistical channel. Connecting cycles through shared *edges* breaks that product decomposition.

Thus **cycle rank alone does not determine monitoring erasure cost**. Intersections among cycles can impose a stricter joint masking budget.

## 5. New research invariant and ASMP-14 admission gate

Define the normalized **symmetrization interaction index** for a graph/connection pair with at least one frustrated cycle:

    I_q(G,c) = eta_sym(G,c;q) /
               max_{C:Hol_c(C)!=0} eta_star(q,|C|).

An index greater than one measures extra readout adversary effort forced by simultaneous cycle constraints. It is one for disjoint-cycle cactus blocks in the factorized setting; it equals 4/3 for the q=4 contrabalanced theta and 638/315 for q=8. Its definition charges the same uniform marginal error cap per monitored edge and compares the complete joint Boolean output laws.

**Candidate conjecture BM-09/C1:** on suitably connected families of translation games, the symmetrization interaction index admits a lower bound through an invariant of the **cycle-edge incidence hypergraph**, perhaps a fractional covering/packing number with alphabet-dependent Fourier weights. A genuine theorem would require a precisely stated class and matching counterexamples. The two solved theta instances and cactus family are seed cases; no general lower-bound formula is asserted.

A possible applied relevance is that **redundant overlapping tests can increase the adversary's masking burden** even when tests share raw telemetry. Their true effectiveness depends on access to genuine independent state traces, adversary capabilities, correlated noise, and independently verified interventions. The ASMP-14 program should compare overlap-aware verifier construction to local-testable-code and adversarial-channel symmetrizability prior art.

## 6. Reproduction and provenance

- [theta_shared_cycle_erasure.py](theta_shared_cycle_erasure.py) provides full exact q=4 and q=8 proofs/witness checks.
- [test_theta_shared_cycle_erasure.py](test_theta_shared_cycle_erasure.py) tests both endpoints, perturbs the q=8 primal witness to ensure sensitivity, checks the q=4 pointwise lemma and the two theta balance regimes.
- [cactus_erasure_control.py](cactus_erasure_control.py) and [test_cactus_erasure_control.py](test_cactus_erasure_control.py) provide an independent edge-disjoint negative control.
- All code is pure Python 3 standard library, exact integer/Fraction arithmetic. The LP solver was used only to *discover* the rational q=8 witness and dual multipliers; runtime verification requires no solver, model calls, external data or GPU.
- The focused ASMP UGC frontier GitHub Actions workflow runs the entire seed test suite.

**Prior art:** Thomas Zaslavsky, [*Biased Graphs I* (1989)](https://doi.org/10.1016/0095-8956(89)90063-4), especially the theta property. [Biased Graphs II: Three Matroids](https://doi.org/10.1016/0095-8956(91)90005-5) relates balance to frame and lift matroids. The BM-09 finite LP is a special-case channel symmetrization problem, whose broader hypothesis-testing theory should be compared with Modak et al., [*Hypothesis Testing for Adversarial Channels* (2026)](https://doi.org/10.1109/TIT.2026.3691175). The formulas and exact certificates are established for the registered toy game; they make no claim of a newly proved model-alignment guarantee.
