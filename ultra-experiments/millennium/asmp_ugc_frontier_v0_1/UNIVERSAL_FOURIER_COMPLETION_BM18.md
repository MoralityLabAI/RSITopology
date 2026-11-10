# BM-18: Universal Fourier completion and the optimal radial annihilator LP

**10 November 2026 | exact theorem and rational certificates.** This continues [BM-17's full-degree K4 obstruction](K4_FULL_DEGREE_OBSTRUCTION_BM17.md). The key distinction is between an **exact graph-specific erasure threshold** and a universal, auditable cost for completing a partially equalized set of Fourier observations. The new completion theorem applies to **every** finite graph and Boolean observation pair under the BM-17 mask model, including 2-connected graphs of arbitrarily high separator width.

The mathematics uses classical Boolean Fourier convolution, permutation averaging, binary Krawtchouk polynomials and finite LP duality. It does not prove an efficient algorithm to optimize graph-specific adversarial masks at low degree, or an empirical claim about AI-system oversight.

## 1. Frozen model and universal completion problem

Let m>=1 be the number of Boolean edge reports. Fix any graph and two clean pattern laws P0,P1 on {0,1}^m. The clean laws arise from independent fresh uniform vertex labelings in the ASMP gain-graph application, but the completion theorem itself needs only **fixed** finite Boolean laws.

For h in {0,1}, let Q_h be a potentially hypothesis-dependent, correlated XOR readout-mask distribution which is **independent of the current clean pattern**. Its per-edge flip marginal is at most eta. Write

    hatP_h(S) = E_{X~P_h}[(-1)^{sum_(i in S) X_i}],
    hatQ_h(S) = E_{M~Q_h}[(-1)^{sum_(i in S) M_i}].

For d in {0,...,m}, define eta_d to be the minimum mask cap under the **degree-d truncated erasure constraints**

    hatP0(S) hatQ0(S) = hatP1(S) hatQ1(S),
    all S subset [m] with |S|<=d.                     (1)

For d=m these are exactly complete output-law equality by Walsh inversion. The nested finite LPs satisfy 0<=eta_d<=eta_m<=1/2: independent fair readout bits achieve full erasure at cap 1/2. The exact BM-17 K4 profile eta_5=4/19<eta_6=3/14 shows that a final high-order constraint can matter.

## 2. BM-18/T1: universal Fourier completion theorem

**Theorem (universal quantitative completion):** for all m>=1 and 0<=d<=m,

    eta_m <= eta_d + r_(m,d)*(1-2eta_d),             (2)

where

    r_(m,d)=(m-d)/(2m).                              (3)

In particular

    0<=eta_m-eta_d <= (m-d)/(2m).                     (4)

**Constructive proof.** Let Q0,Q1 be degree-d feasible achieving mask laws at cap eta_d, which exist by compactness of finite probability simplices.

Independently draw a uniformly random subset H of the m edge positions with cardinality k=m-d. Conditional on H, flip every bit i in H with an independent fair coin and leave all bits outside H unchanged. Let R denote this common postprocessing XOR mask. It is **identical under both hypotheses**, independent of the current clean observation and of the original mask.

For any queried Fourier subset S, if S intersects H then E[chi_S(R)|H]=0. If S is disjoint from H, the same conditional expectation is one. Therefore

    hatR(S) = Pr(H intersects S trivially)
            = binomial(m-|S|,k)/binomial(m,k),       (5)

with the numerator interpreted as zero whenever k>m-|S|. Every S with |S|>d intersects every H of size m-d, so hatR(S)=0 at all remaining higher degrees. Meanwhile multiplying each degree-<=d output Fourier coefficient by the *same* number hatR(S) preserves every equality in (1).

Thus the two **complete** postprocessed output laws P0*Q0*R and P1*Q1*R agree exactly, including every high degree, by Walsh inversion. Each coordinate of R flips with probability

    r=Pr(i in H)*1/2=(m-d)/(2m).

If the original mask has per-edge marginal p_i<=eta_d, independence of R gives

    Pr((M_i XOR R_i)=1)
      =p_i+r-2p_i*r
      =r+(1-2r)p_i
      <=r+(1-2r)eta_d.                              (6)

Rewriting the right side as eta_d+r(1-2eta_d) proves (2). The postprocessor uses only a uniformly sampled subset and independent fair bits, so its **sampling description has polynomial size**, even though its explicit distribution over all 2^m masks can be large.

For additive target epsilon, taking a truncated degree d with (m-d)/(2m)<=epsilon certifies eta_m<=eta_d+epsilon. This requires d>=m(1-2epsilon), generally **near full degree**. Because the truncated graph-specific erasure LP can still have exponentially many mask variables, (2) alone does **not** constitute an FPT approximation scheme in separator width.

## 3. BM-18/T2: optimal universal high-order annihilator is an m+1-variable LP

The random-H construction is one legal **universal high-degree annihilator**. Define r*_m,d as the least achievable maximum per-bit flip probability of any hypothesis-blind mask R for which

    hatR(S)=0 for every S with |S|>d.                (7)

The definition is graph-independent and prevents any higher-degree distinction from surviving readout postprocessing.

**Symmetry theorem.** The family of requirements (7) is invariant under *every permutation* of the m coordinates. Given any feasible R, average its distribution over all m! coordinate permutations. The average still satisfies (7), and every resulting per-bit flip marginal equals the original average marginal, which cannot exceed the original maximum. Hence an optimal annihilator is exchangeable, determined by the probability weights

    w_t=Pr(|R|=t),    t=0,...,m.                       (8)

When |S|=s and R is uniform over masks with t flipped bits, its Walsh expectation is the normalized binary Krawtchouk value

    Phi_s(t) =
      [sum_j (-1)^j binomial(s,j)binomial(m-s,t-j)]
       / binomial(m,t).                               (9)

The exact universal optimum is therefore the rational linear program

    minimize    sum_(t=0)^m (t/m) w_t
    subject to  w_t>=0, sum_t w_t=1,
                sum_t Phi_s(t)w_t=0, s=d+1,...,m.      (10)

It has exactly **m+1 nonnegative primal variables** and **m-d+1 equality rows**. Its rational coefficients have polynomial bit length in m. Every feasible w is an explicit probabilistic mask law, sampling t with probability w_t and then a uniformly random t-subset of coordinates.

**Exact dual:** let y0 be the multiplier for normalization and y_s for each s>d. Any rational vector satisfying

    y0+sum_(s>d) y_s Phi_s(t) <= t/m,
                    for every t=0,...,m             (11)

proves r*_m,d >= y0. Matching feasible primal and dual values give an exact proof, with only **m+1 dual inequalities** to check. [The module](fourier_completion_BM18.py) constructs this general exact LP and verifies rational primal/dual witnesses with no solver dependency.

Because r*_m,d<=1/2 (uniform independent fair noise is always feasible), the preceding proof also gives the **stronger general completion inequality**

    eta_m <= eta_d + r*_m,d (1-2eta_d).              (12)

The exact r* can be determined by polynomial-size rational LP for any m,d, using an external solver if desired; only the small seeded optimum witnesses are bundled for immediate exact verification.

## 4. BM-18/T3: two closed-form sharp universal levels

**Last degree:** d=m-1 requires hatR([m])=0, meaning odd mask parity with probability 1/2. Since an odd mask flips at least one coordinate,

    E|R|>=Pr(|R| odd)=1/2
    and  r>=E|R|/m>=1/(2m).

The uniform construction that flips exactly one randomly chosen coordinate with probability 1/2 (and no coordinate otherwise) attains the lower bound:

    r*_m,m-1=1/(2m).                                (13)

A matching exact Krawtchouk dual has y0=1/(2m), y_m=-1/(2m).

**Last two degrees:** d=m-2 requires zero Walsh coefficients for the full set and for every complement-of-one-edge set. Let Z=(-1)^|R|. Then E Z=0, so Pr(odd parity)=1/2. The complement constraints E[Z(-1)^R_i]=0 imply E[Z R_i]=0 for each i. Summing over i gives

    E[|R| 1_even]=E[|R| 1_odd]>=1/2.

Thus E|R|>=1, and r>=1/m. Drawing a uniform random two-coordinate subset H and flipping its bits independently and fairly achieves E|R|=1 and zero on every degree-m and degree-(m-1) character. Hence, for m>=2,

    r*_m,m-2=1/m.                                  (14)

The exact dual certificate is

    y0=1/m, y_(m-1)=-1/2, y_m=(m-2)/(2m).

The [tests](test_fourier_completion_BM18.py) verify these symbolic formulas with exact Krawtchouk inequalities for m through 20, including both endpoint cases and m=1 where applicable.

**Sharpness in a registered gain graph.** For a q=4 isolated m-cycle, every proper edge subset is acyclic, so eta_(m-1)=0. BM-08 establishes eta_m=1/(2m). Formula (2) is therefore **exactly attained** for every such cycle: its universal final-degree completion gap cannot be lowered as a graph-independent theorem.

## 5. Sharper early-degree universal masks from exact Krawtchouk LP

The uniform random-H mask gives r=(m-d)/(2m). For degrees farther from m, this is sometimes suboptimal. Exact primal and dual certificates found by a numerical LP search and reconstructed as rationals give:

| m | d | Uniform random-H cap | Exact optimal universal r* |
|---:|---:|---:|---:|
| 5 | 2 | 3/10 | **1/4** |
| 6 | 3 | 1/4 | **5/24** |
| 7 | 4 | 3/14 | **1/6** |
| 8 | 4 | 1/4 | **5/26** |

For m=5,d=2 one attaining radial distribution on mask weight t is

    w_0=3/16, w_1=15/32, w_2=5/16, w_5=1/32,

with all other w_t=0. An exact dual has

    y0=1/4, y3=-1/2, y4=1/4, y5=0.

Checking all four equality rows and all six mask-weight dual inequalities proves r*_5,2=1/4. The other finite witness tables and rational duals are embedded in [fourier_completion_BM18.py](fourier_completion_BM18.py), and each is independently checked. These are small exact linear-program facts within a classical Krawtchouk association scheme.

## 6. Applying the completion to previous gain-graph certificates

The new tests take the *actual* BM-17/BM-13 truncated mask witnesses, convolve them with the independent universal mask, and verify **every final Boolean output probability** via full exact integer/rational convolution:

- **K4, d=5:** eta_5=4/19, m=6, r*=1/12. The universal bound gives eta_6<=59/228≈0.25877. The genuine BM-17 optimum is **3/14≈0.21429**, demonstrating that the universal postprocessor is conservative for a particular graph.
- **K4, d=3:** eta_3=1/6, m=6. The sharper universal mask r*=5/24 gives completion bound **11/36**, improving the simple hitting-mask bound of 1/3. The exact graph-specific optimum is still 3/14.
- **Diamond, d=3:** eta_3=1/6, m=5. The uniform fair-noise mask with r=1/5 gives eta_m<=3/10, compared with the exact diamond optimum 1/5.
- **Theta, d=4:** eta_4=1/8, m=6. A postprocessing marginal r=1/6 gives eta_m<=1/4, compared with the exact theta optimum 1/6.
- **Isolated q=4 cycles:** for m=2..6 and d=m-1, zero initial mask plus the universal one-coordinate postprocessor reaches the exact eta_m=1/(2m). This is the sharp control.

All checks remain valid when the **initial** degree-d masks Q0 and Q1 are hypothesis-dependent and internally correlated, because the **added** postprocessor R is common and independent. The completion theorem relies on postprocessing independence; an additional state-aware mask chosen after examining the current clean report requires a new access model.

## 7. Consequences for the ASMP-14 structural complexity conjecture

BM-17 established that Fourier degree m can matter even on the six-edge K4. BM-18 supplies a universal **quantitative** bound on the cost of omitting high degrees. It also isolates a tractable auxiliary LP: computing the cheapest graph-independent mask that annihilates all Fourier terms above a cutoff requires only m+1 radial weights and a small exact dual.

A candidate graph-specific extension is a **support-aware completion program**. For a frozen pair of partially equalized output laws, identify the set of remaining nonzero Fourier discrepancies and optimize a common postprocessor annihilating just those supports, subject to per-edge marginal costs. Such a program can exploit the graph's weighted Fourier structure, unlike the universal mask. A convincing ASMP-14 approximation theorem would further need an algorithm to construct those restricted supports/dual witnesses with resource bounds depending on separator width and alphabet encoding.

The universal additive bound does not alone resolve this: for small epsilon, d must be close to m, and graph-specific truncated erasure LPs can still be exponential in m even if BM-16 computes each clean coefficient efficiently at low width. These distinctions and the previously registered audit/restore contracts remain central to the broader safety motivation.

### Reproducibility and prior art

- [fourier_completion_BM18.py](fourier_completion_BM18.py): universal hitting-noise generator, normalized Krawtchouk ratio, exact radial LP matrix, rational primal/dual verification, sharp near-top formulas and finite improved fixtures, XOR postprocessing of prior graph masks, and symbolic completion bounds.
- [test_fourier_completion_BM18.py](test_fourier_completion_BM18.py): direct mask-orbit character tests, closed-form duals through m=20, independent exact finite LP fixtures, postprocessing of the actual K4/diamond/theta witnesses, isolated-cycle equality control and malformed-contract checks.
- Mathematical antecedents: Fourier analysis of Boolean functions, Delsarte/Hamming-scheme linear programming and Krawtchouk duality. See [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/), and [*Unique optima of the Delsarte linear program*](https://link.springer.com/article/10.1007/s10623-023-01191-y) for the classical coding-theory setting. The BM-18 LP is an application of these methods to a separately defined universal noise-completion optimization.

All executable work uses exact rational Python-standard-library arithmetic and the focused CPU-only GitHub Actions workflow. The result is a finite mathematical monitoring bound; no live model behavior or external trusted state attestation is claimed.
