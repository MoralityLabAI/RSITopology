# BM-26: Sharp eight-label erasure after three ordinary path replicas

> **Subsequent result, BM-29 (10 November 2026):** [The exact infinite-replication theorem](INFINITE_REPLICATION_LIMIT_BM29.md) proves **lim_n eta_n(8,2)=5/52** in the registered hypothesis-aware, current-clean-independent readout model. The open-limit statements below record the historical status before BM-29. Finite-n sharp formulas for n>=4 and a quantitative convergence rate remain open.


**10 November 2026 | exact rational finite theorem, independent primal/dual checks, monotone-limit bracket.** This extends [BM-25's two-ordinary-path q=8 theorem](REPLICATED_GAIN_Q8_BM25.md) on the growing-core theta family from [BM-24](WREATH_THETA_SYMMETRY_BM24.md).

The result is confined to the registered statistical observation experiment. Every episode uses fresh, independently uniform gain-group vertex labels and full Boolean edge-satisfaction readouts. The adversary knows the flat/frustrated hidden hypothesis and chooses an arbitrary correlated XOR error-mask distribution independently of the **current** clean observation, with a common per-bit maximum flip probability eta. The upper and lower claims include all such hypothesis-dependent masks. No operational model-safety guarantee or conjectured Unique Games proof follows.

## 1. Statement BM-26/T1: a third exact replication threshold

Set K=F2^3, q=8. Use **n ordinary two-edge paths** joining common terminals u,v and one **exceptional two-edge path**. Each ordinary path has XOR gain zero under both hypotheses. The exceptional path has gain zero in the flat world and an arbitrary fixed nonzero gain in the frustrated world. Let eta_n denote the smallest uniform per-bit readout error cap that can equalize the **complete** Boolean output laws under the two hypotheses.

The preceding exact values are

    eta_1 = 1/44                   (BM-08),
    eta_2 = 5/118                  (BM-25).

**New exact theorem:**

    eta_3 = 751225/13956626 = 0.053825688242989... .    (1)

The strict increase over BM-25 is

    eta_3-eta_2
      = 4715355/411720467 > 0.                          (2)

This is a finite q=8 graph with **four two-edge paths, six vertices and eight observed edges**, whose cycle rank is three. The complete optimum (1) is certified by a rational upper mask pair and a rational lower dual. It does not assume the two worlds use identical masks or independent mask bits.

## 2. Exact 30-orbit attaining mask pair

BM-24's symmetry group permutes the two edges inside each path and permutes the n=3 identical ordinary paths. A mask orbit is labeled by

    (c0,c1,c2;t), where c0+c1+c2=3 and t in {0,1,2}.

The numbers c_j count ordinary paths with j flipped readout bits; t counts flipped bits on the exceptional path. Thus the full 256-mask space per hypothesis reduces to

    M=binomial(3+2,2)*3=30

mask histogram classes per world. The exact full erasure LP has **61 variables**, **31 Fourier/normalization equality rows** and **four marginal inequality rows**.

The [attaining mask table](state_aware_three_replica_BM26.py) assigns **integer orbit mass numerators over denominator 27,913,252**. Exactly 16 classes in each world have nonzero mass. All normalized weights are nonnegative and sum to one. Each ordinary readout bit and each exceptional readout bit, under **both worlds**, has marginal flip probability exactly

    eta_3 = 1,502,450 / 27,913,252
          = 751225 / 13956626.                           (3)

The exact verifier checks every nontrivial path-histogram Walsh equality, both mask normalizations and all per-type marginal constraints. An independently assembled rational LP matrix accepts the same attaining point.

To verify the claim without relying solely on BM-24's compressed Fourier code, the module also expands each mask-histogram orbit **uniformly onto its constituent full Boolean masks**, independently enumerates the 8^6=262,144 fresh uniform vertex labelings under each world, and checks equality of all **256** complete postprocessed Boolean output probabilities.

## 3. Exact lower dual over all legal masks

The rational LP dual has unrestricted Walsh equality multipliers y_S, two normalization multipliers n0,n1, and signed readout-marginal multipliers z_(h,type)<=0. A full-width mask-atom inequality is

    n_h + (-1)^h sum_S y_S W_h(S) chi_S(x)
          + sum_{e:x_e=1} z_(h,e) <=0                 (4)

for every full Boolean mask x under each hidden hypothesis. Normalize the signed marginal multipliers to sum to -1. Then weak linear-program duality gives eta>=n0+n1.

The new lower certificate uses **29 nonzero histogram Walsh multipliers** (all nontrivial signatures of this 30-orbit quotient) with exact common denominator

    D_y=3,979,313,205,120.

Its normalization numerators are

    n0_num = -117251951355,
    n1_num =  331441223355,

so the dual objective is exactly

    (n0_num+n1_num)/D_y
       = 751225/13956626.                               (5)

The four signed orbit-marginal coefficients, in order (flat ordinary, flat exceptional, frustrated ordinary, frustrated exceptional), have numerator vector

    (-2972592, 0, 0, -4005721) / 6978313.

They are nonpositive and sum to -1. The [certificate verifier](state_aware_three_replica_BM26.py) checks **all 60 orbit-mask inequalities**, both worlds, exactly with Python Fraction arithmetic. Every inequality is satisfied.

Because orbit symmetry applies to the **complete** original adversarial LP, this already proves eta>=the value in (5) against every legal correlated, world-dependent full mask distribution. The additional independent check expands the 29 orbit Walsh coefficients into **255 individual nonzero Walsh multipliers** and distributes the marginal coefficients across all eight underlying readout bits. The existing generic BM-17 verifier checks **every one of 512 full-mask dual inequalities**. The rational lower objective is unchanged by this expansion.

The primal cap (3) equals the dual value (5), proving (1). The numerator tables were reconstructed from a finite numerical LP discovery run; the committed verification path uses **only exact rational arithmetic and CPU**. No numerical optimization solver is needed to check the theorem.

The 29 histogram coefficients are an **achieved** certificate support count. There is no claim that they form a minimum-support dual.

## 4. BM-26/T2: a monotone and convergent repeated-path erasure sequence

For arbitrary q=2^s and fixed path length L, write eta_n(q,L) for the sharp hypothesis-aware erasure threshold with n ordinary paths of gain 0/0 and one exceptional path of gain 0/gamma!=0. Suppose the n+1 path instance has a successful equalizing pair (Q0,Q1) with cap eta. Project the full readouts and both masks onto any n ordinary paths plus the exceptional path.

The clean projected law is precisely the fresh-uniform-label n-path instance, and the projected masks remain independent of the current clean vector with unchanged per-bit caps. Hence

    eta_n(q,L) <= eta_(n+1)(q,L).                    (6)

BM-24 constructs a **common** mask with cap 1/(4L) for every n and q. Therefore

    0 <= eta_n(q,L) <= 1/(4L),                       (7)

and by monotone bounded convergence, the limit

    eta_infinity(q,L)=lim_(n→infinity) eta_n(q,L)     (8)

**exists** for every fixed alphabet and path length under this model. This is a theorem about existence, with no assumption that its value equals the common-channel optimum.

For q=2/4, BM-24 already proved eta_n=1/(4L) for every n and hence the limit is exactly 1/(4L).

For **q=8,L=2**, the certified third-replica bound gives the improved rigorous bracket

    751225/13956626
       <= eta_n(8,2) <= 1/8,     n>=3,              (9)

and therefore the same bracket on eta_infinity(8,2).

The **full dual for n=3 also lifts unchanged** onto any larger n, by embedding its supported Fourier characters on the first three ordinary two-edge paths and the final exceptional two-edge path and assigning zero coefficients to all other ordinary paths. Every retained clean Walsh coefficient agrees exactly with that of the n=3 system by projection. All 2^(2n+2) global full-mask dual inequalities reduce to the 512 already certified eight-bit cases. The module verifies the 255 coefficient identities for n=3,4,5,10,250 using BM-24's gain-grouped exact oracle.

Thus the 502-edge n=250 graph inherits a **255-character full-basis lower certificate**, equivalently 29 path-histogram Fourier orbit coefficients in the n=3 subgraph. The graph's full mask space and clean support cardinality are enormous, but the projection proof remains constant-sized in the original eight retained bits.

## 5. Exploratory larger-n numerical scan and the limit question

A separate SciPy/HiGHS exploration of the BM-24 quotient LP, with all normalization and nonempty Walsh equalities included, gave these **floating-point pilot values**:

| Ordinary paths n | Orbit classes per world | Numerical eta_n (exploratory) |
|---:|---:|---:|
| 1 | 9 | 0.02272727 |
| 2 | 18 | 0.04237288 |
| 3 | 30 | 0.05382569 |
| 4 | 45 | 0.06387494 |
| 6 | 84 | 0.08001167 |
| 8 | 135 | 0.08880589 |
| 10 | 198 | 0.09206396 |
| 12 | 273 | 0.09345674 |
| 14 | 360 | 0.09436694 |
| 16 | 459 | 0.09487830 |

**Only n=1,2,3 are registered as exact optima.** The other numbers are exploratory approximate LP outputs, with neither rational attaining masks nor matching exact dual certificates committed. Solver conditioning, degeneracy and untracked arithmetic precision can affect their last digits. In particular, the scan is insufficient to infer the exact asymptotic limit or to establish a proposed convergence rate.

The numerical values remain below BM-24's common-channel limit 1/8. The rigorous theorem establishes that eta_infinity exists somewhere inside (9); whether it **equals 1/8** or a smaller value remains open. A viable next direction is a uniform-in-n lower bound using ordinary-path exchangeability and Fourier moments of many fully selected paths. An independent analytic obstruction or family of common/noncommon attaining masks would decide the limit.

## 6. Research significance, verification and limits

The exact three-replica theorem is a second strict replication-cost increase after BM-25. It also exposes a scaling issue in certificate structure: BM-25's lower dual required three histogram signatures, whereas this independently reconstructed n=3 optimum has 29 nonzero histogram coefficients. This numerical observation about one attained certificate is **not** a proven minimum-sparsity lower bound.

[BM-26 code](state_aware_three_replica_BM26.py) stores the rational primal/dual and the exact full-mask expansion, checks the 30-class quotient LP, and lifts its lower dual to arbitrary n>=3. [BM-26 tests](test_state_aware_three_replica_BM26.py) reconstruct independent complete output laws and the generic full dual, compare all four exact readout marginal bounds, test all nonzero exceptional gains, check the 502-edge projection, and reject perturbed invalid masks and duals. The focused CI runs the full finite exact suite with no SciPy dependency.

Classical antecedents include Walsh Fourier transforms, LP strong duality, finite adversarial-channel symmetrizability, and the wreath-product symmetry reduction from BM-24. Relevant background: [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/), [Zaslavsky, *Biased Graphs I*](https://doi.org/10.1016/0095-8956(89)90063-4), and [BM-25 q=8 replication note](REPLICATED_GAIN_Q8_BM25.md). This is a narrowly defined finite channel theorem, without independent novelty certification, live AI-control evaluation, or trusted intervention/restoration claims.
