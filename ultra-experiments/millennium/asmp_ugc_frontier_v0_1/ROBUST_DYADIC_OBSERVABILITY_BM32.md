# BM-32: Quantitative observable control of the signed dyadic equation

**10 November 2026 | finite-observation robustness and exact polynomial-moment rate.** This builds directly on [BM-29's signed dyadic overlap theorem](INFINITE_REPLICATION_LIMIT_BM29.md), [BM-30's limiting channel rigidity](OPTIMAL_CHANNEL_RIGIDITY_BM30.md) and [BM-31's finite-exchangeability extension](FINITE_EXCHANGEABILITY_RATE_BM31.md).

**The research target** is an explicit scalar rate for `5/52−eta_n(8,2)`, where eta_n is the exact fully hypothesis-aware erasure threshold with n ordinary two-edge paths and one exceptional two-edge path over q=8. BM-32 proves a narrower but quantitative result: every feasible finite-n equalizer induces a genuinely infinite exchangeable **empirical replacement** channel whose BM-29 signed parity-measure equation is *approximately satisfied* at a precisely controlled finite-window rate. For **all bounded Lipschitz tests**, the defect is O(n^(-1/3)); for **every fixed-degree polynomial monomial**, it is O(1/n).

These are exact inequalities with explicit rational bound certificates. They do **not** by themselves establish a scalar convergence rate for eta_n. The missing step is a quantitative stability theorem for the signed dyadic-overlap inequality under these approximate moment equations.

## 1. Frozen model and BM-31's empirical replacement extension

Let q=8, K=F2³ and take n ordinary two-edge u–v paths whose gain is zero under both hypotheses plus one exceptional path whose gain differs across hypotheses. A new uniform vertex labeling is drawn every observation episode; the complete 2n+2 Boolean edge-satisfaction vector is observed.

The adversary chooses hypothesis-dependent XOR readout masks Q0,Q1 with arbitrary within-episode correlation, independent of the **current** clean observation, and individual mask-flip marginals at most eta. Assume the two complete masked output laws are identical.

BM-29's exact Fourier marginal-rigidity lemma forces the ordinary mask laws to agree between the two hypotheses, as well as their joint laws with either *individual* exceptional mask bit. Average over path swaps and within-path edge swaps. The mask is represented by the finite empirical ordinary type histogram c=(c0,c1,c2), sum c=n, and distinguished exceptional pair mask z in {00,10,01,11}.

BM-31 constructs an **infinite exchangeable extension** by drawing (c,z) from its actual finite joint law and then drawing infinite ordinary mask pairs i.i.d. from the empirical physical pair law

    M_c=(c0/n,c1/(2n),c1/(2n),c2/n).             (1)

The mask coordinates of this directing law are

    u=(c0−c2)/n,     w=(c0−c1+c2)/n.               (2)

The extension retains both worlds' common ordinary directing distribution, the world-specific exceptional-pair conditional law and the individual exceptional-bit compatibility constraints. It preserves **every per-edge mask-error marginal**.

For 1<=k<=n, write \widetilde P_(h,k) for its observed joint law on the first k ordinary two-bit paths and the exceptional observed pair under world h. Let

    eps_(n,k) =
      dTV(\widetilde P_(0,k),\widetilde P_(1,k)).

The original finite output laws are equal exactly. BM-31's without/with-replacement coupling and three-color entropy refinement yield

    eps_(n,k) <= 2e_(n,k),                         (3)

with

    e_(n,k)^2 <=
      v_(n,k)=k(k−1)/[2(n−1)(n−k+1)]             (4)

for n>=2. Here dTV is the standard total variation distance. BM-31's exact sampler also gives e<=1-(n)_k/n^k, including n=1.

## 2. The signed dyadic defect and a measurable output statistic

As in BM-29, let mu be the shared directing distribution of the two-bit ordinary noise pair M, and let nu_h be the signed measures on the directing parameter space induced by the **parity** of the distinguished exceptional noise pair in world h. Define the dyadic map

    S(u,w)=(u,w/2),

and the signed measure

    D=(2I+7S_*)nu_0 − (I+8S_*)nu_1.               (5)

For an *exact* infinite-replica equalizer, BM-29 proved D=0. BM-31's approximate infinite replacement channels generally have D≠0, because sampling *with* replacement changes the finite ordinary-mask correlations.

For any test function f on [-1,1]², its signed defect is

    D[f]=int f dD
      =int [2f(u,w)+7f(u,w/2)] dnu_0
        −int [f(u,w)+8f(u,w/2)] dnu_1.            (6)

The coefficients 2,7,1,8 come from the exact clean terminal-match weights and exceptional pair-parity coefficients. In particular, the observable exceptional output **pair parity** is the signed bit which carries D.

Consider one reported ordinary path pair Y_i=(Y_(i,1),Y_(i,2)), writing each reported Boolean bit in Walsh form

    X_i=(-1)^Y_(i,1),      Z_i=(-1)^Y_(i,2).

Conditional on M=(u,w) and on the clean terminal regime, different ordinary output pairs are i.i.d., and

    E[X_i]=E[Z_i]=(3/4)u,
    E[X_i Z_i]=v,     v=w or w/2.                 (7)

Define the empirical estimators

    Uhat=clip_[−1,1]{ (2/(3k))sum_i(X_i+Z_i) },
    What=(1/k)sum_i X_i Z_i.                       (8)

They are estimators of u and v. The un-clipped first estimator is unbiased; clipping is 1-Lipschitz and leaves the true latent u unchanged. Each single-path term (2/3)(X_i+Z_i) has magnitude at most 4/3, while each X_i Z_i has magnitude one. Conditional independence and Cauchy–Schwarz therefore imply

    E|Uhat−u| <= 4/(3 sqrt(k)),
    E|What−v| <= 1/sqrt(k),

and hence

    E[|Uhat−u|+|What−v|] <=7/(3 sqrt(k)).         (9)

Take any real f with sup|f|<=B and Lipschitz constant L in the l1 distance on [-1,1]². The observable

    G_f = (-1)^(special_output_pair_parity)
                              * f(Uhat,What)      (10)

is bounded by B. Conditional on latent M, clean terminal regime and exceptional noise, equations (7)-(9) show that its mean differs from the ideal special-parity-weighted value f(u,v) by at most 7L/(3 sqrt(k)) under each hypothesis.

The two worlds' expectations of G_f differ by at most 2B eps_(n,k), because their **reported output laws** have TV distance eps_(n,k). BM-29's exact clean parity weights give

    E_0[ideal G_f] − E_1[ideal G_f] = D[f]/16.

Combining all estimates yields:

> **BM-32/T1 (robust finite-observation dyadic identity):**
>
> For every bounded L-Lipschitz f on [-1,1]² and every pair of infinite exchangeable q8 mask processes whose k-path-plus-exceptional output TV distance is at most epsilon,
>
> **|D[f]| <= 32 B epsilon + (224 L)/(3 sqrt(k)).** (11)
>
> This applies to any valid world-specific exceptional noise coupling and ordinary directing law, including BM-31's finite-n empirical replacement construction.

The proof is entirely finite expectation accounting once the directing representation is given. In particular, (11) is a **bounded-Lipschitz-norm quantitative residual inequality**, with an explicit universal coefficient.

### Specializing to a genuine finite-n eraser

Substitute epsilon<=2e and (4):

    |D[f]| <=64 B sqrt(v_(n,k))
                         +224 L/(3 sqrt(k)).       (12)

The expression on the right involves square roots, so the **exact rational verifier** uses the conservative inequality (a+b)²<=2a²+2b²:

    |D[f]|² <=
        2*[4096 B² v_(n,k)+(224L/3)²/k].         (13)

The bound (13) is a rational number. The code can check a claimed signed defect against it in integer/Fraction arithmetic without approximating any square root. The full inequality (11) is also checked exactly by isolating the deterministic TV term and squaring only the nonnegative remaining sampling term.

Choose k=floor(n^(2/3)). Then v_(n,k)=O(n^(-2/3)) and 1/k=O(n^(-2/3)), so (13) establishes

    **sup_{sup|f|<=B,Lip(f)<=L} |D[f]|
          =O_(B,L)(n^(-1/3)).**                  (14)

The convergence rate applies to the signed dyadic *equation* of the empirical extension. It is independent of the optimizers' complicated correlation and depends only on the frozen observation/noise model. The constants are conservative; at n=10^12 the simple B=L=1 square bound certifies a defect below approximately 0.01235.

## 3. BM-32/T2: unbiased polynomial probes and an O(1/n) moment rate

Bounded Lipschitz estimation loses an O(k^(-1/2)) term. For a polynomial monomial `f(u,w)=u^a w^b`, we can construct an **unbiased** product statistic using distinct ordinary reported paths. Fix a,b>=0 and let d=a+b<=k.

On the first a ordinary paths retain the first reported-bit Walsh characters X_i. On the next b ordinary paths retain their **pair-parity** characters X_i Z_i. Multiply the product by (4/3)^a, canceling the clean one-bit Fourier factor. Finally multiply by the exceptional reported pair parity:

    G_(a,b) = (4/3)^a
       (-1)^(special output pair parity)
       prod_(i=1)^a X_i
       prod_(j=a+1)^(a+b) X_j Z_j.                 (15)

Because all these reported ordinary paths are conditionally independent given the directing pair noise M and clean terminal regime,

    E[G_(a,b) | M, regime, exceptional noise]
       = exceptional_clean_parity
           * exceptional_noise_parity
           * u^a v^b,                             (16)

where v=w or w/2 according to the regime. The identity (16) holds **exactly**, without a sampling approximation.

Consequently, for the infinite empirical replacement extensions,

    **D[u^a w^b]
       =16*(E_0 G_(a,b) − E_1 G_(a,b)).**          (17)

Since |G_(a,b)|=(4/3)^a, an output TV bound epsilon yields

    |D[u^a w^b]| <=32*(4/3)^a epsilon.             (18)

Now take a genuine finite-n exact equalizer and its BM-31 replacement extension. With k=max(1,d), BM-31 gives epsilon<=2 e_(n,k), and the collision coupling (7) yields

    **|D[u^a w^b]|
       <=64*(4/3)^a*(1-(n)_k/n^k)
       <=32*(4/3)^a*d(d−1)/n,**                   (19)

for every d>=1, d<=n. For d=0 the right side is defined as zero; its special-pair parity equality is already enforced by the original exact full-output condition and the k=1 projection.

Thus for any **fixed total degree d**, every corresponding dyadic moment defect is O(d²(4/3)^a/n), an **explicit inverse-n rate**. This substantially improves the O(n^(-1/3)) bounded-Lipschitz rate on the polynomial test subspace.

Equation (19) is checked by two independent constructions: direct exact signed measures on the finite empirical histogram and the expected product of output Walsh characters after sampling the empirical pair law **with replacement**. For all seeded BM-25 through BM-30 exact mask witnesses, the code verifies the identity (17), the measured output-TV bound and the uniform symbolic d/n rate.

For illustration, for f(u,w)=uw (a=b=1) and n=10^9, (19) gives an absolute signed-measure defect at most

    256/(3*10^9) ≈ 8.5333e-8,

without any enumeration of n ordinary masks. This is a moment estimate; it is **not** a bound on `eta_infinity−eta_n`.

## 4. Why this is still short of a scalar finite-n threshold rate

BM-29's exact limiting lower bound is derived from **signed measure overlap**, involving the minimum of two Radon–Nikodym densities. BM-30 sharpened the equality case and established a stability inequality assuming the signed dyadic equation is exactly zero.

BM-32 now controls the **defect** in that equation, quantitatively:
- in bounded-Lipschitz norm at O(n^(-1/3));
- in every fixed-degree polynomial moment at O(1/n).

To prove an explicit scalar lower bound

    eta_n(8,2) >= 5/52 - R(n),

we still need a **robust signed-overlap theorem** that turns one of these approximate dyadic identities into a near-sharp inequality

    8 C_ordinary +5 C_exceptional
        >=5/4 - delta_n.                           (20)

The error delta_n must be quantified in terms of the observable moment errors and an explicit approximation to the relevant signed-measure dual witness, with its Lipschitz constant or polynomial coefficient norm charged honestly. A bounded test family without such a robustness modulus does **not** bound total variation of arbitrary signed measures or their lattice minimum. In particular, arbitrarily close latent parity parameters can produce sharply different signed overlap.

A potential next experiment is to construct a finite-degree **polynomial approximation of the BM-29 dyadic dual certificate** and quantify both its uniform approximation error and its monomial coefficient l1 norm. The O(1/n) moment bound (19) would then give a rigorous threshold rate once those approximation constants are available. Independently, finite-dimensional rational LP duals such as the BM-28 n=16 certificate remain exact lower controls.

## 5. Code, independent controls and claim boundaries

- [robust_dyadic_observables_BM32.py](robust_dyadic_observables_BM32.py) implements exact finite empirical directing-measure defects, report-bit parameter estimators, bounded-Lipschitz TV/sampling bounds, rational square certificates, unbiased polynomial/Walsh probes and symbolic O(d²/n) monomial rates.
- [test_robust_dyadic_observables_BM32.py](test_robust_dyadic_observables_BM32.py) tests conditional q8 pair Fourier means, independent expansion of signed dyadic coefficients, real BM-25/BM-26 world-aware attaining masks, BM-27 all-n masks and BM-30 equality family masks, exact output TV and moment bounds, estimator unbiasedness, finite test-domain controls, and billion-path symbolic upper bounds.
- [BM-31 finite exchangeability](FINITE_EXCHANGEABILITY_RATE_BM31.md), [BM-29 dyadic proof](INFINITE_REPLICATION_LIMIT_BM29.md) and [BM-30 rigidity proof](OPTIMAL_CHANNEL_RIGIDITY_BM30.md) supply the surrounding hypotheses.

The key background mathematics is the finite de Finetti/Diaconis–Freedman coupling, conditional variance, Pinsker's inequality and classical Walsh Fourier characters. BM-32 applies these to a specific adversarial monitoring channel. It provides **statistical signed-measure robustness**, with no machine formalization of the underlying infinite de Finetti theorem and no quantitative full model-control or trusted-restoration safety guarantee. Publication novelty and measure-theoretic details merit independent review.
