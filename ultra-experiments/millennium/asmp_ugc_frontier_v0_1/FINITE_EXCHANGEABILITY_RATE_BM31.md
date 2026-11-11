# BM-31: Quantitative finite exchangeability with a distinguished exceptional mask

> **Subsequent result, BM-33 (10 November 2026):** The [explicit Lipschitz signed-overlap dual](FINITE_ERASURE_RATE_BM33.md) now proves the finite scalar rate \(0\le5/52-\eta_n(8,2)\le O(n^{-1/3})\), including an explicit nonasymptotic inequality for every \(n\ge2\). Statements below calling the *existence* of a finite-n rate open describe the historical status before BM-33. Its numerical sharpness, finite-n exact optima for n>=4, and higher-alphabet extensions remain open.


**10 November 2026 | exact finite-window approximation theorem and independently checked rational controls.**

This advances the next proof obligation after [BM-29's exact q8 replication limit](INFINITE_REPLICATION_LIMIT_BM29.md) and [BM-30's uniqueness/stability theorem](OPTIMAL_CHANNEL_RIGIDITY_BM30.md). The new result supplies an explicit **finite-n quantitative exchangeability extension**, preserving the exceptional-pair coupling and the legally capped individual mask errors. It also produces a rigorous approximate-output equality bound when applied to ANY exact finite erasing pair.

The result is an application of the classical finite de Finetti sampling argument of Diaconis and Freedman, with an additional KL/chi-square/Pinsker rate derived for the *three-category ordinary mask-type alphabet*. Its special feature for the BM-24–30 program is that **the two worlds' ordinary directing laws and either individual exceptional-bit conditional marginals remain identical** under the extension.

It quantifies the approximation step of the infinite BM-29 proof. Deriving a **numerical rate for the scalar erasure thresholds eta_n approaching 5/52** remains a separate, unproved robust-duality problem.

## 1. Frozen channel and empirical directing law

Fix q=8 and n ordinary two-edge u–v paths of path gain zero under both hypotheses, plus one exceptional two-edge path whose gain changes from zero to a nonzero value. Fresh uniform vertex labels create a complete Boolean edge-satisfaction vector. Under hidden hypothesis h=0,1 the adversary chooses a correlated XOR mask Q_(h,n), independent of the **current** clean observation, with maximum flip marginal at most eta.

The complete readout laws under the two worlds are assumed exactly equal. As in BM-24, average Q_(h,n) under:
- permutation of the n ordinary paths;
- independent exchange of the two edge bits within every ordinary path;
- exchange of the two exceptional edge bits.

Each clean law is invariant under these permutations, so averaging preserves complete-output equality, the current-clean independence premise and the maximum per-bit flip cap. The resulting ordinary pair-mask value is one of 00,10,01,11. After within-pair swaps, its **type** is t=0,1,2 flipped bits, with one-flip orientations 10/01 each having probability 1/2.

Let

    C=(C0,C1,C2),        C0+C1+C2=n,

be the full empirical count histogram of ordinary pair-mask types. Let Z_h in {00,10,01,11} denote the complete exceptional noise pair. A symmetrized mask law is encoded **exactly** by the rational joint distribution

    pi_h(c,z)=Pr(C=c,Z_h=z).                          (1)

Conditioned on C=c and Z_h=z, the n ordinary mask-pair types appear in uniformly random order, sampled **without replacement** from the multiset with c_t copies of type t. One-flip orientations are independent fair bits.

The ordinary empirical directing law for this finite n is

    mu_(h,n)(c) = sum_z pi_h(c,z).                   (2)

### BM-31/L1: shared empirical directing law and special single-bit marginals

BM-29's finite Fourier-positivity argument gives, for any complete-output equalizing pair,

    (Q0)_ordinary=(Q1)_ordinary,
    (Q0)_(ordinary + special_j)
       =(Q1)_(ordinary + special_j),  j=1,2.       (3)

Indeed, the common clean Walsh coefficient on any selected ordinary reports, and on that set plus either individual exceptional bit, is

    (3/4)^(b+j) [1+7*2^(-r)]/8 >0,                  (4)

where b counts singly selected ordinary paths, r fully selected ordinary paths, and j is 0 or 1. Since the complete *output* Walsh coefficients agree and XOR convolution multiplies clean and mask Fourier characters, the corresponding **mask** Walsh coefficients agree. Full Walsh inversion on those marginal bits proves (3).

Taking the empirical histogram C, which is a function of the complete ordinary mask, in (3) gives

    mu_(0,n)=mu_(1,n)=:mu_n,                         (5)

and identical `pi_h(c,z)` marginals after retaining **either** one exceptional noise bit. The full exceptional pair conditional law may differ between hypotheses; its parity is the channel freedom analyzed in BM-29.

These are exact finite-n identities. The tests reconstruct them independently from the actual BM-25 and BM-26 sharp world-dependent mask laws and from BM-27/BM-30 attaining mixtures.

## 2. BM-31/T1: an explicit infinitely exchangeable replacement extension

For any n and each histogram c define the **physical empirical ordinary pair distribution**

    lambda_c = (c0/n,c1/(2n),c1/(2n),c2/n),         (6)

in pair-value order (00,10,01,11). Because c0+c1+c2=n, it is a legal nonnegative normalized pair probability law.

Build an infinite extension for each world h by:

1. Draw (C,Z_h) according to the exact original joint histogram law pi_h.
2. Conditional on (C,Z_h), draw an infinite sequence of ordinary two-bit mask pairs **i.i.d.** from lambda_C.
3. Keep the previously drawn exceptional mask pair Z_h unchanged.

This defines a genuine infinitely exchangeable ordinary pair-mask sequence with a distinguished exceptional pair, and it has a **common** directing histogram law mu_n under both hidden worlds by (5). Because the exceptional single-bit marginals conditional on C are shared, the resulting two infinite extensions also preserve the *special single-bit* rigidity assumption of BM-29.

A single ordinary pair has the same marginal under the original without-replacement sample and the replacement extension; the exceptional pair has exactly its original marginal in each world. Therefore **every individual bit-flip probability and hence every original adversarial mask cap eta are preserved exactly**.

This construction uses one finite empirical histogram and a conditional exceptional-pair law. It is a certificate-preserving probabilistic extension, with an O(n) description when the original histogram law is available compactly, although an arbitrary input pi_h may itself contain exponentially many histogram atoms if its representation is unrestricted.

### TV distance on a finite window

For 1<=k<=n, let Q_(h,n)^[k] denote the original, symmetrized joint law on the **first k ordinary mask pairs and the entire exceptional pair**. Let \widetilde Q_(h,n)^[k] be the corresponding window under the infinitely exchangeable extension above.

Conditioned on C=c and Z_h=z, generate k uniformly random ordinary indices **with replacement** from {1,...,n}. If the chosen indices are all distinct, their sequence has exactly the **without-replacement** distribution of k ordered indices. Couple one-flip orientations and the fixed exceptional pair identically. Thus the two resulting masks disagree only when a repeated index is drawn in the replacement experiment.

The exact collision probability is

    eps_(n,k)=1-(n)_k/n^k,
    (n)_k=n(n-1)...(n-k+1),                        (7)

so a coupling inequality and a union bound give

    **d_TV(Q_(h,n)^[k], Qtilde_(h,n)^[k])
           <= eps_(n,k) <= k(k-1)/(2n).**           (8)

The bound is **uniform in h, c, the exceptional-pair coupling, and the choice of the original finite eraser**. It is exact zero for k=1. The first inequality can be sharp: for n=2, ordinary masks with one 00 pair and one 11 pair randomly ordered have total-variation error exactly 1/2 at k=2, equal to eps_(2,2).

## 3. BM-31/T2: sharper O(k/n) finite-alphabet entropy bound

Our ordinary pair type takes only **three** values t in {0,1,2}. This allows a stronger bound than the collision coupling when k grows.

Condition on any fixed empirical histogram c. Let p_i=c_i/n for each color i with p_i>0, and let N_i(t) count that type among the first t **without-replacement** draws. Given the previous draws, the probability of the next type i is

    q_i^(t)=(n*p_i-N_i(t))/(n-t).                    (9)

Compare the ordered without-replacement type law P^wo with the **independent** empirical type law P^iid. The chain rule for relative entropy yields

    D(P^wo || P^iid)
      = sum_(t=0)^(k-1) E[ D(q^(t)||p) ].            (10)

Apply log x<=x-1, which implies `D(q||p)<=chi²(q||p)=sum_i(q_i-p_i)^2/p_i`. The hypergeometric variance identity is

    Var[N_i(t)]
      =t*p_i*(1-p_i)*(n-t)/(n-1).                   (11)

Hence, with a<=3 nonempty types,

    E[chi²(q^(t)||p)]
      = t*(a-1)/[(n-1)(n-t)]
      <= 2t/[(n-1)(n-t)].                          (12)

Combining (10)/(12), and applying Pinsker's inequality for standard total variation `d_TV=sup_A|P(A)-Q(A)|`,

    d_TV(P^wo,P^iid)^2 <= (1/2)D(P^wo||P^iid)
       <= 1/(n-1) sum_(t=0)^(k-1) t/(n-t).         (13)

Bound each denominator by n-k+1 and sum the arithmetic series:

    **d_TV(P^wo,P^iid)^2
       <= k(k-1)/[2(n-1)(n-k+1)].**                (14)

The output bit-pair orientation randomizers, addition of exceptional Z_h and mixing over c are common stochastic kernels, so relative entropy and total variation cannot increase under those transformations. Thus (14) holds for the **complete joint k-ordinary-plus-exceptional mask windows** and for both hypotheses:

    **d_TV(Q_(h,n)^[k],Qtilde_(h,n)^[k])^2
       <= k(k-1)/[2(n-1)(n-k+1)],**    n>=2.     (15)

The code supplies this simple closed **rational squared-TV certificate** and the sharper pre-inequality rational sum in (13), with no numerical square-root precision issues. It verifies both bounds against exact rational distributions for BM-25, BM-26, BM-27 and BM-30 witnesses.

For fixed k and n→∞, (15) gives O(k/n) total-variation approximation. More importantly, for **k=o(n)** it goes to zero: the finite population can be approximated on a window that grows almost linearly with n.

### Explicit symbolic scaling

Take k=floor(n^(2/3)). Equation (15) gives

    d_TV = O(n^(-1/3)).

For example, the registered formula gives the following **rigorous approximate mask-TV upper values**:

| n ordinary paths | k retained ordinary paths | Upper bound from (15) |
|---:|---:|---:|
| 250 | 10 | 0.027385 |
| 1,000,000 | 10,000 | 0.007107 |
| 1,000,000,000 | 1,000,000 | 0.000708 |

The large instances use **only** exact rational size formulas and do not materialize a complete readout mask table.

## 4. BM-31/T3: controlled approximate equality of the output laws

Let P_(0,k) and P_(1,k) be the original clean Boolean observation laws on k ordinary paths plus the distinguished exceptional path. Projecting the n-path **exact** masked output equality gives

    P_(0,k)*Q_(0,n)^[k]
        =P_(1,k)*Q_(1,n)^[k].                        (16)

For each world, applying the same clean convolution kernel to the true and empirical replacement mask windows cannot increase their total-variation distance. The triangle inequality with (16) therefore gives the **explicit approximate infinite-extension output bound**

    d_TV(
      P_(0,k)*Qtilde_(0,n)^[k],
      P_(1,k)*Qtilde_(1,n)^[k]
    )
        <= 2 eps_(n,k),                             (17)

as well as the entropy-improved bound

    **d_TV(output0_tilde, output1_tilde)^2
        <= 4*k(k-1)/[2(n-1)(n-k+1)].**             (18)

For any Walsh character S of those 2k+2 observed bits, its value is between -1 and 1. The difference in its expectations between the two replacement outputs is at most twice their total-variation distance. Thus

    |Delta_tilde(S)| <= 4 eps_(n,k),                 (19)

and its square is at most **16 times** the rational mask squared-TV bound in (15). Equations (17)-(19) hold for *any* exact finite equalizer, including correlated world-dependent masks.

The [executable verifier](finite_empirical_extension_BM31.py) computes both finite hypergeometric and iid empirical mask windows independently. For small q8 n, it reconstructs the full symmetrized original masks, checks genuine complete erasure through direct Boolean XOR convolution, confirms finite marginal rigidity, verifies TV distances exactly, and tests the new approximate-output and Fourier inequalities.

## 5. What remains between BM-31 and a finite-n threshold rate

BM-29's `eta_n(8,2)` increases monotonically to 5/52. BM-30 establishes a unique limiting symmetrized eraser and qualitative convergence of fixed-coordinate mask projections. BM-31 now supplies an **explicit finite exchangeability approximation** from any optimal n-path mask to an infinite i.i.d. directing mixture, including the distinguished exceptional pair, whose first `k=o(n)` paths have **approximately equal** output laws at the controlled rate in (18).

The missing bridge is a **robust version of BM-29's signed dyadic-overlap inequality** applying when the infinite-mixture output laws agree only approximately on a finite observation window. BM-29's exact proof identifies the directing parameters by an infinite empirical law and uses exact equality of signed measures. BM-31 controls a finite sample of those measures; upgrading it to a scalar `5/52 - eta_n <= f(n)` requires additional quantitative moment-inversion or approximate-dual arguments. No such scalar rate is claimed here.

The open BM-31/C1 target is therefore specific:

> Find explicit, computable constants and a function `R(k,epsilon)` such that any pair of *infinite exchangeable*, legal q8 masks whose first k ordinary-plus-exceptional output laws have total variation at most epsilon obeys
>
> `8 C_o+5 C_s >=5/4 - R(k,epsilon)`,
>
> with `R(k,epsilon)→0` as k→∞ and epsilon→0. Combined with (18), this would yield a rigorous finite-n convergence rate for eta_n→5/52.

The entropy estimate is a finite-sample consequence of classical Diaconis–Freedman exchangeability, hypergeometric covariance, and KL/Pinsker inequalities. Relevant background includes [Diaconis and Freedman, *Finite Exchangeable Sequences* (1980)](https://doi.org/10.1214/aop/1176994663) and [Bobkov, *De Finetti's Theorem and Related Results for Infinite-Dimensional Convex Sets*](https://www-users.cse.umn.edu/~bobko001/papers/2005_JTP_De.Finetti.pdf) for sample-with/without-replacement comparisons. The q8 exceptional-coupling calculation is specialized to our observation experiment and needs independent prior-art review before a novelty claim.

## 6. Code and independent controls

- [finite_empirical_extension_BM31.py](finite_empirical_extension_BM31.py): symmetrized empirical mask histograms with exceptional pair, exact finite and iid projection DPs, preserved ordinary and single-special-bit marginals, exact collision bounds, rational KL/Pinsker bounds, output/Fourier discrepancy checks and billion-path symbolic scaling receipts.
- [test_finite_empirical_extension_BM31.py](test_finite_empirical_extension_BM31.py): independent exact complete BM-25/BM-26/BM-27/BM-30 mask witnesses, direct bitwise projection versus hypergeometric DP, held-out exceptional-bit rigidity, sharp n=2 collision adversary, exact output-TV checks, finite-alphabet entropy and KL controls, projective consistency and growing-window numerical-size guards.
- All checks are deterministic and use only the Python standard library. They make no assertion of a solved n>=4 optimum, a deployed agent monitoring guarantee, independently attested restoration, or a new Unique Games theorem.
