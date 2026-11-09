# BM-13: Sparse weighted-Fourier certificates and a sharp measurement-degree hierarchy

**10 November 2026 | exact finite theorems, separate rational checks.** This note closes two useful finite problems inside the open structural dual-certificate question of [BM-10](WEIGHTED_FOURIER_DIAMOND_BM10.md), following [BM-11 block tensorization](BLOCK_TENSOR_ERASURE_BM11.md) and [BM-12 theta Fourier transfer](THETA_FOURIER_TRANSFER_BM12.md). The new results are exact for two registered q=4 gain networks. Whether the sparse-certificate sizes scale favorably through genuinely 2-connected graph families is still open.

## 1. A restricted observation hierarchy

For the registered flat and frustrated Boolean edge-satisfaction distributions P0,P1, and separate adversarial XOR mask laws Q0,Q1, define the **degree-d Fourier erasure relaxation** by requiring output-coefficient equality only on Walsh subsets S satisfying 1<=|S|<=d:

    hatP0(S)*hatQ0(S) = hatP1(S)*hatQ1(S),
    |S|<=d.

Retain mask normalization and the per-bit uniform error allowance eta. Let eta_d be the minimum eta satisfying these constraints. The full erasure threshold is eta_m for m=|E|.

The degree-d LP is a mathematical *relaxation* in which a verifier observes only the truncated family of Fourier statistics. It is not the same as a physical monitor that receives raw complete edge patterns and chooses how to process them. For d'<d, eta_d'<=eta_d. Any valid dual with support at degree <=d yields a certified lower bound on eta_d and all higher levels.

If every edge subset of cardinality <=d has zero holonomy, then the clean P0 and P1 Walsh moments agree at all those degrees and eta_d=0 by taking zero noise. This is the finite holonomy-girth blindness phenomenon from UGCS-02/ASMP-14.

## 2. Exact degree profiles (BM-13/T1)

For the five-edge q=4 contrabalanced **diamond**, whose shortest unbalanced cycles have length 3:

| Max Walsh degree d | 0,1,2 | 3 | 4,5 |
|---:|---:|---:|---:|
| Exact eta_d | 0 | 1/6 | 1/5 |

For the six-edge q=4 contrabalanced **K2,3 theta**, whose shortest unbalanced cycles have length 4:

| Max Walsh degree d | 0,1,2,3 | 4 | 5,6 |
|---:|---:|---:|---:|
| Exact eta_d | 0 | 1/8 | 1/6 |

These are **exact finite optimum values** with explicit primal masks and lower certificates, not numerical approximations.

### Proof of the lower and upper bounds

At degrees below the shortest frustrated cycle, the Fourier data agree between worlds and a zero mask attains eta_d=0. At the first nonzero degree, projecting the truncated Fourier equalities onto one entire frustrated shortest cycle includes every Fourier subset of that cycle. BM-08's sharp q=4 single-cycle erasure theorem therefore gives eta_3>=1/6 for the diamond and eta_4>=1/8 for the theta.

For the matching upper witnesses:
- Diamond degree 3: use the *same* mask distribution in both hypotheses, putting probability 1/6 on the zero mask and each of the five singleton edge flips. Every full triangle Fourier character has zero mask expectation because it has three edges, while all smaller forest coefficients already agree.
- Theta degree 4: use zero-mask probability 2/8 and singleton-flip probability 1/8 on each of the six edges. Every full four-cycle Fourier character has zero expectation. All lower degrees remain matched.
- Diamond degrees >=4: reuse the full BM-10 common mask with denominator 20 and per-bit cap 1/5.
- Theta degrees >=5: reuse the full BM-09 common mask with denominator 12 and per-bit cap 1/6.

The following sparse dual certificates prove the full lower bounds **already at degree m-1**, so degree m adds no additional erasure cost.

## 3. Eight-term diamond dual replaces the original 17-term witness (BM-13/T2)

The previous BM-10 lower proof was certified by 17 nonzero Walsh multipliers. A new independently verified dual needs only **eight** Fourier supports:

    S={7,15,23,24,25,26,28,30}.

Set normalization multipliers y0=y1=1/10. Assign their respective Walsh multipliers:

    y_7= 2/5,  y_15=-2/5, y_23=-2/5, y_24=-1/5,
    y_25=1/5, y_26= 2/5, y_28= 2/5, y_30=-2/5.

Every edge in both worlds receives marginal dual multiplier -1/10. The ten marginal multipliers sum to -1, so the eta coefficient is normalized correctly, and the objective y0+y1=1/5.

For every five-bit mask m under hypothesis h, check

    y_h+(-1)^h sum_{S in supports}
       y_S hatP_h(S)(-1)^|m intersect S|
       - |m|/10 <= 0.

The rational verifier evaluates all 64 mask-atom inequalities against the independent exact clean probability census. All hold. Weak LP duality proves eta_d>=1/5 for d>=4. The existing full BM-10 mask attains it, completing the exact degree-4 optimum.

**Claim boundary:** This is a sparse *attaining* certificate with eight Fourier terms. A global minimum support cardinality among all possible duals has not been proven.

## 4. Five-term theta dual, with no degree-six Fourier term (BM-13/T3)

The six-edge q=4 contrabalanced theta has an even more compact lower witness. Only **five Fourier subsets** are needed:

    S={15,51,60,31,47}.

The first three are the three complete frustrated four-cycles, and the latter two are five-edge subsets. Define

    y_norm0=1/6, y_norm1=0,
    y_15=-2/3, y_51=-1/3, y_60=-1/3,
    y_31= 2/3, y_47= 2/3.

Give each flat-world edge a marginal multiplier -1/6 and give the frustrated-world marginal constraints multiplier zero. Every listed Fourier coefficient in the frustrated world vanishes at q=4, so the frustrated-world mask-atom dual inequalities are identically zero. In the flat world, exact verification checks

    1/6 + sum_{S in five supports}
       y_S hatP0(S)(-1)^|m intersect S| - |m|/6 <=0

for **all 64 masks m**. The six negative marginal multipliers sum to -1; the dual objective is exactly 1/6.

This proves eta_5>=1/6, and BM-09's explicit mask distribution attains it. Every Fourier coefficient at degree six is therefore redundant for this **particular optimum**. The six-edge q=4 theta's exact symmetrization cost is already certified using degree-five moments. Again, there is no claim that five is the smallest possible number of dual supports.

## 5. Relationship to the open sparse-certificate conjecture

The observed minimum **degree** required to certify the full erasure cost is 4 on the diamond and 5 on the theta, each one below the total number of observed edges. The two graphs have equal cycle rank beta1=2. Their Fourier hierarchy jumps as more overlapping-cycle constraints enter the observable family:

    diamond: 0 -> 1/6 -> 1/5,
    theta:   0 -> 1/8 -> 1/6.

BM-10 showed that retaining only Fourier zero locations misses full erasure cost on the diamond. BM-13 now shows that **a small selected set of weighted, nonzero coefficients** can nonetheless certify the exact optimum in both seed graphs. Together with BM-11, which lifts a block-local dual unchanged through one-vertex sums, this suggests the following improved research problem.

**BM-13/C1 (open):** Freeze a class of 2-connected gain graphs, alphabet regime, bounded cycle-intersection width w, and a certificate grammar. Determine whether there is a constructive algorithm producing an epsilon-approximate lower bound on eta_sym from at most f(w,1/epsilon) poly(|V|) weighted Walsh constraints, together with an explicit compatible upper mask, at stated bit complexity. The theorem must charge full certificate *verification* cost and maintain the hypothesis-aware correlated-readout model. Candidate counterexamples should include families with growing cycle overlap and no articulation decomposition.

BM-11 gives an exact reduction across articulation blocks and BM-12 computes individual theta Walsh coefficients in 2^k gain-equality operations. BM-13 provides sharp finite rational targets within those blocks. This collection is a mathematical foundation for testing an ASMP-14 structural monitoring theorem, not evidence that the conjectured scaling is already possible.

## 6. Reproduction

- [Exact sparse dual and hierarchy module](sparse_fourier_degree_BM13.py): 8-term diamond/5-term theta duals, all exact rational per-mask inequalities, and explicit common-mask witnesses for every Fourier-degree cutoff.
- [Independent tests](test_sparse_fourier_degree_BM13.py): cross-check previous BM-09/10 primal/duals, independently recompute every Walsh coefficient from the clean integer census, verify all 64/128 mask constraints, and confirm each degree profile and its next-degree violating witnesses.
- No SciPy or LP solver is invoked in the committed verification path; a numerical LP was used only to discover the rational certificates, which are verified exactly.

Historical mathematics: Walsh Fourier transformations on the Boolean cube, weak linear-program duality and gain-graph cycle geometry are classical. See [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/), [Zaslavsky's gain-graph notes](https://people.math.binghamton.edu/zaslav/Tpapers/gaingraphs-lecture-notes.pdf), and the earlier [BM-10 theorem note](WEIGHTED_FOURIER_DIAMOND_BM10.md). Promotion of BM-13 to an independent novelty claim requires a separate prior-art review.
