# BM-36: Triangular Bernstein Hessian certificate improves the q8 finite erasure rate to 117/n

**11 November 2026 | exact rational improvement to BM-35, same dual, same mask contract**

## Theorem

For the registered q=8 repeated two-edge-path experiment with n ordinary paths, one exceptional path, fresh uniformly sampled vertex labels, and current-clean-independent but possibly fully correlated and hypothesis-aware XOR masks, the minimum per-bit erasure allowance obeys, for every integer n>=1,

\[
\boxed{0\leq \frac{5}{52}-\eta_n(8,2)\leq\frac{117}{n}.}
\]

The same degree-five rational dual f from [BM-35](SMOOTH_POLYNOMIAL_ERASURE_RATE_BM35.md) proves this result. Its complete physical-domain signed-overlap inequalities remain certified there by 5,760 exact nonnegative Bernstein coefficients. Only the estimator-bias Hessian calculation changes.

The exact coefficient delivered by the new triangular certificate is

\[
K_{\rm tri}=
\frac{433489819753448825447087550392}
{3727057529810093862630619125}
\approx116.3088619605 <117.
\]

The older rectangle-wide monomial coefficient envelope gave K approximately 347.3775.

## Observation-support geometry

Each ordinary observed path produces two signs X_i,Y_i in {-1,+1}. Its two Fourier contributions are

\[
(U_i,W_i)=\left(\frac23(X_i+Y_i),X_iY_i\right).
\]

The only possible points are (-4/3,1), (0,-1), (4/3,1). The empirical means

\[
\widehat U=\frac1n\sum_i U_i,\quad
\widehat W=\frac1n\sum_i W_i
\]

therefore lie in the compact convex triangle

\[
T=\{(u,w): |u|\le4/3,\;3|u|/2-1\le w\le1\}.
\]

Conditional on any fixed ordinary empirical mask histogram, the exceptional mask and clean regime A/B, the means of the unbiased estimators lie in this same convex triangle. Every segment joining a realized estimator to its conditional mean also remains in T. Consequently, the conditional second-order Taylor remainder of BM-35 needs Hessian bounds only on T.

## Independent exact certificate

Use u breakpoints

\[
-4/3,-1,-2/3,-1/3,0,1/3,2/3,1,4/3
\]

and y breakpoints 0,1/4,1/2,3/4,1. On each of the eight u intervals and four y intervals, parameterize the triangle by

\[
u=u_a+(u_b-u_a)x,\qquad
w=(3|u|/2-1)+(2-3|u|/2)\bigl(y_a+(y_b-y_a)y\bigr),
\quad (x,y)\in[0,1]^2.
\]

The sign of u is fixed on each cell. The w-coordinate is bilinear in x,y. Each of the three second partial derivatives of f has total polynomial degree at most three, so its pullback on a cell has bidegree at most (3,3).

The [independent checker](triangular_hessian_BM36.py) evaluates each derivative at the 16 tensor grid nodes with x,y in {0,1/3,2/3,1}. It reconstructs all 16 bivariate cubic Bernstein coefficients by an exact inverse 4x4 collocation transform, whose inverse identity it checks directly. This uses neither BM-35's power-polynomial substitution nor its Bernstein expander.

The resulting 32 cells times three derivative fields times 16 coefficients yield **1,536 exact rational coefficients**. Since the cubic Bernstein basis is nonnegative and sums to one on the unit square, the maximum absolute coefficient in each field uniformly bounds that second derivative throughout T.

The exact maxima of those absolute coefficients are

\[
\begin{aligned}
M_{uu}&=\frac{436135497777991794997121344}{31855192562479434723338625}
 \approx13.6911901230,\\
M_{uw}&=\frac{640780500121816588916939272}{31855192562479434723338625}
 \approx20.1154175686,\\
M_{ww}&=\frac{17346026126993139909417264008}{286696733062314912510047625}
 \approx60.5030477387.
\end{aligned}
\]

These are certified envelopes obtained from Bernstein coefficients, rather than claims that the maxima of the derivatives themselves have been solved exactly.

## Finite n consequence

BM-34's exact conditional moment table supplies

\[
\begin{array}{c|cc}
&\mathrm{Var}(\widehat U)&\mathrm{Var}(\widehat W)\\
A&\le7/(9n)&0\\
B&\le4/(9n)&\le3/(4n).
\end{array}
\]

For a centered pair of estimator errors, Taylor's integral remainder and conditional Cauchy-Schwarz give

\[
\left|\mathbb E f(\widehat U,\widehat W)-f(\mathbb E\widehat U,\mathbb E\widehat W)\right|
\le\frac{1}{2}M_{uu}\mathrm{Var}(\widehat U)
+M_{uw}\sqrt{\mathrm{Var}(\widehat U)\mathrm{Var}(\widehat W)}
+\frac{1}{2}M_{ww}\mathrm{Var}(\widehat W).
\]

As in BM-35, the unmatched cross term is at most sqrt(1/3)/n <=3/(5n). Thus a uniform conditional bias coefficient is

\[
C_{\rm tri}=
\max\left(\frac7{18}M_{uu},\,
\frac29M_{uu}+\frac35M_{uw}+\frac38M_{ww}\right).
\]

The two complete reported-output laws coincide under any exact erasing mask pair, implying equality of the BM-35 exceptional-parity-weighted polynomial observable in the two worlds. Subtract its conditional ideal expectations, which differ by D[f]/16, to obtain

\[
|D[f]|\le32 C_{\rm tri}/n.
\]

The already certified pointwise signed-overlap dual yields

\[
13\eta_n\ge\frac54-\frac54D[f],
\]

whence

\[
0\le5/52-\eta_n(8,2)\le
\frac{40C_{\rm tri}}{13n}=\frac{K_{\rm tri}}n<\frac{117}n.
\]

BM-27 supplies the common all-n upper construction eta_n<=5/52.

## Verification and limits

The [BM-36 independent tests](test_triangular_hessian_BM36.py) check the exact inverse transform, all three rational coefficient maxima, interior Bernstein reconstruction against direct polynomial differentiation, exhaustive path-support cases through n=6, every histogram center through n=8, deliberate invalid polynomial mutations and symbolic rates out to n=10^12. The full-output equalizer regressions and exact global dual inequalities are inherited unchanged from BM-35 and its separate tests.

The improvement is to the **finite-n convergence coefficient** under the same frozen statistical access model. It does not establish a sharp n-dependent optimum, an optimal convergence exponent, a general Unique Games theorem or a deployed oversight guarantee. Independent mathematical review remains warranted.
