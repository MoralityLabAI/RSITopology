# BM-37: Quantitative total-variation certificates for correlated q8 readout masking

**11 November 2026 | bounded observable, matched-marginal separation, all-mask robustness and adaptive-transcript corollary.**

This extends [BM-36](TRIANGULAR_HESSIAN_RATE_BM36.md) from exact equality of full output laws to quantitative distinguishability. Its two principal results have different adversarial scope. BM-29 forces ordinary and ordinary-plus-one-special-bit noise marginal agreement **when complete output laws are exactly equal**; approximate output equality requires an additional robustness argument. A conditional theorem delivers the useful near-threshold coefficient, while a separate, much weaker universal theorem holds for arbitrary legal correlated masks.

The frozen statistical experiment: q=8, n ordinary gain-zero two-edge paths, one exceptional two-edge path whose gain is changed by a fixed nonzero element in world 1. Every episode uses fresh uniformly random vertex labels. The adversary knows the hidden world and may correlate all 2n+2 readout-mask bits, but each mask is independent of the current clean sample and every bit's flip marginal is at most eta. Let P0 and P1 denote the complete masked output laws, and \(\varepsilon=\operatorname{TV}(P_0,P_1)\) with \(\operatorname{TV}(P,Q)=\tfrac12\sum|P-P'|\).

## BM-37/T1: quantitative separation for matched noise marginals

After the legitimate independent within-ordinary-pair swaps, ordinary-path permutations and exceptional-pair swap, represent the masks by a histogram C and exceptional pair Z. Suppose the two worlds have (i) exactly the same distribution of C and (ii) exactly the same joint distribution of (C,Z_1). Because the exceptional pair is exchangeable, this also matches (C,Z_2). These conditions define the **matched-marginal adversary subclass**. All within-episode noise correlations and world dependence of the exceptional two-bit coupling remain allowed.

Define

\[
K=\frac{433489819753448825447087550392}
{3727057529810093862630619125}<117,\qquad
B=\frac{127}{50}.
\]

For every n>=1 and every eta in [0,1], the original BM-35 degree-five polynomial and BM-36 Hessian certificate yield

\[
\boxed{\varepsilon\ \ge\
\frac{65}{508}\left[\frac5{52}-\eta-\frac{K}{n}\right]_+.}
\tag{1}
\]

**Proof.** The common ordinary histogram measure \(\mu\) and common signed exceptional one-bit measure \(v\) satisfy the BM-33 pointwise overlap lemma. With world-specific signed exceptional parity measures \(\nu_h\), writing D[f] for the BM-29 dyadic defect gives

\[
13\eta\ge 8C_{\rm ord}+5C_{\rm exc}
\ge\frac54-\frac54D[f].
\tag{2}
\]

As in BM-35, condition on each full ordinary mask histogram, exceptional mask and clean terminal regime. The unclipped empirical Fourier estimator is unbiased. BM-36 bounds its polynomial expectation error in each world by \(C_{\rm tri}/n\), where \(K=40C_{\rm tri}/13\). Define the actual measurable score

\[
G=(-1)^{\text{exceptional reported pair parity}}\,
f(\widehat U,\widehat W).
\]

A new independent exact interpolation certificate gives \(|G|\le B\). Since \(|\mathbb E_0G-\mathbb E_1G|\le2B\varepsilon\) and the ideal expectations differ by D[f]/16,

\[
|D[f]|\le32B\varepsilon+\frac{32C_{\rm tri}}n.
\tag{3}
\]

Combining (2) and (3) yields \(5/52-\eta\le(40/13)B\varepsilon+K/n\). The inverse of \((40/13)B=508/65\) is 65/508, proving (1).

**Independent supremum certificate.** The observable's Fourier pair lies in the convex triangle with vertices (-4/3,1), (0,-1), (4/3,1). On 8 signed-u cells times 4 vertical-fraction cells, the degree-five polynomial pulls back to bidegree <=(5,5). An independently derived 6x6 exact rational Bernstein collocation inverse recovers all 36 coefficients per cell, totaling 1,152. Their maximum absolute value is

\[
\frac{3636528285638174746233679387}
{1433483665311574562550238125}
\approx2.536847<127/50.
\]

This proves the supremum bound on the complete observed-statistic triangle. It is independent of BM-35's power-to-Bernstein conversion and BM-36's degree-three Hessian interpolator.

## BM-37/T2: a universal low-noise four-bit witness

For **every** pair of legal masks, with no matched-marginal requirement, one ordinary path's reported pair parity times the exceptional path's reported pair parity has clean expectations 11/32 under H0 and 5/16 under H1. The clean sample and chosen mask are independent. With no more than eta probability of flipping each of the four selected bits, the mask parity expectation is at least \(1-8\eta\) and at most 1. Therefore

\[
\boxed{\varepsilon\ge [1/64-11\eta/8]_+}.
\tag{4}
\]

This is positive for eta<1/88, for every n, including history-aware mask selection with the per-history marginal cap. It is much weaker than the limiting erasure threshold 5/52 but applies to the **unrestricted** adversary.

## BM-37/T3: unconditional near-threshold separation with an explicit deconvolution penalty

A positive all-mask separation bound near 5/52 also follows from a conservative Fourier inversion argument. It is currently too weak for operational sample-size planning.

Let \(\mu_h\) be the symmetrized noise histogram law in each world, and \(v_h\) its signed one-special-bit measure. Put
\(d=\operatorname{TV}(\mu_0,\mu_1)\), and \(d_1\) equal to the TV of the world-specific noise joint laws (histogram, exceptional first bit). The complete output TV is epsilon. The clean ordinary Walsh multipliers are all strictly positive, with \(\widehat C_{\rm ord}(S)\ge(3/4)^n/8\). The multipliers including a single exceptional bit obey \(\widehat C_{\rm ord+one}(S)\ge(3/4)^{n+1}/8\), equal in both worlds (BM-29). Parseval, the exact inverse Fourier formula and Cauchy-Schwarz yield

\[
d\le L_0\varepsilon,\quad d_1\le L_1\varepsilon,\qquad
L_0=8(8/3)^n,\quad L_1=(64/3)(8/3)^n.
\tag{5}
\]

Let \(\mu_c=\min(\mu_0,\mu_1)\) pointwise, with mass \(1-d\). Trimming each world to this common subprobability law removes d mass from each; ordinary and exceptional per-bit costs can only decrease. Denote the resulting signed special one-bit laws by \(v_h^c\). They satisfy

\[
\|v_0^c-v_1^c\|_1\le2d_1+2d.
\tag{6}
\]

With \(v_c=(v_0^c+v_1^c)/2\) and \(H_c=\int\min(\nu_0^c,\nu_1^c)\), the exceptional-pair atom nonnegativity inequalities imply

\[
C_{\rm exc}^c\ge
\bigl[(1-d)-H_c-\|v_0^c-v_1^c\|_1\bigr]/4.
\]

Applying the BM-33 overlap inequality to the common subprobability law, and using \(C_{\rm ordinary}^c,C_{\rm exceptional}^c\le\eta\), gives

\[
\frac5{52}-\eta\le
\frac5{52}(d+\|v_0^c-v_1^c\|_1+D_c[f]).
\]

The original observed score differs from its trimmed counterpart in each world by at most Bd, so

\[
|D_c[f]|\le32B(\varepsilon+d)+32C_{\rm tri}/n.
\]

Together with (5) and (6),

\[
\boxed{
\varepsilon\ge
\frac{[\,5/52-\eta-K/n\,]_+}
{\frac5{52}\{32B+(3+32B)L_0+2L_1\}}.
}
\tag{7}
\]

Combining (4) and (7) yields the stated unconditional lower certificate. The denominator grows exponentially with n. The theorem is useful as a mathematical scope closure, while (1) is the practical matched-marginal reference.

## BM-37/T4: history-adaptive multi-episode Bayes bound

Suppose each new episode refreshes clean labels independently and, **conditional on every public history in either world**, the current masks obey the same cap and one of the conditions yielding a per-episode TV lower bound \(t>0\). These conditional mask laws may be chosen adaptively from the history. The conditional Hellinger affinity is at most \(\sqrt{1-t^2}\le1-t^2/2\). Induction over the transcript tree bounds its joint affinity by \((1-t^2/2)^m\) after m episodes, and hence the optimal equal-prior Bayes risk by

\[
\boxed{R_m^*\le\frac12(1-t^2/2)^m
\le\frac12e^{-mt^2/2}.}
\tag{8}
\]

This is a **pair-specific optimal likelihood-ratio detector** bound. It does not construct a single monitor robust to every adversary policy, nor guarantee a fixed false-positive rate. It remains valid with adaptive history-dependent strategies satisfying the registered per-history constraints; trajectory-average or marginal-only caps are insufficient.

## Eval and control applications

Use the matched-marginal family as a registration condition for a synthetic Control-Harness benchmark. BM-27's exact all-n eraser has mask cost 5/52 and zero output TV. Mix the eraser masks in both worlds with a zero mask using common weight lambda. The resulting pair retains matched noise marginals, has exact bit cap \((1-\lambda)5/52\), and the reported output TV is **lambda times the unmasked clean-output TV** for every n. This makes a graded reference family with a known positive or zero signal and a validated adversarial cap.

Measure empirical held-out FP/FN and the steganographic decoder utility gap, plus registered observation support, independent fresh labels, mask/clean independence and per-history cap. Report theoretical matched-TV, all-mask low-noise TV, the weak all-mask deconvolution TV, and any adaptive Bayes oracle bound in separate fields. A certified TV separation alone does not give a fixed-decoder accuracy or a finite-sample matched-FPR guarantee.

## Verification

[Exact source](quantitative_mask_tv_BM37.py) and [independent regression tests](test_quantitative_mask_tv_BM37.py) verify 1,152 supremum coefficients; exact interpolation and polynomial evaluations at arbitrary interior points; clean Walsh four-bit expectations; BM-27's exact world-dependent erasers; blended mask controls; deliberate matched-marginal violations; random legal noise distributions; and history-adaptive binary transcript controls. BM-35 and BM-36's original continuum and Hessian certificates are retained.

The underlying problem is a frozen finite q8 gain-graph statistical channel. A reduction from real neural observation systems, an adversary-independent decoder, stronger all-mask rates and independent peer review remain open.
