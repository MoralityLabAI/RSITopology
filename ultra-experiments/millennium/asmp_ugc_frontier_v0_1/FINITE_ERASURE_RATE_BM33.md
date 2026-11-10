# BM-33: A finite-replica convergence rate from an explicit Lipschitz overlap dual

**10 November 2026 | exact scalar finite-n theorem, constructive dual, rational regression controls.**

This closes the precise rate gap left by [BM-29's q8 limiting masking theorem](INFINITE_REPLICATION_LIMIT_BM29.md), [BM-30's uniqueness/stability theorem](OPTIMAL_CHANNEL_RIGIDITY_BM30.md), [BM-31's finite empirical exchangeability](FINITE_EXCHANGEABILITY_RATE_BM31.md), and [BM-32's quantitative signed-measure observables](ROBUST_DYADIC_OBSERVABILITY_BM32.md). The advance is an explicit **continuous piecewise-bilinear test function** whose pointwise signed-measure inequalities are already sharp at BM-27's unique limiting eraser. It converts BM-32's bounded-Lipschitz dyadic residual estimate into a numerical lower bound on the actual finite-n erasure cost.

All statements are in the original frozen model: q=8=|F₂³|, n ordinary length-two paths with gains 0/0, one exceptional length-two path with gains 0/nonzero, fresh uniform vertex labels, complete Boolean edge-satisfaction reports, and **hypothesis-dependent within-episode correlated XOR masks independent of the current clean observation**. The adversary knows the hidden hypothesis and obeys a common maximum per-bit flip cap. The theorem applies to the full class of such masks.

## 1. Main scalar convergence theorem

Let eta_n be the exact smallest per-bit masking allowance that equalizes the two complete output laws for n ordinary paths. BM-29 proved lim_n eta_n=5/52, while BM-27 gave eta_n<=5/52 for all n.

> **BM-33/T1 (explicit, nonasymptotic scalar convergence).** For every integer n>=2 and 1<=k<=n,
>
> \
> **0 <= 5/52 - eta_n
>    <= (200/39)*sqrt[k(k-1)/(2(n-1)(n-k+1))]
>        + (3584/117)/sqrt(k).**                         (1)
>
> Choosing k=floor(n^(2/3)) proves
>
> **5/52 - eta_n = O(n^(-1/3)).**                         (2)
>
> A simple explicit corollary, valid for every n>=8, is
>
> **0 <= 5/52 - eta_n <= 51 n^(-1/3).**                  (3)

The constants are explicit and the proof has no numerical LP discovery assumption. The rate is conservative at finite sizes, where independently certified BM-25/BM-26/BM-28 exact thresholds and lower bounds are substantially stronger; its significance is that it proves an **algebraic convergence rate** for all n rather than relying on numerical extrapolation or qualitative compactness.

The mathematical proof consists of the following explicit pointwise dual, a robust signed-overlap inequality, and the already registered BM-31/BM-32 finite observation estimates. **The scalar finite-n theorem can be derived entirely from finite probability distributions**: BM-31's empirical replacement directing law has at most binomial(n+2,2) ordinary histogram atoms, and its first k conditionally i.i.d. samples are an explicit finite mixture. No abstract infinite de Finetti limit is required to prove (1), even though BM-29 originally established the limiting value through exchangeability.

## 2. A pointwise dual to the signed dyadic overlap

BM-29's infinite de Finetti representation has a common positive probability measure mu on physically feasible symmetric two-bit ordinary noise Fourier coordinates (u,w). The physical domain is

    -1<=u<=1,   2|u|-1<=w<=1.                       (4)

Indeed, inverse Walsh gives mask probabilities

    p00=(1+2u+w)/4, p10=p01=(1-w)/4,
    p11=(1-2u+w)/4,

so nonnegativity is equivalent to (4). Let nu_0,nu_1 be the exceptional-mask **pair-parity signed measures**, with |nu_h|<=mu. Let v be the shared exceptional-mask one-bit signed measure. Physical nonnegativity of the exceptional 11 mask atom under each hypothesis gives

    2v<=mu + (nu_0 wedge nu_1),                      (5)

where the meet is the pointwise minimum of the two signed Radon–Nikodym densities relative to mu. We do **not** assume the exact infinite dyadic relation holds.

Write

    J=int(1-u)dmu, H=int min(dnu0,dnu1),
    C_ord=J/2, C_exc=(1-int dv)/2.                   (6)

For any test f define the signed dyadic defect

    D[f]=int (2f(u,w)+7f(u,w/2)) dnu0
             -(f(u,w)+8f(u,w/2)) dnu1.             (7)

The BM-29 relation is precisely D=0 for an exactly equalizing infinite channel. BM-31's empirical infinite extension of a finite-n equalizer can have nonzero D.

### A dual envelope lemma

Define c(u)=16(1-u)/5. Suppose f is a real function on [-1,1]² such that on every physical (u,w),

    |1-f(u,w)+f(u,w/2)| <= c(u),                    (8)
    |3f(u,w)+15f(u,w/2)| <= 1+c(u).                 (9)

Then, for any -1<=a,b<=1,

    min(a,b)
      <=c(u)+(2f+7f_shift)*a -(f+8f_shift)*b,       (10)

where f=f(u,w), f_shift=f(u,w/2).

**Proof of the pointwise lemma.** Put A=2f+7f_shift and B=-(f+8f_shift). The function min(a,b)-Aa-Bb is affine on each of the two triangular regions a<=b and b<=a of the square [-1,1]². Its maximum therefore occurs at one of the four corners and equals

    max{ |1-A-B|, -1+|A-B| }.

Here A+B=f-f_shift and A-B=3f+15f_shift. Conditions (8)-(9) assert that both maxima are at most c(u), proving (10). □

Multiply (10) by dmu with a=dnu0/dmu, b=dnu1/dmu and integrate. This immediately gives the robust signed-overlap inequality

    **H <= (16/5) J + D[f].**                        (11)

Crucially, (11) is valid when D is **nonzero**, and holds over arbitrary atomic or continuous directing measures with arbitrary world-dependent exceptional-pair correlations. By (5),

    C_exc >= (1-H)/4.

Substitute (11) and C_ord=J/2 to obtain

    8C_ord+5C_exc
       >=5/4+4J-(5/4)H
       >=**5/4-(5/4) D[f]**.                       (12)

The missing task is to construct a *globally bounded, Lipschitz* f satisfying (8)-(9) with useful norms.

## 3. BM-33/T2: an explicit exact piecewise-bilinear potential

Define the one-variable base function f0 on [-1,1] by

    f0(w) =
      -2/15,                             w<=1/4,
      -2/15+(8/5)(w-1/4),               1/4<w<=3/8,
       1/15,                            3/8<w<=1/2,
       1/15+(4/5)(w-1/2),               1/2<w<=3/4,
       4/15,                             w>3/4.      (13)

It is continuous, piecewise affine, nondecreasing, and has

    sup|f0|=4/15, Lip(f0)<=8/5.

A direct evaluation at the four breakpoints w=3/8,1/2,3/4,1, followed by linear interpolation within each interval, gives **for every real w in [3/8,1]**

    f0(w)-f0(w/2)=1/5,
    |3f0(w)+15f0(w/2)|<=9/5.                       (14)

These are exact endpoint/affine identities, so checking the four rational endpoints proves the entire continuum, rather than approximating it with a numerical grid.

Now define the two-variable function f(u,w) by three u-regimes. Use clamp(x,0,t)=min(t,max(0,x)).

    f(u,w)=
      0,                               u<=11/16,

      (16u-11)f0(w),                    11/16<u<=3/4,

      (1-t)f0(w)-t/6+
            clamp(2w-1,0,t),           3/4<u<=1,
                           t=4u-3.                (15)

This defines a real continuous piecewise-bilinear function on the entire compact square [-1,1]², including all physical states. Its exact uniform bounds are

    **sup|f|<=5/6,     Lip_l1(f)<=64/15.**         (16)

The norm bound follows from the ranges of f0 and the clamp term. The Lipschitz bound follows by inspecting affine pieces: in the middle u-regime |partial_u f|<=16*(4/15)=64/15 and |partial_w f|<=8/5. In the upper regime |partial_u f|<=58/15 and |partial_w f|<=18/5. The function is continuous across both u-regime boundaries, and all slopes are bounded by 64/15. This proves the l1-Lipschitz bound globally.

### Exact proof that every physical point satisfies the dual

We verify (8)-(9) algebraically in three regimes.

**Regime A, u<=11/16.** Here c(u)>=1 and f=f_shift=0. The left sides of (8)-(9) are 1 and 0, so both inequalities hold.

**Regime B, 11/16<u<=3/4.** Physical feasibility (4) gives w>=2u-1>=3/8, where (14) holds. Put t=16u-11, so 0<t<=1 and c(u)=1-t/5. Since f=t f0,

    f-f_shift=t/5,
    |3f+15f_shift|<=9t/5.

The first left side of (8) equals 1-t/5=c(u). The second is at most 9t/5, which is at most 1+c(u)=2-t/5 for t<=1.

**Regime C, 3/4<u<=1.** Put t=4u-3∈(0,1], so c(u)=4(1-t)/5. Physical feasibility gives

    w>=2u-1=(1+t)/2,    w/2<=1/2.

Consequently clamp(2w-1,0,t)=t and clamp(w-1,0,t)=0. Equation (15) therefore gives

    f(u,w)=(1-t)f0(w)+5t/6,
    f(u,w/2)=(1-t)f0(w/2)-t/6.

Since w>=1/2, identity (14) applies:

    f-f_shift=(1-t)/5+t
             =1-4(1-t)/5
             =1-c(u),

    3f+15f_shift=(1-t)[3f0(w)+15f0(w/2)].

The first dual inequality is an equality; the second holds because

    |3f+15f_shift|
       <=(1-t)*9/5
       <=1+4(1-t)/5=1+c(u).

This completes the global proof of both pointwise inequalities. □

### Sharpness on the BM-27 equality atoms

At u=3/4, the two interacting BM-27 ordinary parity values have

    f(3/4,1)=4/15,    f(3/4,1/2)=1/15,
    f(3/4,1/4)=-2/15.

Both dual conditions are tight at w=1 and w=1/2. At the remaining ordinary identity mode (u,w)=(1,1),

    f(1,1)=5/6,    f(1,1/2)=-1/6,

and the first condition is again tight. The BM-27 directing masses and exceptional signed parity measures therefore saturate (11) and (12); the resulting finite-rate dual has **zero gap at the exact limiting optimum**.

The [BM-33 code](robust_overlap_potential_BM33.py) checks all exact breakpoints and the three symbolic interpolation cases, and the independent tests check every point of a dense rational physical grid, derivatives/Lipschitz inequalities on randomized exact rational pairs, and the BM-27/BM-30 equality families.

## 4. BM-33/T1 finite-n consequence

Take an arbitrary **optimal** finite n-path erasing mask pair Q0,Q1 and average it by the group symmetries. BM-31 builds a genuine infinite empirical-exchangeable extension with the same individual per-bit costs and its ordinary-plus-exceptional compatibility constraints preserved. Write its costs C_ord and C_exc. They satisfy

    C_ord<=eta_n,  C_exc<=eta_n.

Apply the robust weighted inequality (12):

    13 eta_n >= 8C_ord+5C_exc
               >=5/4-(5/4)*D[f],

so

    eta_n >=5/52-(5/52)|D[f]|.                    (17)

BM-32 established for any B-bounded L-Lipschitz test, after keeping k<=n ordinary reported paths, that the signed defect of the infinite empirical extension obeys

    |D[f]|
      <=64B*sqrt(v_(n,k)) +224L/(3 sqrt(k)),
    v_(n,k)=k(k-1)/[2(n-1)(n-k+1)].                (18)

Substitute the **globally proved** values B=5/6, L=64/15 from (16) into (17)-(18). Exact fraction simplification gives

    **eta_n >=5/52
      -(200/39)*sqrt(v_(n,k))
      -(3584/117)/sqrt(k).**                       (19)

The BM-27 all-n upper eta_n<=5/52 proves the two-sided assertion (1) of section 1.

### Explicit asymptotic rate and a coarse universal constant

Choose k=floor(n^(2/3)). For n>=8, elementary inequalities give

    n^(2/3)/2 <= k <= n^(2/3),
    n-1>=n/2,
    n-k+1>=n/2.

Consequently

    v_(n,k)<=2n^(-2/3),
    1/sqrt(k)<=sqrt(2)n^(-1/3).

From (1),

    5/52-eta_n
       <=sqrt(2)*(200/39+3584/117)*n^(-1/3)
       =sqrt(2)*(4184/117)*n^(-1/3)
       <**51 n^(-1/3)**.                           (20)

The final strict inequality is verified by the exact integer comparison `2*4184² < (51*117)²`. This proves the rate (2) and explicit universal statement (3).

These constants are deliberately loose. The tight independent q8 n16 lower certificate in BM-28 is already about **0.09487758**, whereas (19) is not competitive at n=16. Equation (19) becomes nontrivial for sufficiently large n. The significance of BM-33 is a **uniform, logically complete finite-n convergence theorem** from the BM-29/30 asymptotic structure.

### Exact rational computer verification

The square roots in (19) are real analytic bounds, while the [BM-33 implementation](robust_overlap_potential_BM33.py) stores a conservative **pure rational squared-gap certificate**:

    (5/52-eta_n)^2
       <=2*[(200/39)^2*v_(n,k)
             +(3584/117)^2/k].                     (21)

It uses (a+b)^2<=2a²+2b², so no floating-point square root is needed to validate the finite-rate claim. The suite checks the exact rates against BM-25 n2 and BM-26 n3 exact optima and the BM-28 n16 certified lower value, while retaining the exact BM-29/BM-30 limiting equality.

The test suite includes arbitrary finite signed measures with *nonzero dyadic defect* to ensure (11)-(12) do not accidentally rely on the exact infinite relation D=0. An end-to-end finite empirical-mask check additionally converts the registered BM-25 n=2, BM-26 n=3, and BM-27 n=2/3 world-aware attaining masks into their actual histogram directing measures, verifies the signed overlap and the BM-32 independent dyadic evaluation, and checks the new finite scalar bound directly. A completely independent four-corner check numerically corroborates (10) on more than twenty thousand exact rational physical parameter points. The global theorem itself follows from the analytic endpoint and convexity argument.

## 5. Open problems and mathematical scope

**Resolved in the specified statistical channel:** BM-29 found the exact limiting erasure threshold 5/52, BM-30 proved its unique symmetrized limiting channel, BM-31 quantified finite exchangeability, BM-32 quantified its signed-measure residual, and **BM-33 now proves an explicit finite-n scalar convergence rate O(n^(-1/3))**.

The next useful questions are to improve the numerical constants/rate, obtain sharp finite-n optima for n>=4, generalize the robust pointwise dual to q>=16 or longer paths, and translate the finite-statistical monitoring insights into separately attested and costed intervention experiments. A polynomial dual approximation may still improve the finite-n rate, but a continuous exact bounded-Lipschitz dual has already solved the original rate-existence question.

The result uses classical de Finetti exchangeability, finite-hypergeometric KL/Pinsker bounds, Fourier convolution and pointwise linear-program duality; its explicit piecewise certificate is a model-specific constructive argument. Earlier foundational mathematics includes [Hewitt–Savage (1955)](https://doi.org/10.1090/S0002-9947-1955-0076206-8) and [Diaconis–Freedman (1980)](https://doi.org/10.1214/aop/1176994663). The infinite measure/disintegration steps in BM-29 are written in mathematical prose and have not been formalized in Lean. Independent mathematical peer review and a novelty survey remain appropriate before asserting publication originality.

No live model safety, trusted restoration root, authenticated control, or new Unique Games proof is claimed.
