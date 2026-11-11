# BM-19: Support-aware Fourier completion after a frozen partial readout policy

**10 November 2026 | exact finite LP theorem and five certified witnesses.** This extends [BM-18 universal completion](UNIVERSAL_FOURIER_COMPLETION_BM18.md) and uses the [BM-17 graph-pair certificate model](K4_FULL_DEGREE_OBSTRUCTION_BM17.md).

The central object is the **residual Fourier support of a specific partial readout-mask pair**. It is a graph-dependent collection of Walsh characters still distinguishing the two hidden hypotheses. The goal is to add one common, observation-independent XOR postprocessor at the least possible per-edge error cost. This is a classical finite Fourier-annihilation LP specialized to the gain-monitoring channel. The exact optimality claims in this note apply to the *frozen partial masks* listed below.

## 1. The exact support-aware completion theorem (BM-19/T1)

Let P0,P1 be any two probability distributions on m Boolean edge observations. Fix a pair of existing possibly **hypothesis-dependent and internally correlated** XOR error-mask laws Q0,Q1, each independent of the current clean observation. Their output laws are

    F0=P0*Q0,       F1=P1*Q1,

where * denotes convolution on the binary cube {0,1}^m. Suppose they already satisfy every Fourier equality up to a registered degree d, as in BM-17. Define their actual discrepancy coefficients

    Delta(S)=hat F0(S)-hat F1(S),     S subset [m],

and the *residual discrepancy support*

    D={S != empty : Delta(S) != 0}.                    (1)

The finite output laws are normalized, so the empty-set discrepancy vanishes.

Now apply the **same** independent XOR mask R to both output channels. Because Fourier transforms diagonalize XOR convolution,

    hat(F0*R)(S)-hat(F1*R)(S)=Delta(S)*hat R(S).        (2)

The full postprocessed output distributions are identical **if and only if**

    hat R(S)=0 for every S in D.                      (3)

In this fixed-partial-pair completion problem, the numerical magnitudes of the nonzero Delta(S) drop out of the equality constraints (3). Their **locations** determine the exact postprocessing feasibility LP. This simplification is specific to *adding a common independent mask after Q0 and Q1 are frozen*; choosing both original masks jointly, as in BM-10, still requires the weighted Fourier amplitudes.

### Exact finite primal LP

Choose a probability mass w_z for every Boolean mask z in {0,1}^m and a uniform per-bit cap r. The **optimal common completion rate** is

    r*(D) = min r
    s.t.  sum_z w_z=1, w_z>=0,
          sum_z w_z (-1)^(|z intersect S|)=0   for S in D,
          sum_(z:z_i=1) w_z <= r            for i=1..m. (4)

This is a rational LP with 2^m+1 variables, 1+|D| equality rows and m marginal inequalities. It is feasible for r=1/2 by independent fair noise on every bit, and its optimum lies in [0,1/2]. In general it remains exponential in m, even if |D| is small.

### Exact rational dual

Let y0 be the normalization multiplier, y_S an unrestricted multiplier for each S in D, and z_i<=0 the marginal multipliers, with

    -sum_i z_i=1.

If for every mask x in {0,1}^m,

    y0 + sum_(S in D) y_S (-1)^(|x intersect S|)
       + sum_(i:x_i=1) z_i <=0,                       (5)

then every feasible completion mask has cap r>=y0. To see this, average (5) against w: the Walsh terms vanish by (4), leaving

    y0 + sum_i z_i p_i <=0,

where p_i<=r, so y0<=-sum_i z_i p_i<=r. Matching primal and dual values certify the exact r*(D) without requiring a numerical LP solver at verification time. [support_aware_completion_BM19.py](support_aware_completion_BM19.py) checks all 2^m dual inequalities and generates the exact solver-ready matrix.

### Effect on the original partially masked system

Let the original masks have marginal caps eta<=1/2. Take an optimal R with marginal cap r=r*(D)<=1/2. If p_(h,i)<=eta is the initial per-edge flip probability and t_i<=r is the independent postprocessor's flip probability, the final XOR mask's edge flip probability is

    p_(h,i)+t_i-2p_(h,i)t_i
      <= eta+r*(1-2eta).                             (6)

Thus the cost of **fully completing the frozen degree-d witness** is bounded by

    eta_complete <= eta_d+r*(D)*(1-2eta_d).           (7)

If all original marginals equal eta_d and the worst postprocessor marginal reaches r*(D), this upper bound equals the actual completed cap.

Equation (7) yields a graph-specific improvement over BM-18's universal bound whenever r*(D) is smaller than the optimal graph-independent annihilator rate. The globally reoptimized full LP can achieve a lower cost by replacing Q0 and Q1; the completion algorithm does not prohibit that.

## 2. BM-19/T2: an analytic sharp K4 degree-four witness

Use the registered q=4 K4 flat-vs-(0,0,0,1,2,1) experiment from BM-17. The original degree-four attaining mask is common to both worlds and has exact cap

    eta_4=1/5.

Directly computing the exact Fourier transforms of the two *partially masked complete output laws* leaves

    D_4={47,61,63},                                  (8)

with edge-support sizes 5,5,6.

**Lower bound:** `hat R(47)=0` implies the parity of flips on the five edges in set 47 is odd with probability exactly 1/2. The odd-parity event requires at least one of those five edges to flip. By the union bound, for any legal R,

    1/2 <= sum_(i in 47) Pr(R_i=1) <= 5r.

Hence r>=1/10.

**Matching upper witness:** define R using the following exact numerator masses over denominator 20:

| Boolean mask index | Numerator |
|---:|---:|
| 0 | 9 |
| 1,4,8,32 | 2 each |
| 2,16,18 | 1 each |

Every edge has flip probability 2/20=1/10. Direct evaluation gives

    hat R(47)=hat R(61)=hat R(63)=0.

Therefore

    **r*(D_4)=1/10.**                              (9)

A very sparse exact dual verifies the same lower bound: take y0=1/10, y_61=-1/10, z_i=-1/5 for the five edges in support 61 and z_i=0 for its one excluded edge. Equation (5) holds for all 64 masks. The single five-edge character in the dual recovers the union-bound proof.

The completed original pair has cap

    eta_4+(1/10)*(1-2eta_4)
      =1/5+(1/10)*(3/5)
      =**13/50 = 26%**.                             (10)

The **universal** BM-18 degree-four postprocessor has r=1/6, yielding a completed cap 3/10=30%. The best **globally reoptimized** K4 full-erasure mask from BM-17 has cost 3/14≈21.43%. These three different resources are all measured under the same conditional adversarial readout model; (10) prices keeping the original degree-four mask unchanged.

## 3. BM-19/T3: exact finite comparisons

The [fixture table](support_aware_fixtures_BM19.py) includes separate rational mask-distribution **primals** and matching all-mask Walsh-domain **duals** for five frozen partial policies. Their discrepancy supports are computed independently from the complete partially masked output laws, rather than inferred only from Fourier degree.

| Frozen partial policy | Nonzero remaining Fourier characters | Optimal r*(D) | BM-18 universal r* | Completed uniform cap |
|---|---:|---:|---:|---:|
| K4, degree 3 | 17 | **7/38** | 5/24 | 11/38 |
| K4, degree 4 | 3 | **1/10** | 1/6 | 13/50 |
| K4, degree 5 | 1 | 1/12 | 1/12 | 59/228 |
| Diamond, degree 3 | 6 | 1/5 | 1/5 | 3/10 |
| Theta, degree 4 | 7 | 1/6 | 1/6 | 1/4 |

The K4 degree-three residual support is

    D_3={15,23,27,29,30,39,43,46,47,51,53,54,57,58,60,61,63},

and the exact common-mask optimum is r=7/38. Its attaining rational mask uses denominator 76 and 22 nonzero mask atoms; an independent 12-character Fourier dual with coefficients over 38 and six nonpositive edge multipliers over 19 certifies the sharp lower bound. This improves the BM-18 optimal universal high-degree mask r=5/24 by

    5/24-7/38=11/456.

The K4 degree-five support is the full set {63}; the universal final-degree one-hot law is already optimal. The diamond and theta test cases also match their corresponding universal BM-18 completion costs, supplying **negative controls** against assuming that support-aware postprocessing always improves the bound.

The verified masks make the **complete output laws identical**, checked by direct convolution with the original integer vertex-label distributions. They do not imply that the partially masked system was already safe or that the additional noise is desirable for oversight. The mathematical optimization quantifies how cheaply an *adversarial* readout could conceal the remaining distinguishing signal.

## 4. BM-19/C1: exploiting sparse discrepancy support in larger graphs

The residual-support LP (4) has only |D|+1 equality rows, which may be small, but it has 2^m nonnegative mask-state variables. A potential solver uses **column generation**: a candidate dual needs its inequalities checked on mask atoms; the separation problem is

    max_(x in {0,1}^m)
       [y0+sum_(S in D) y_S chi_S(x)+sum_i z_i x_i]. (11)

For arbitrary support hypergraphs D, the expression is a weighted pseudo-Boolean parity optimization. Efficient separation may depend on the interaction width of the support hypergraph, as well as on the original graph's separator structure. Graph treewidth of G alone has not been shown to bound the hardness of this dual separation.

**Open BM-19/C1:** Freeze a class of graph/partial-monitor pairs for which the residual Fourier support D has a bounded-width factorization and the original partial-mask certificate is accessible. Determine whether a rational dual separating oracle for (11), a compatible attaining mask distribution and a certified additive approximation to the full erasure cost can be computed in `f(w,1/epsilon) poly(m,log q)` bit complexity, with w an explicit width measure on the residual hypergraph. BM-17's K4 and BM-19's fixed-pair masks serve as required finite counterchecks.

This is a narrower and more testable next algorithmic target than asserting that bounded *graph* treewidth alone compresses all adversarial masking decisions.

## 5. Code, proofs and novelty boundary

- [support_aware_completion_BM19.py](support_aware_completion_BM19.py) contains the exact support criterion, complete exponential-size rational LP matrix, matching primal/dual verifiers, common mask convolution, final marginal bounds and the single-character union-bound lower certificate.
- [support_aware_fixtures_BM19.py](support_aware_fixtures_BM19.py) freezes all five rational witnesses, including the 8-mask K4 degree-four proof and 22-mask K4 degree-three proof.
- [test_support_aware_completion_BM19.py](test_support_aware_completion_BM19.py) independently reconstructs residual support through complete-output convolution, verifies each rational LP primal and dual on all mask atoms, mutates witnesses to ensure rejection, compares exact solver matrices, and checks the completed full-output laws.
- Classical antecedents include Fourier analysis on the Boolean cube, linear-program duality, hypergraph covering bounds and Delsarte-type moment constraints. See [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/) and [linear-programming covering methods in coding theory](https://citeseerx.ist.psu.edu/document?doi=96606d6cc35a6d2e6d3382d25379c6a2b2ecd592&repid=rep1&type=pdf).

All proofs concern finite, fully declared statistical access assumptions. No live model attacks, independent hardware-root attestations, new UGC proof or empirical alignment guarantees are claimed.
