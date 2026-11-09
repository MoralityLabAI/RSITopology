# BM-10: Weighted Fourier constraints beat the zero-spectrum surrogate

**10 November 2026.** Exact finite theorem, independent rational primal/dual checks. Companion to [BM-09 theta interactions](THETA_CYCLE_INTERACTION_BM09.md) and the [BM-08 sharp isolated-cycle bound](SHARP_ERASURE_OPTIMALITY_BM08.md). This is a registered small-instance result in the stated adversarial readout model, not a general formula for all gain graphs.

## 1. The five-edge diamond graph

The graph is the theta with three u-v paths of lengths (1,2,2). It has four vertices, five edge occurrences, two triangles sharing a central edge, and an outer four-cycle. Fix the edge order

    e0=(0,1),  e1=(0,2), e2=(2,1),
    e3=(0,3),  e4=(3,1).

The alphabet is K=F₂², q=4. Compare the flat connection c=0 with shifts c=(0,1,0,2,0), assigning distinct u-v path gains (0,1,2). Every one of the three cycles in the nonflat world has nonzero holonomy. The first sampling model draws a fresh, uniform label a in K^4; the monitor receives all five Boolean edge-satisfaction indicators. A readout adversary may choose a separate XOR mask distribution Q0 or Q1 after seeing the hidden flat/nonflat hypothesis, but the mask must be independent of the **current** clean observation. Each edge's mask marginal is at most a uniform cap eta.

Let P0,P1 be the exact 32-outcome clean Boolean distributions. Define

    eta_sym(G,c;q)=min{eta: P0*Q0=P1*Q1,
                        Q0,Q1 are distributions on {0,1}^E,
                        Pr_Qh(M_i=1)<=eta for every h,i}.

**Theorem BM-10/T1.**

    eta_sym(diamond,c;4)=1/5.                         (1)

This is greater than the isolated frustrated triangle's sharp BM-08 cap of 1/6; the corresponding interaction index is

    I_4(diamond,c)=(1/5)/(1/6)=6/5.                  (2)

The six-edge K2,3 contrabalanced theta from BM-09 has index 4/3. Both examples have cycle rank beta1=2, while the cycle lengths and interaction constraints differ.

## 2. Exact primal upper certificate

A **common** mask distribution Q0=Q1 attains eta=1/5. Index each five-bit mask by its integer value. Its nonzero masses have denominator 20:

| Mask integer | Numerator |
|---:|---:|
| 0 | 5 |
| 1, 2, 4, 8, 16 | 2 each |
| 5, 9, 10, 18, 20 | 1 each |

The total mass numerator is 20. Every bit's marginal numerator is 4, giving error 4/20=1/5. Enumerating all 4^4=256 uniform vertex labelings yields integer clean counts C0,C1. The submitted pure-Python verifier checks **every** one of the 32 output equations

    sum_m C0(y XOR m) Q(m) = sum_m C1(y XOR m) Q(m).

All equalities hold exactly with rational/integer arithmetic.

## 3. Exact sparse rational dual lower certificate

Write the Walsh coefficient of the clean Boolean law under world h as

    hat P_h(S)=E_{X~P_h}[(-1)^{popcount(X & S)}].

In the full erasure linear program, equality of masked outputs is equivalent to

    hat P0(S) E_Q0 chi_S(M)
      -hat P1(S) E_Q1 chi_S(M)=0               for every S!=empty,

along with normalization sum_m Qh(m)=1. The per-edge inequalities are
sum_{m:m_i=1}Qh(m)-eta<=0. We minimize eta.

A sparse dual certificate has normalization multipliers

    y_norm0=1/20,  y_norm1=3/20,

and the following nonzero Walsh multipliers y_S:

| S | y_S | S | y_S |
|---:|---:|---:|---:|
| 1 | 1/10 | 2 | -1/10 |
| 4 | 1/10 | 6 | -1/5 |
| 7 | 1/5 | 9 | -1/5 |
| 10 | -1/5 | 11 | 2/5 |
| 14 | 2/5 | 17 | 1/5 |
| 18 | 1/5 | 19 | -2/5 |
| 22 | 2/5 | 25 | 2/5 |
| 27 | -2/5 | 29 | -2/5 |
| 30 | -2/5 |  |  |

The only nonzero marginal dual multipliers are

    z_(flat,1)=z_(flat,3)=-1/5,
    z_(frustrated,0)=z_(frustrated,2)
                    =z_(frustrated,4)=-1/5.

Their sum is -1, which exactly saturates the eta coefficient of the dual. The dual objective y_norm0+y_norm1 is 1/5.

**Universal dual verification.** For every one of the 32 masks m in either world h, the exact coefficient inequality is

    y_norm0 + sum_S y_S hatP0(S) chi_S(m)
       + sum_{i:m_i=1} z_(flat,i) <= 0,

    y_norm1 - sum_S y_S hatP1(S) chi_S(m)
       + sum_{i:m_i=1} z_(frustrated,i) <= 0.

The [verifier](diamond_weighted_fourier_BM10.py) checks all **64 inequalities** against exact rational Walsh coefficients. All 17 listed y_S are included, together with zero values for every other S. By weak linear-program duality, *every* erasing mask pair satisfies eta>=1/5. Combined with the primal mask distribution, this proves (1).

## 4. A provably inadequate zero-Fourier shortcut (BM-10/T2)

One appealing lower-bound heuristic looks only at Fourier indices where the flat clean distribution has nonzero Walsh coefficient and the frustrated clean distribution has **zero** coefficient. Such indices enforce E_Q0 chi_S(M)=0 for every erasing mask pair. On this diamond, direct exact calculation gives precisely the two index masks

    Z={30,31},   bit sizes 4 and 5.

The shortcut considers only the constraints

    E_Q chi_30(M)=0,  E_Q chi_31(M)=0,

along with mask normalization and per-edge marginal costs. Its **exact** optimum is 1/8:

- The index 30 has four bits, so chi_30-mean zero requires at least 1/2 probability of odd intersection with those four positions. By a union bound, 4eta>=1/2 and eta>=1/8.
- The following mask law with denominator 16 attains the bound and satisfies both constraints:

| Mask integer | Numerator |
|---:|---:|
| 0 | 7 |
| 1, 8, 9 | 1 each |
| 2, 4, 16 | 2 each |

Every edge has marginal error 2/16=1/8. Its Walsh expectations on S=30 and 31 both vanish, yet its masked full output laws **differ**.

Thus the zero-spectrum-only relaxation underestimates the true erasure cost:

    eta_full / eta_zero_only = (1/5)/(1/8)=8/5.       (3)

This is a concrete counterexample to treating **locations of Fourier zeros alone** as a complete geometric predictor of monitor symmetrizability. Nonzero Fourier coefficient ratios and their joint compatibility matter, even when the graph has only two independent cycles.

## 5. Toward a general weighted Fourier interaction certificate

The exact finite result motivates a more appropriate LP-based graph invariant. For a fixed gain-graph pair (G,c) and alphabet q, construct the complete Walsh coefficient vectors hatP0,hatP1. Define a certificate as rational numbers y_norm0,y_norm1, multipliers y_S for nonempty edge subsets, and nonpositive marginal multipliers z_(h,e), satisfying

    -sum_(h,e) z_(h,e)<=1,

together with all mask-atom inequalities from section 3. Every such certificate gives the universal **computable lower bound**

    eta_sym(G,c;q) >= y_norm0+y_norm1.               (4)

The optimum of this dual equals the primal eta_sym by finite LP strong duality, with the original channel assumptions. This is a general *finite characterization*, rather than a closed-form graph invariant. The substantive research question is to obtain **sparse analytic certificates** from the cycle-edge incidence hypergraph and the nonzero Fourier weights, with a provable approximation ratio and scalable computation.

**BM-10/C1 (proposed):** Identify graph families of bounded cycle-overlap complexity for which a polynomial-size (or fixed-parameter-size in an overlap-width parameter) Fourier dual certificate approximates eta_sym to an alphabet-independent constant factor. A counterfamily where all such sparse certificates lose an unbounded factor would refute this conjecture once 'overlap width' and certificate family are frozen. This is a proposal, not an established conjecture theorem.

The known BM-08 isolated-cycle certificate, BM-09 theta/cactus examples and the diamond (1,2,2) certificate become the required calibration suite. Graph cycle rank alone is insufficient to predict the erasure gap; the same five-edge graph illustrates the need to retain the magnitude and compatibility of Fourier coefficients.

## 6. Verification and prior-art boundary

The new pure-Python modules are:

- [Exact diamond primal/dual verifier](diamond_weighted_fourier_BM10.py).
- [Seven independent tests](test_diamond_weighted_fourier_BM10.py) comparing full-label enumeration against the earlier `finite_seed.Game` oracle, checking every rational mask and dual constraint, and probing perturbations of the primal distribution.

No floating-point or LP solver is invoked by the committed verification path. The numerical optimizer was only used to discover a candidate primal/dual solution. The dual inequalities are the actual proof certificate. This finite application of LP duality and Walsh analysis belongs in the existing mathematics of adversarial channel symmetrization; new general structure theorems require separate novelty review.

Related sources: [Zaslavsky, *Biased graphs I* (1989)](https://doi.org/10.1016/0095-8956(89)90063-4), [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/), and [BM-09 theta proof](THETA_CYCLE_INTERACTION_BM09.md).
