# BM-35: Exact smooth polynomial overlap dual and an \(O(1/n)\) erasure-rate theorem

**11 November 2026 | constructive rational polynomial certificate, global Bernstein positivity proof, finite-sample Taylor bound.**

This strengthens [BM-34's finite-replica \(O(n^{-1/2})\) bound](DIRECT_FINITE_CONCENTRATION_BM34.md) for the replicated q8 gain-graph observation channel. The new argument uses an explicitly certified **degree-five smooth polynomial** satisfying BM-33's robust signed-overlap dual inequalities at every physical noise parameter. Its bounded second derivatives convert the unbiased all-\(n\) Fourier estimator's variance into an **inverse-\(n\)** bias, giving the first registered finite-replica \(O(1/n)\) scalar theorem.

The model is unchanged: \(q=8\), \(n\) ordinary two-edge paths with total gain zero in both hidden worlds, and one exceptional two-edge path with gain zero/nonzero. Each episode samples fresh uniform vertex labels. The full Boolean edge-satisfaction output is observed after a potentially correlated, hypothesis-aware XOR mask that is **independent of the current clean observation**. The per-edge maximum mask marginal is \(\eta\), and \(\eta_n(8,2)\) is the smallest such \(\eta\) that can equalize the two complete observation laws.

## 1. BM-35/T1: an explicit \(O(1/n)\) scalar bound

> **Theorem.** For every integer \(n\ge1\),
>
> \[
> \boxed{\displaystyle
> 0\le \frac5{52}-\eta_n(8,2)\le\frac{348}{n}.}
> \]
>
> The coefficient is conservative. Its rational certificate actually supplies \(K/n\) with
>
> \[
> K=
> \frac{431565367752631556213009198104}
> {1242352509936697954210206375}
> \approx347.3775472749 <348.
> \]

BM-27's explicit common construction already proves \(\eta_n\le5/52\) for all \(n\). The new lower proof is global over every legal world-dependent, within-episode correlated readout mask. It uses only a finite histogram representation of the original \(n\) masks, their conditional path moments, and an exact polynomial dual.

The earlier BM-34 theorem showed \(5/52-\eta_n\le(2158/117)/\sqrt{n}\). At \(n=10^6\), the new bound is \(0.000348\) in probability units, equivalent to **0.0348 percentage points**. It gets smaller proportionally to \(1/n\).

## 2. A degree-five rational polynomial sharp at the limiting channel

Use the physical symmetric ordinary-mask pair Fourier coordinates

\[
-1\le u\le1,\qquad 2|u|-1\le w\le1.
\]

BM-29's signed dyadic defect, written for a test function \(f\), is

\[
D[f]=\int \bigl(2f(u,w)+7f(u,w/2)\bigr)d\nu_0
-\int \bigl(f(u,w)+8f(u,w/2)\bigr)d\nu_1.
\]

BM-33's pointwise overlap lemma shows that the following four inequalities suffice for the robust weighted lower bound:

\[
\begin{aligned}
c-1+f(u,w)-f(u,w/2)&\ge0,\\
c+1-f(u,w)+f(u,w/2)&\ge0,\\
1+c-3f(u,w)-15f(u,w/2)&\ge0,\\
1+c+3f(u,w)+15f(u,w/2)&\ge0,
\end{aligned}
\quad c=\frac{16(1-u)}5.
\tag{1}
\]

BM-35 supplies a polynomial \(f(u,w)=\sum_{i+j\le5}a_{ij}u^iw^j\) with 15 nonzero terms. Every coefficient is an **exact integer over a common denominator**

\[
Q=10618397520826478241112875.
\]

| Monomial \(u^i w^j\) | Integer numerator \(Qa_{ij}\) |
|---|---:|
| 1 | −1076736653654158041110193 |
| \(w^2\) | 18464882583625017233477460 |
| \(w^3\) | 6486402490362451683275616 |
| \(w^4\) | −35835488780122577036523072 |
| \(w^5\) | −6593003805718016241762816 |
| \(u\) | −2587870994787646052289222 |
| \(uw\) | −9876877388907284199697128 |
| \(uw^2\) | 37702214153042684718671136 |
| \(u^2w\) | −13545651178393693820786304 |
| \(u^2w^2\) | 22915113666863066818300544 |
| \(u^2w^3\) | 2839140676754611310347776 |
| \(u^3\) | 16624936351390026791749152 |
| \(u^3w\) | −63356923913487888775100544 |
| \(u^3w^2\) | 35359145140666198863460864 |
| \(u^4\) | 1226259363776323810894848 |

The coefficients were found using a numerical linear-program search **subject to exact binding values at the three limiting-channel modes**. The numerical search is only a discovery mechanism; every assertion in the theorem is subsequently checked by an independent pure-rational certificate.

At BM-27's optimal dyadic modes, the polynomial has the exact values

\[
f(3/4,1)=4/15,\quad
f(3/4,1/2)=1/15,\quad
f(3/4,1/4)=-2/15,
\]

and \(f(1,1)-f(1,1/2)=1\). These recover the equality conditions in the sharp BM-29 overlap bound.

## 3. BM-35/L1: exact positivity across the entire physical continuum

The checker verifies (1) over a two-dimensional **continuum**, using the nonnegativity of the Bernstein basis on the unit square.

Partition the physical \(u\)-interval at the rational breakpoints

\[
-1,-1/2,0,1/4,1/2,5/8,11/16,3/4,13/16,7/8,1.
\]

For each \(u\), parameterize its complete allowed \(w\)-range by

\[
w=\bigl(2|u|-1\bigr)+y\bigl(2-2|u|\bigr),
\qquad 0\le y\le1,
\tag{2}
\]

and split \(y\) at \(0,1/4,1/2,3/4,1\). This gives **40 closed parameter cells**. On every cell, \(u\) is affine and \(w\) is bilinear in local coordinates \((x,y)\in[0,1]^2\).

Each of the four slacks in (1) becomes a bivariate polynomial with degree at most 5 in each local variable. Expand it exactly as

\[
g(x,y)=\sum_{a,b=0}^5\beta_{ab}
\binom5a x^a(1-x)^{5-a}
\binom5b y^b(1-y)^{5-b}.
\]

The [BM-35 certificate checker](smooth_polynomial_overlap_BM35.py) reconstructs all coefficients using the exact power-to-Bernstein identity

\[
x^i=\sum_{a=i}^5
\frac{\binom ai}{\binom5i}
\binom5a x^a(1-x)^{5-a}.
\]

It checks **40 cells × 4 inequalities × 36 coefficients = 5,760 exact rational inequalities**. Every coefficient is nonnegative; **72 coefficients are exactly zero**. Since every Bernstein basis factor is nonnegative on \([0,1]^2\), this finite rational certificate proves all four original inequalities for **every real physical \((u,w)\)**.

The proof includes the physical region boundaries \(w=2|u|-1\) and \(w=1\). A separate direct rational-grid test checks the original inequalities as an independent sanity control, and deliberate certificate perturbations are rejected.

## 4. BM-35/L2: bounded Hessian and inverse-\(n\) estimator bias

BM-34 introduced the full-sample ordinary Fourier estimators. BM-35 uses the **unclipped** versions

\[
\widehat U=\frac2{3n}\sum_{i=1}^n(X_i+Y_i),
\qquad
\widehat W=\frac1n\sum_{i=1}^n X_iY_i,
\tag{3}
\]

where \(X_i,Y_i\in\{-1,+1\}\) are the two reported edge signs for ordinary path \(i\).

After the readout masks are symmetrized, condition on their full empirical flip-count histogram \(C=(c_0,c_1,c_2)\), the exceptional mask and the clean terminal-difference regime A or B. The ordinary mask-type ordering can be fixed because the estimator is permutation invariant. Fresh clean path interiors and the random orientation of one-flip masks are independent from path to path under this conditioning. Consequently,

\[
\mathbb E(\widehat U)=u=\frac{c_0-c_2}{n},
\qquad
\mathbb E(\widehat W)=
\begin{cases}w,& A,\\w/2,&B,\end{cases}
\]

with \(w=(c_0-c_1+c_2)/n\). The exact conditional variances, previously independently verified in BM-34, satisfy

\[
\begin{array}{c|cc}
&\operatorname{Var}(\widehat U)&\operatorname{Var}(\widehat W)\\
A&\le7/(9n)&0\\
B&\le4/(9n)&\le3/(4n).
\end{array}
\tag{4}
\]

The **unclipped** statistic \(\widehat U\) lies in \([-4/3,4/3]\), while \(\widehat W\in[-1,1]\). The polynomial is smooth on this entire rectangle. Direct coefficient-wise differentiation yields exact bounds

\[
\begin{aligned}
\|\partial_{uu}f\|_\infty&\le M_{uu}<97,\\
\|\partial_{uw}f\|_\infty&\le M_{uw}<93,\\
\|\partial_{ww}f\|_\infty&\le M_{ww}<96.
\end{aligned}
\tag{5}
\]

The bounds use the exact rational sum of absolute monomial coefficients and appropriate powers of \(4/3\). The [implementation](smooth_polynomial_overlap_BM35.py) computes the three complete fractions and the resulting rate coefficient.

For any centered random pair \((\Delta U,\Delta W)\), a second-order Taylor expansion along the segment from its mean gives

\[
\left|\mathbb E f(U+\Delta U,W+\Delta W)-f(U,W)\right|
\le
\frac12M_{uu}\operatorname{Var}(\Delta U)
+M_{uw}\sqrt{\operatorname{Var}(\Delta U)\operatorname{Var}(\Delta W)}
+\frac12M_{ww}\operatorname{Var}(\Delta W).
\tag{6}
\]

The first-order terms vanish by conditional unbiasedness. Using (4), the matched-regime bias is at most \(7M_{uu}/(18n)\). In the unmatched regime use \(\sqrt{1/3}\le3/5\) to obtain

\[
\frac1n\left(
\frac29M_{uu}+\frac35M_{uw}+\frac38M_{ww}\right).
\]

Let

\[
C=\max\left\{
\frac7{18}M_{uu},\
\frac29M_{uu}+\frac35M_{uw}+\frac38M_{ww}
\right\}.
\tag{7}
\]

The exact rational coefficient calculation gives \(C\approx112.8977028643\). Thus **for every histogram, exceptional mask and clean regime**, the estimator's expected polynomial bias has magnitude at most \(C/n\).

The unclipped observable in the actual reported data is

\[
G_f=(-1)^{\text{exceptional reported-pair parity}}
f(\widehat U,\widehat W).
\tag{8}
\]

It is a measurable function of the **entire actual finite report**, and is the same in both worlds. Complete reported-output equality means \(\mathbb E_0G_f=\mathbb E_1G_f\).

The corresponding ideal conditional expectations differ by exactly \(D[f]/16\), with \(D\) the signed dyadic defect of the common finite empirical histogram directing measure. Each world incurs at most \(C/n\) bias from (6)/(7), so

\[
\boxed{|D[f]|\le\frac{32C}{n}.}
\tag{9}
\]

This estimate uses the actual finite mask distributions and conditional variance, with no iid empirical-replacement error and no infinite de Finetti limiting argument.

## 5. The scalar rate follows from the certified pointwise dual

BM-33's robust pointwise lemma, applied to this very polynomial \(f\), gives for the same finite empirical directing measure and world-dependent exceptional parity measures

\[
8C_{\rm ordinary}+5C_{\rm exceptional}
\ge\frac54-\frac54 D[f].
\tag{10}
\]

Both corruption marginals are bounded by the finite optimum \(\eta_n\), so

\[
13\eta_n\ge\frac54-\frac54 D[f]
\quad\Longrightarrow\quad
\eta_n\ge\frac5{52}-\frac5{52}|D[f]|.
\]

Combining with (9) yields the exact rational inverse-\(n\) coefficient

\[
\frac{40C}{13}
=
\frac{431565367752631556213009198104}
{1242352509936697954210206375}
<348.
\]

BM-27 already proves \(\eta_n\le5/52\), completing the main theorem.

The code also provides the all-rational squared-gap certificate

\[
\bigl(5/52-\eta_n\bigr)^2\le\frac{348^2}{n^2}.
\tag{11}
\]

A direct full-cube regression independently reconstructs the output distributions from the previous BM-25, BM-26 and BM-27 attaining masks, computes the **unclipped** observable, and checks that its exact expectation difference is zero. It then computes the ideal finite empirical signed defect with an independent formula and verifies both the Taylor bound and the scalar result. Deliberately corrupted dual coefficients fail the global Bernstein checker.

## 6. Mathematical scope and next work

BM-35 is a constructive finite statistical-channel result. The polynomial was discovered by a numerical LP, but the submitted theorem uses an **exact rational Bernstein positivity certificate** and standard-library Fraction arithmetic, so verification does **not trust the numerical solver**. There is no stochastic approximation in the final inequalities, and the certificate covers the complete physical domain.

The resulting \(O(1/n)\) upper on the finite-replica gap is stronger in rate than BM-34's \(O(n^{-1/2})\) theorem. Its constant 348 is conservative, especially for modest \(n\) where the exact BM-25/BM-26 optima and BM-28 n=16 lower certificate are much tighter. BM-35 does not prove the \(1/n\) exponent is sharp, derive the exact finite-\(n\) optimum for \(n\ge4\), or generalize automatically to other alphabets or heterogeneous graph cores.

Useful next steps are to optimize the Hessian envelope while retaining the exact Bernstein certificate, seek finite-n duals with sharp constants or exponential rates, formalize the polynomial positivity and probabilistic arguments in Lean, and extend the construction to q>=16 and nonuniform path lengths.

The mathematical ingredients are polynomial Bernstein positivity, a finite symmetric gain-channel Fourier transform, conditional second moments and pointwise LP duality. No empirical AI-monitoring guarantee, authenticated restoration mechanism or Unique Games theorem is claimed.
