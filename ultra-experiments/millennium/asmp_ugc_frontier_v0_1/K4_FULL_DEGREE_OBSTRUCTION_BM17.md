# BM-17: K4 requires its highest Fourier degree for exact readout erasure

**10 November 2026 | exact finite primal-dual theorem and hostile control.**

This extends the [BM-13 finite Fourier hierarchy](SPARSE_FOURIER_DEGREE_BM13.md) and [BM-16 general-separator coefficient oracle](SEPARATOR_FACTOR_TRANSFER_BM16.md). It is a registered counterexample to a tempting extrapolation from the five-edge diamond and six-edge theta: **degree m-1 Fourier observation constraints do not always determine the complete adversarial erasure threshold on a connected 2-connected gain graph with m edges**.

The result is a finite application of linear-program duality and the Walsh basis, with independent exact rational primal and dual verifiers. It does **not** prove a general lower bound on Fourier-certificate sparsity for bounded-treewidth graphs, and does not establish an operational AI-safety result.

## 1. Frozen graph, connection and readout game

Let G=K4 with vertices {0,1,2,3} and six **ordered edge occurrences**

    e0=01, e1=02, e2=03, e3=12, e4=13, e5=23.

The label alphabet is K=F2² (q=4). The flat world has gains c0=(0,0,0,0,0,0), and the frustrated world has

    c1=(0,0,0,1,2,1).                                  (1)

Every one of the four triangles has nonzero gain holonomy. The three nontrivial fundamental-cycle returns are 1,2,1, so the numerical holonomy-image subgroup has order four. The graph has cycle rank three, is 3-vertex-connected and has treewidth three. It cannot be decomposed into the parallel u-v paths of BM-14, nor the two-terminal series-parallel algebra of BM-15.

Draw a uniformly random labeling a in K^4 independently for each observation episode, and report the complete vector X of six Boolean satisfied-edge indicators. For the two hypotheses h=0,1 denote the clean observation laws P_h on {0,1}^6.

The readout adversary may choose **two separate, hypothesis-aware, correlated XOR mask distributions** Q_0 and Q_1, independent of the *current* clean satisfaction vector. Each mask coordinate must have marginal flip probability <=eta. The exact complete-output erasure problem is

    min eta
    s.t.  P0*Q0 = P1*Q1
          Q_h >=0, sum Q_h=1,
          Pr_Qh[M_e=1] <= eta, for every h,e.           (2)

Under a common mask Q0=Q1 we obtain a legitimate special case. The optimal erasing mask for this instance turns out to be **common**; the lower-bound dual remains valid against all hypothesis-aware pairs.

For each integer degree 0<=d<=6, relax equation (2) to require equality only for Walsh coefficients indexed by edge sets S with |S|<=d. Call its optimum eta_d. These are linear programs over the **same unrestricted Q_0 and Q_1** with fewer output-equality constraints. The sequence eta_0,...,eta_6 is nondecreasing, and eta_6 is the complete output-erasure threshold.

## 2. Exact theorem BM-17/T1: a nontrivial degree-six jump

The exact optimal values are

| Maximum Walsh degree d | Exact eta_d | Decimal |
|---:|---:|---:|
| 0,1,2 | 0 | 0 |
| 3 | 1/6 | 0.1666667 |
| 4 | 1/5 | 0.2000000 |
| 5 | 4/19 | 0.2105263 |
| 6 | 3/14 | 0.2142857 |

The degree-five/full-degree gap is strictly positive:

    eta_6 - eta_5 = 3/14 - 4/19 = 1/266.             (3)

**Proof by matched exact rational LP certificates.** For every d>=3, [k4_high_degree_BM17.py](k4_high_degree_BM17.py) contains:
- two explicit nonnegative **integer-numerator mask distributions** Q0,Q1 and a common denominator, with eta_d fixed to the table value;
- a rational Walsh dual indexed by Fourier subsets S of size at most d, two normalization multipliers, and twelve nonpositive readout-marginal multipliers.

For every edge subset S with |S|<=d, the verifier checks exact equality

    hatP0(S) hatQ0(S) = hatP1(S) hatQ1(S),            (4)

and checks all **twelve** mask marginal bounds. This certifies eta_d is *at most* the table value.

For the dual, write y_S for each nonzero Fourier multiplier, y_norm,h for the two normalization multipliers, and z_(h,e)<=0 for the twelve marginal multipliers. Verify

    -sum_(h,e) z_(h,e)=1,                           (5)

and, for **every** mask m in {0,1}^6 under each hypothesis h,

    y_norm,h + (-1)^h sum_S
       y_S hatP_h(S) (-1)^{|m intersect S|}
       + sum_{e:m_e=1} z_(h,e) <= 0.               (6)

The verification checks **128 mask-atom inequalities** at each degree. Weak LP duality then proves the universal lower bound

    eta_d >= y_norm,0 + y_norm,1.                   (7)

For all four nontrivial degrees, the normalization objective in (7) equals the achieving primal cap, establishing the exact optima. This proof includes the full **hypothesis-aware** channel set, even though some optimal primal masks are hypothesis-blind.

At degrees zero, one and two, the clean moments agree because every edge set with at most two occurrences is a forest; the zero error mask satisfies the relaxed equality. An elementary dual with objective zero proves nonnegativity.

The finite tests compare *all 64 clean Walsh coefficients of both hypotheses* against the independent BM-16 factor-elimination code, which uses a distinct calculation from the full-label census used by the generic certificate verifier. The source data therefore have a second exact oracle.

### Full-degree primal (compact explicit witness)

At d=6 the two optimal masks are identical, with denominator 56 and the following nonzero integer masses:

| Mask index | Numerator | Mask index | Numerator |
|---:|---:|---:|---:|
| 0 | 10 | 1 | 3 |
| 2 | 6 | 4 | 3 |
| 5 | 2 | 8 | 3 |
| 9 | 2 | 12 | 2 |
| 13 | 1 | 16 | 6 |
| 18 | 6 | 32 | 3 |
| 33 | 2 | 36 | 2 |
| 37 | 1 | 40 | 2 |
| 41 | 1 | 44 | 1 |

They total 56, and every edge has marginal flip mass 12/56=3/14. The verifier checks exact equality of **all 64 complete output probabilities** after Boolean XOR convolution, independently of the Walsh equality equations.

The degree-five primal has distinct Q0 and Q1 distributions with denominator 152, both satisfying all degree-five Fourier equalities at eta=4/19. Their **complete output laws differ** in the six-edge Walsh character. This demonstrates directly that the missing top-degree statistic carries usable information after every lower-degree statistic has been exactly masked.

### Size of verified certificates

The constructed dual proofs have the following nonzero Walsh terms:

| Degree | Nonzero Walsh dual supports | Primal denominator |
|---:|---:|---:|
| 3 | 1 | 6 |
| 4 | 18 | 20 |
| 5 | 42 | 152 |
| 6 | 34 | 56 |

These are **feasible attained support sizes**, with no claim that any cardinality is smallest possible. The data were discovered with a numerical finite LP and reconstructed as exact fractions; GitHub tests use only the standard library and independent rational checks.

## 3. Relation to ASMP-14's certificate-width program

The earlier graph experiments give a useful progression:

| Graph | Cycle rank | Treewidth | Exact q=4 erasure cap | Highest degree needed in registered profile |
|---|---:|---:|---:|---:|
| One frustrated triangle | 1 | 2 | 1/6 | 3 |
| Five-edge diamond, all cycles frustrated | 2 | 2 | 1/5 | 4 of 5 |
| Six-edge contrabalanced theta | 2 | 2 | 1/6 | 5 of 6 |
| Four-vertex K4, gains (0,0,0,1,2,1) | 3 | 3 | **3/14** | **6 of 6** |

For K4, the ratio to the strongest individual frustrated triangle's BM-08 erasure threshold is

    I_4(K4,c)=(3/14)/(1/6)=9/7.                    (8)

This is a finite example where the entire top-degree Fourier constraint remains necessary **for the exact optimum**. The shorter BM-13 conjectural shortcut of stopping at degree m-1 would fail. A valid structural theorem must allow higher-order weighted interactions even for bounded-size separators.

K4 also shows the distinction between the BM-16 capability (each clean Fourier coefficient is efficiently computed at bounded width) and the **joint adversarial mask LP** (which may have constraints involving all observed edges). Exact coefficients are needed to instantiate the latter; their efficient availability alone does not imply that a low-degree truncation achieves its optimum.

The graph has only six edges, so this example does **not** imply asymptotic hardness of the erasure LP for fixed treewidth. A strong next theorem or counterfamily must explicitly charge separator width, alphabet encoding, graph size, target approximation epsilon and the number of weighted Fourier dual constraints.

## 4. General-purpose certificate checker

The new [generic_fourier_erasure_BM17.py](generic_fourier_erasure_BM17.py) accepts any matching pair of finite ordered gain graphs, an integer Fourier-degree cutoff, and exact rational primal/dual witnesses. It checks all Walsh equalities, both mask normalizations, every edge marginal and the complete finite weak-duality inequalities. An exact matched witness pair returns a receipt containing the optimum and whether the **complete** output distributions already agree.

This avoids relying on a numerical LP solver in CI and exposes a deterministic, falsifiable certification interface for subsequent conjecture tests on other small gain graphs. Inputs are restricted to modest graphs for direct label enumeration, and the implementation performs exponential mask-atom checking. It is a research oracle for discovering and verifying small cases rather than an efficient general algorithm.

[Test coverage](test_k4_high_degree_BM17.py) includes malformed mask laws, invalid dual signs and support degree, perturbations of the full mask witness, the degree-five/full-degree distinction, q=4 K4 triangle holonomies, and independent BM-16 coefficient agreement. The focused CI workflow exercises these alongside the earlier BM-01 through BM-16 modules.

## 5. Novelty and next steps

The certificate calculation belongs to established finite LP duality, Walsh Fourier analysis and adversarial-channel symmetrization. See [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/), [Zaslavsky's biased graphs](https://doi.org/10.1016/0095-8956(89)90063-4), and [Modak et al., *Hypothesis Testing for Adversarial Channels* (2026)](https://doi.org/10.1109/TIT.2026.3691175). The exact finite instance is useful as a registered negative control and source of certificate data; it does not by itself establish a new asymptotic complexity theorem, UGC implication, or model-safety guarantee.

A next useful frontier is to investigate **families of biconnected partial k-trees**, where all clean Fourier coefficients can be computed by BM-16, to determine whether approximate hostile-mask dual proofs need high Fourier degree or many incompatible constraints as graph size grows. This would test the still-open ASMP-14 general certificate-width conjecture under a frozen observation and attacker knowledge model.
