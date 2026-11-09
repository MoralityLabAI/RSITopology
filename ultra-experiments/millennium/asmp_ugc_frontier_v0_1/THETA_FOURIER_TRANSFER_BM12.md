# BM-12: Exact theta-network Fourier transfer through a two-vertex separator

**10 November 2026 | finite algebraic identity, bounded exact checks.** This complements [BM-11 articulation tensorization](BLOCK_TENSOR_ERASURE_BM11.md): once a graph's 2-connected blocks have been isolated, their Fourier weights still need to be computed. A theta network is the smallest example of genuine interacting cycles. Its three internally vertex-disjoint paths meet at **two** terminals, and those shared terminal labels couple their consistency constraints.

## 1. Frozen gain and observation model

Consider k>=2 internally vertex-disjoint paths between endpoints u,v, each having L_i>=1 edges and total additive gain g_i in K=F2^s, q=|K|. Draw a fresh uniform labeling of all vertices and record the Boolean satisfaction vector X_e for every edge.

For any Walsh subset S of edges, define its coefficient

    W(S) = E[ (-1)^(sum_{e in S} X_e) ].

The coefficients of P_flat and P_frustrated enter the full adversarial readout LP as

    W0(S)*E_Q0[chi_S(M)]
       = W1(S)*E_Q1[chi_S(M)].

BM-10 established that retaining the **values** of nonzero coefficients matters. The result below computes them without enumerating the q^|V| possible vertex labelings.

## 2. Exact conditional transfer identity BM-12/T1

Let d=a(v)-a(u) be the endpoint label difference, which is uniform in K. Conditional on d, the internal vertex labels of distinct u-v paths are independent.

For path i, write S_i for its selected edges, with s_i=|S_i|. If S_i is a proper edge subset, the selected constraints form a forest with no connected u-v path. Their indicator events are independent with satisfaction probability 1/q, even conditioned on d, so

    E[chi_{S_i}(X)|d]=(1-2/q)^s_i,     S_i proper.   (1)

If the **entire** path i of L_i edges is selected, all proper edge-subset products still have probability q^(-r), but the probability of *all* path edges satisfied is q^(-(L_i-1))*1[d=g_i]. Expanding the product ∏(1-2X_e) gives

    E[chi_{S_i}(X)|d] = A_i + B_i 1[d=g_i],         (2)

where

    A_i=(1-2/q)^L_i - (-2/q)^L_i,
    B_i=(-2)^L_i / q^(L_i-1).

For the set I of fully selected paths and the remaining proper path subsets, conditional independence therefore gives

    W(S) = (1-2/q)^(sum_{i notin I} s_i)
           * E_{d uniform in K}
                [prod_{i in I}(A_i+B_i 1[d=g_i])].     (3)

Expanding the product over T subset I yields the **exact finite closed form**

    W(S)=(1-2/q)^(sum_{i notin I} s_i)
        * [ prod_{i in I} A_i
           + (1/q)*sum_{empty!=T subset I, all g_i (i in T) equal}
                    prod_{i in T} B_i * prod_{j in I\T} A_j ]. (4)

This costs O(k 2^k) rational arithmetic operations for a specified S, with bit cost governed by the lengths and alphabet encoding. It is **independent of q vertex-label enumeration**, and for the original three-path theta network uses at most eight gain-equality subsets.

The formula shows directly that the entire Boolean observation law, and thus the complete Walsh input to its symmetrization LP, depends on the path gains only through their **equality partition**. Any two assignments with the same equality partition have identical W(S) for every S. This analytically recovers a gain-graph/ASMP-9 observational-equivalence fact in the two-terminal setting.

### Relation to BM-09 and BM-10

For path lengths (2,2,2), equation (2) becomes

    E[chi_path|d]=1-4/q+(4/q)1[d=g],

the conditional expression used in the q=4 K2,3 theta proof. The three pairwise distinct gains (0,1,2) yield the exact q=4 and q=8 Fourier weights required by BM-09.

For lengths (1,2,2), equation (4) computes every one of the 32 Walsh coefficients of the BM-10 five-edge diamond. It accounts for the coefficients that remain nonzero in both worlds, explaining why a zero-spectrum-only approximation fails on that instance.

## 3. Computable tests and a scale separation

- [theta_fourier_transfer_BM12.py](theta_fourier_transfer_BM12.py) constructs the registered two-terminal path graph, computes W(S) using (4), and supplies an independent complete-label enumeration oracle for verification.
- [test_theta_fourier_transfer_BM12.py](test_theta_fourier_transfer_BM12.py) checks **every Walsh subset** on q=4 diamonds and theta graphs, the q=8 theta, graphs with custom unequal path lengths, the original BM-09/10 clean counting oracles, parallel-edge cycles, and gain equality partition invariance.
- A larger seeded symbolic query q=2^12=4096, path lengths (12,10,9) has **30 vertices and 31 edges**. A single coefficient is computed with at most eight gain-equality subset terms, without attempting 4096^30 vertex labels or 2^31 complete observation states.

This is a **Fourier coefficient oracle**, not an efficient algorithm for the full global symmetrization LP, which still has exponentially many mask variables in the number of observed edges. The distinction is load-bearing for the ASMP-14 complexity program.

## 4. BM-12/C1: the first algorithmic target inside a 2-connected block

Given the BM-11 reduction to articulation blocks and the BM-12 conditional Fourier oracle for parallel-terminal path graphs, a natural structural question is:

**Can the hypothesis-aware erasure LP on a bounded-terminal-width, bounded-overlap graph family be approximated by a polynomial-size or fixed-parameter-size set of *weighted* Walsh constraints and a certifying sparse dual, with a provable accuracy factor?**

A valid theorem requires:
- a frozen family of graph/gain pairs, the precise observation and adversary contracts, and a parameter measuring terminal/separator width;
- an explicit lower-certificate construction with finite rational bit complexity;
- a matched approximate mask-channel upper witness, or a counterfamily disproving a claimed factor;
- calibration against the BM-08 isolated cycles, BM-09 q=4/q=8 shared theta examples, BM-10 diamond, and BM-11 one-sum block extension.

The transfer formula is an elementary two-terminal conditional-independence calculation, closely related to transfer matrices and junction-tree factorization. It is a useful exact building block. Whether a **small set of weighted constraints suffices to approximate the full adversarial erasure threshold** remains genuinely open.

## 5. Previous mathematics and exact scope

This note uses classical finite-group character orthogonality, factor-graph conditioning, and gain-graph balance. Relevant background includes [Zaslavsky's balanced chromatic polynomial lectures](https://people.math.binghamton.edu/zaslav/Tpapers/gaingraphs-lecture-notes.pdf) and the [Fortuin–Kasteleyn random-cluster representation](https://mathworld.wolfram.com/PottsModel.html). BM-12 is a finite computational identity in a particular model; there is no model training, empirical safety evaluation, or claim to a new general algorithm for UGC.
