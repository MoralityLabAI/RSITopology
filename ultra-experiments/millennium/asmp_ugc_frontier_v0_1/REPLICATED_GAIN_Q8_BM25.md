# BM-25: Replication raises the sharp hypothesis-aware erasure threshold at q=8

**10 November 2026 | exact six-edge rational theorem and a 502-edge symbolic lower certificate.** This closes the first nontrivial instance of the q>=8 research question left open by [BM-24's growing-core path theorem](WREATH_THETA_SYMMETRY_BM24.md). It adds a rigorous positive interaction-cost effect when an additional repeated observation path is introduced.

The underlying Fourier, convolution and LP tools are classical. The results are exact in the registered finite gain-graph observation model. Publication novelty would require a separate adversarial-channel prior-art audit. There is no empirical AI-monitoring or root-attestation claim.

## 1. Frozen readout model and the sharp result

Let K=F2^3 (q=8). Consider n ordinary u-v paths and one exceptional u-v path, **each with two edges**. A fresh uniform vertex labeling is drawn for every episode; the monitor observes only the complete Boolean edge-satisfaction vector. In the flat world every path has total gain zero. In the frustrated world the n ordinary paths still have gain zero, while the exceptional path has a fixed nonzero gain gamma in K.

The adversary knows the hypothesis and may choose a different *within-episode correlated* XOR readout-mask distribution under each world. Each mask is independent of the **current clean satisfaction vector** and each edge is flipped with marginal probability at most eta. Let eta_sym(n;q=8,L=2) be the least uniform eta that makes the complete masked output laws identical.

**Theorem BM-25/T1 (exact q8 two-ordinary-path threshold):**

    eta_sym(1;8,2) = 1/44,                 [BM-08]
    eta_sym(2;8,2) = 5/118.                [BM-25]      (1)

For n=1, the single frustrated cycle is length four, so the BM-08 exact cycle formula gives 1/44. At n=2, the three internally disjoint two-edge paths form the K2,3 theta. The ordinary-to-ordinary four-cycle is balanced, and each ordinary-to-exceptional four-cycle is frustrated. The exact threshold increases by

    5/118-1/44 = 51/2596 > 0,

a multiplicative factor of

    (5/118)/(1/44)=110/59 ≈ 1.8644.                    (2)

The extra redundant ordinary path therefore raises the error allowance an *optimal state-aware* adversary needs to erase all statistical distinction.

**Scope:** the optimum in (1) is over **all** legal hypothesis-aware correlated masks independent of the fresh current clean vector, including those outside the symmetry-reduced family. An orbit-average argument from BM-24 guarantees an attaining pair inside the quotient without weakening the lower bound.

## 2. The clean Fourier discrepancy has seven characters

For q=8, a properly selected portion of a two-edge path contributes alpha=1-2/q=3/4 per selected edge. A **fully selected** path of gain g contributes, conditional on the endpoint difference d,

    f_g(d)=1/2 + (1/2)*1[d=g].                         (3)

Let r in {0,1,2} denote the number of fully selected ordinary paths, and let b be the number of selected edges on all remaining *proper* paths. If the exceptional path is **not** completely selected, the two worlds have identical Fourier coefficients.

If the exceptional path is complete, the exact gain-grouped terminal average gives

    W_0(S) = (3/4)^b * [7*2^(-(r+1))+1]/8,
    W_1(S) = (3/4)^b * [6*2^(-(r+1)) + 1/2 + 2^(-r)]/8.

Therefore

    Delta(S)=W_0(S)-W_1(S)
            =(3/4)^b * [1-2^(-r)]/16.                (4)

For r=0 the difference is zero, while for r>=1 it is positive. With the six edge bits ordered as the first ordinary path (0,1), second ordinary path (2,3), and exceptional path (4,5), the **entire** clean discrepancy support is

    D_clean={51,55,59,60,61,62,63},   |D_clean|=7.  (5)

This agrees with BM-24's general L=2 count 4^n−3^n at n=2.

A key mathematical subtlety is that the *optimal lower dual* uses two Fourier characters **outside D_clean**, because the adversary may choose different masks under the two hypotheses. Cleanly equal moments still constrain how the two mask channels can differ.

## 3. Exact 18-orbit attaining primal (BM-25/T1 upper)

The BM-24 symmetry group permutes the two bits within every path and also exchanges the two ordinary paths. The complete mask orbit is indexed by

    (c0,c1,c2 ; e),

where c_j counts how many ordinary paths have j flipped bits, c0+c1+c2=2, and e in {0,1,2} is the number of flipped bits on the exceptional path. There are binomial(4,2)*3=18 such orbits.

The exact attaining pair Q0/Q1 has **integer numerators over 13,216**, as follows. Each entry is the *total probability mass of that orbit*; the mass is distributed uniformly over individual masks in the orbit.

| (c0,c1,c2; e) | Flat numerator | Frustrated numerator |
|---|---:|---:|
| (0,0,2; 0) | 0 | 5 |
| (0,0,2; 1) | 10 | 0 |
| (0,0,2; 2) | 0 | 5 |
| (0,1,1; 0) | 14 | 0 |
| (0,1,1; 1) | 0 | 28 |
| (0,1,1; 2) | 14 | 0 |
| (0,2,0; 0) | 0 | 8 |
| (0,2,0; 1) | 16 | 0 |
| (0,2,0; 2) | 0 | 8 |
| (1,0,1; 0) | 0 | 136 |
| (1,0,1; 1) | 272 | 0 |
| (1,0,1; 2) | 0 | 136 |
| (1,1,0; 0) | 1,274 | 1,008 |
| (1,1,0; 1) | 0 | 532 |
| (1,1,0; 2) | 266 | 0 |
| (2,0,0; 0) | 11,088 | 11,219 |
| (2,0,0; 1) | 262 | 0 |
| (2,0,0; 2) | 0 | 131 |

Both column totals equal 13,216. Each ordinary edge **and** each exceptional edge in either world has marginal mask error exactly

    eta=5/118.                                             (6)

The [BM-25 primal implementation](state_aware_replication_BM25.py) verifies all 18 histogram Fourier equalities and the complete solver-ready rational LP matrix. Independently expanding the histograms into the original 64 Boolean mask vectors yields world-specific laws on 33 and 36 mask atoms; direct uniform-label enumeration of 8^5=32,768 graph vertex assignments per world confirms equality of **all 64 postprocessed output probabilities** with exact fractions.

## 4. A seven-character full-cube dual lower proof

Let y_S be the multiplier on the complete masked output Fourier equality at S, n_h the two normalization multipliers and z_(h,i)<=0 the twelve signed per-edge readout-cap multipliers. An admissible lower dual obeys

    -sum_(h,i) z_(h,i)=1,

and for every mask x in {0,1}^6 and h in {0,1},

    n_h + (-1)^h sum_S y_S W_h(S) (-1)^|x∩S|
          + sum_(i:x_i=1) z_(h,i) <= 0.             (7)

Such a dual certifies eta_sym >=n_0+n_1 by exact weak linear-program duality.

The following rational coefficients give **the exact optimum**:

    n_0=0,         n_1=5/118,

    y_31=y_47=608/1947,
    y_55=y_59=y_61=y_62=16/177,
    y_63=−64/59,

    z_(flat,i)=-11/236       on each of the four ordinary edges,
    z_(flat,i)=-19/118       on each exceptional edge,
    z_(frustrated,i)=-5/118  on each ordinary edge,
    z_(frustrated,i)=-19/118 on each exceptional edge. (8)

All other y_S are zero. The 12 signed marginal multipliers sum to -1, and n_0+n_1=5/118. The exact verifier checks **every one of the 128 mask-atom inequalities** in (7), with maximum slack zero.

Only three **orbit-signature** multipliers are needed before expansion into the seven original Fourier subsets. The two supports S=31,47 have equal clean Fourier coefficients in the two worlds, while S=51,60 have genuine clean discrepancies but zero multipliers in this particular optimal dual. This distinction between the *clean discrepancy set* and the *dual support needed to enforce hypothesis-aware mask compatibility* is essential.

The attaining primal from section 3 and dual (8) have the same objective. This proves (1), entirely in rational arithmetic, with no numerical optimizer required by any submitted test.

## 5. BM-25/T2: a constant-seven-character lower certificate for all n>=2

Adding ordinary paths gives a monotone sequence of minimax masking costs. If n+1 ordinary paths can be erased at cap eta, project the complete output laws and readout masks onto any n ordinary paths plus the exceptional path. The projected clean labeling law is exactly that of the n-path experiment, and the projected masks remain independent of its current clean observation, with the same per-bit caps. Therefore

    eta_sym(n+1;8,2) >= eta_sym(n;8,2).             (9)

In particular, for **all n>=2**, projection to two ordinary paths plus the exceptional path gives the exact lower bracket

    eta_sym(n;8,2) >= 5/118.                         (10)

The BM-24 common-mask sampler works for **any** q,n,L at cap 1/(4L), so for L=2,

    5/118 <= eta_sym(n;8,2) <= 1/8,   n>=2.        (11)

The inequalities in (11) are rigorous; the optimum for n>=3 remains an open problem.

There is also an explicit **sparse global dual lift** of (8). Embed the first four ordinary edge coordinates and the two exceptional edge coordinates into the 2n+2 edge reports, with all other ordinary-path coordinates ignored. Every retained clean Fourier coefficient is unchanged by adding independent ordinary paths. Extend the seven coefficients y_S to their embedded supports, place the same signed marginal multipliers on the retained six bits, and put zero multipliers on all other edges.

Every full-mask dual slack now depends on only six bits. Checking the same 128 six-bit combinations proves the dual bound **5/118 against every one of the 2^(2n+2) possible masks**. The [symbolic lift implementation](state_aware_replication_BM25.py) verifies this using BM-24's exact conditional Fourier transfer for n=2,3,5,10 and 250, with no full table expansion.

For n=250, q=8, L=2, the graph has 251 paths, 253 vertices and 502 reported edges. Its **clean Fourier discrepancy support** has 4^250−3^250 members, and the BM-24 full-mask LP quotient has 94,878 histogram classes per hypothesis instead of 2^502 individual masks. The 5/118 lower certificate still has seven Fourier characters. No exact full optimum or large LP solve is claimed for this n=250 instance.

## 6. A controlled topology-vs-holonomy comparison

The earlier [BM-09 six-edge theta theorem](THETA_CYCLE_INTERACTION_BM09.md) considered q=8 with path gains (0,1,2), making *all three* four-cycles frustrated. Its exact state-aware erasure cost was 29/630≈0.04603.

BM-25 instead uses path gains (0,0,1): one cycle is balanced and two frustrated. It has the **same six-edge graph topology**, but the exact erasure cost is 5/118≈0.04237. The difference is driven by gain-balance structure in the joint Boolean observation law. Neither topology nor the count of raw edge reports alone determines the optimal hostile-mask cost.

The single four-cycle threshold 1/44, the repeated-but-one-balanced theta threshold 5/118 and the contrabalanced theta threshold 29/630 supply **three separately certified controls** for later claims about redundancy and monitoring geometry.

## 7. Reproducibility and open mathematical frontier

- [state_aware_replication_BM25.py](state_aware_replication_BM25.py) contains the exact two-world rational orbit masks, matching three-signature histogram dual, the seven-character full-cube expansion, complete-output and 128-atom proof checks, and the n>=2 symbolic dual lift/projection bound.
- [test_state_aware_replication_BM25.py](test_state_aware_replication_BM25.py) independently checks the 18-orbit model, solver-ready LP matrix, all six individual mask marginals, 64 exact output probabilities, clean-versus-dual Fourier support distinction, arbitrary nonzero exceptional gains, strict n1-to-n2 interaction cost increase, lifted dual validity on 502 edges, and deliberate malformed primal/dual mutations.
- The full focused standard-library CPU suite includes BM-01 through BM-25 and is run on the open draft research PR.

A **numeric LP exploratory scan** for n>=3 suggests further increases in erasure cost, but no exact rational matching primal/dual has been registered for those cases. The next formal target is a sharp formula or monotone convergence limit for the q>=8 repeated-path family, ideally with an analytic dual that scales with n and with alphabet q. Equally important is whether a related replication effect survives on variable-size cores without strong path exchangeability, using a frozen readout/intervention and restoration threat model.

The results rest on established Fourier convolution, gain-graph balance, permutation-orbit LP and adversarial-channel symmetrizability. Relevant background includes [Zaslavsky, *Biased Graphs I*](https://doi.org/10.1016/0095-8956(89)90063-4), [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/), and [Modak et al., *Hypothesis Testing for Adversarial Channels* (2026)](https://doi.org/10.1109/TIT.2026.3691175). Independent prior-art review is needed before a novelty claim. These are frozen statistical channel theorems, with no empirical AI safety guarantee or independently authenticated root-state attestations.
