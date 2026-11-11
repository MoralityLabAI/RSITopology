# BM-34: Direct finite-population concentration gives an O(n⁻¹ᐟ²) masking convergence rate

> **Subsequent result, BM-35 (11 November 2026):** The [exact degree-five rational Bernstein dual](SMOOTH_POLYNOMIAL_ERASURE_RATE_BM35.md) improves the scalar threshold rate to \(0\le5/52-\eta_n(8,2)\le348/n\) for every \(n\ge1\). The inverse-square-root and inverse-cube-root bounds below remain valid historical results. BM-35 proves continuum positivity by checking 5,760 exact rational Bernstein coefficients and uses conditional second-order Taylor bias on all ordinary reported paths.


**11 November 2026 | exact finite-channel theorem, independent conditional variance table and full-output checks.**

This improves [BM-33's scalar finite-n rate](FINITE_ERASURE_RATE_BM33.md) for the q=8 replicated gain-path readout game. BM-33's approximate infinite-exchangeability extension incurs a finite-sampling error when it replaces without-replacement ordinary mask types with conditionally i.i.d. draws. The central observation of BM-34 is that its Fourier estimator is a **symmetric average over all n ordinary paths**. Conditional on the complete empirical mask histogram, the order of the n mask types is irrelevant, and the remaining clean/noise randomness has **independent path contributions**. This permits a direct nonasymptotic concentration bound with no finite de Finetti approximation and no logarithmic loss.

The result is a constructive finite-probability proof of a faster scalar rate, without an assumption that the finite-n mask optimizers have a specific product-mixture representation. All masks may remain **world-aware and arbitrarily correlated within each episode**, subject to the original requirement that the current clean report is unavailable to the masking channel.

## 1. Main theorem BM-34/T1

Fix q=8, n>=1 ordinary two-edge u–v paths with total gain zero in both worlds and one exceptional two-edge path with gain zero in the flat world and a fixed nonzero gain in the frustrated world. Every episode samples independent uniform F₂³ vertex labels. The monitor receives the **entire** Boolean edge-satisfaction vector, potentially corrupted by a correlated XOR mask whose law is world-aware but independent of the current clean report. Every edge may be flipped with marginal probability at most eta.

Let eta_n(8,2) denote the minimum such uniform eta for which the complete two-world output laws can be made identical. BM-27 proved the global upper eta_n<=5/52. BM-29 established the exact limit 5/52, and BM-33 proved a finite-n O(n^(-1/3)) rate.

> **BM-34/T1 (direct finite concentration rate).** For EVERY integer n>=1,
>
> \[
> \boxed{\displaystyle
> 0\le\frac5{52}-\eta_n(8,2)
> \le\frac{2158}{117\sqrt n}.}
> \tag{1}
> \]
>
> In particular, **eta_infinity−eta_n=O(n^(-1/2))**.

The proof works directly on the n-path experiment and uses only exact algebra, a conditional second-moment bound, the established explicit BM-33 overlap dual, and the existing BM-27 legal upper eraser.

The coefficient 2158/117≈18.4444 is conservative. It provides a uniform rate for arbitrary n and arbitrary legal correlated masks. Exact finite-n thresholds at n=2,3 and the certified n=16 lower bound remain much tighter at those small sizes.

## 2. Symmetry and the exact finite empirical representation

As in BM-24 and BM-31, independently permute ordinary paths and swap the two bits in every ordinary path; also swap the exceptional pair's bits. The complete clean output laws are invariant under this action. Averaging an arbitrary legal equalizing mask pair under this symmetry preserves the exact two-world output equality and cannot increase the uniform per-bit flip allowance.

After symmetrization the ordinary mask is described by the three empirical counts

\[
 C=(c_0,c_1,c_2),\qquad c_0+c_1+c_2=n,
\]

where c_t counts paths with exactly t corrupted readout bits. Keep the exceptional two-bit mask Z_h separately, since its full conditional law may differ between hidden hypotheses.

Conditioned on (C,Z_h), the ordinary mask types have a **uniform random ordering**, and every one-flip type has a uniformly chosen orientation. All ordinary path interiors are freshly and independently labeled conditional on the two terminal labels. The masking channel is also independent of the current clean vertex labels. These properties imply that conditional on the terminal difference and a **fixed ordering of the mask types**, the path output pairs are independent.

The empirical statistics below are symmetric under permutation of the ordinary paths. We may therefore fix any canonical ordering of the c_0 type-zero paths, c_1 type-one paths and c_2 type-two paths **without changing the distribution of those statistics**. The random type ordering contributes no variance to the symmetric sum.

The noise's ordinary pair Fourier coordinates are precisely

\[
 u=\frac{c_0-c_2}{n},\qquad
 w=\frac{c_0-c_1+c_2}{n}.
\tag{2}
\]

By BM-29's strict Fourier positivity, complete output equality forces both worlds to have the **same marginal law of C** and the same marginal law of (C, either individual exceptional noise bit). The exceptional pair-parity signed measures may differ, and that is the degree of freedom needed for the readout attack.

## 3. Exact conditional path variance table

Let the observed ordinary bits on path i be encoded as Fourier signs X_i,Y_i∈{−1,+1}, and let

\[
 U_i=\frac23(X_i+Y_i),\qquad V_i=X_iY_i.
\tag{3}
\]

Define the empirical estimators using **all n paths**:

\[
 \widehat u=\operatorname{clip}_{[-1,1]}
   \left(\frac1n\sum_{i=1}^n U_i\right),
 \qquad
 \widehat v=\frac1n\sum_{i=1}^n V_i.
\tag{4}
\]

The clean ordinary two-bit pair law conditional on the terminal difference is one of

\[
 A=(7/8,0,0,1/8),\quad
 B=(3/4,1/8,1/8,0),
\]

indexed by Boolean pair outcomes 00,10,01,11. Here A means the terminal difference matches the ordinary path gain; B means it differs. Both have clean one-bit Fourier mean 3/4. Their clean full-pair parity means are 1 and 1/2 respectively.

Condition on one path's mask type t∈{0,1,2}. Type zero has mask 00, type one uniformly chooses 10 or 01, and type two has mask 11. The exact conditional distribution is the XOR convolution of the clean A/B law and the corresponding mask law. Enumerating its four possible outputs gives:

| Clean regime | Mask type t | E U_i | E V_i | Var(U_i) | Var(V_i) |
|---|---:|---:|---:|---:|---:|
| A | 0 | 1 | 1 | 7/9 | 0 |
| A | 1 | 0 | −1 | 0 | 0 |
| A | 2 | −1 | 1 | 7/9 | 0 |
| B | 0 | 1 | 1/2 | 1/3 | 3/4 |
| B | 1 | 0 | −1/2 | 4/9 | 3/4 |
| B | 2 | −1 | 1/2 | 1/3 | 3/4 |

Every table entry is a direct four-outcome **rational identity** independently checked in [the BM-34 tests](test_direct_finite_concentration_BM34.py). In particular, the conditional means of (4), given the entire histogram C, exceptional noise Z_h and terminal regime, are exactly

\[
 \mathbb E\widehat U=u,\qquad
 \mathbb E\widehat v=
 \begin{cases}w,&A,\\w/2,&B,\end{cases}
\tag{5}
\]

where \(\widehat U\) denotes the **unclipped** first statistic. Clipping cannot increase |\widehat U−u| because the true u lies in [−1,1].

Pathwise conditional independence at a fixed type allocation now gives the exact variances

\[
 \operatorname{Var}(\widehat U\mid C,A)
   =\frac{7(c_0+c_2)}{9n^2}\le\frac7{9n},
 \qquad
 \operatorname{Var}(\widehat v\mid C,A)=0,
\tag{6}
\]

and

\[
 \operatorname{Var}(\widehat U\mid C,B)
 =\frac{(c_0+c_2)/3+4c_1/9}{n^2}
 \le\frac4{9n},
 \qquad
 \operatorname{Var}(\widehat v\mid C,B)=\frac3{4n}.
\tag{7}
\]

These identities can be checked independently by enumerating the entire output distribution on every conditional fixed histogram with n<=4.

By Jensen/Cauchy–Schwarz,

\[
 \mathbb E|\widehat u-u|\le\sqrt{\operatorname{Var}(\widehat U)},
 \qquad
 \mathbb E|\widehat v-v|\le\sqrt{\operatorname{Var}(\widehat v)}.
\tag{8}
\]

Thus the estimator error has a uniform **n^(-1/2)** bound under both clean regimes, despite arbitrary correlations in the original world-dependent noise law. Conditional on the complete histogram, the sampling without replacement disappears from the permutation-invariant statistic.

## 4. BM-34/L1: direct observable control of the signed dyadic defect

Recall the BM-33 robust overlap potential f(u,w), whose complete analytic construction is in [BM-33](FINITE_ERASURE_RATE_BM33.md). It is defined on the entire square [−1,1]², including statistical estimates outside the physical noise region. Its *coordinatewise* Lipschitz constants can be bounded more sharply than a single l1 norm:

\[
 |f(u,w)-f(u',w')|
 \le\frac{64}{15}|u-u'|
     +\frac{18}{5}|w-w'|.
\tag{9}
\]

The proof is a finite affine-slope calculation. In the middle u-regime, the u derivative is 16 f_0(w) with |f_0|<=4/15, and the w derivative has magnitude at most 8/5. In the upper regime, put t=4u−3: the u derivative lies between

\[
 -4f_0(w)-\frac23
 \quad\text{and}\quad
 -4f_0(w)-\frac23+4,
\]

with maximum absolute value 58/15 over all f_0∈[−2/15,4/15]; the w derivative is bounded by 8/5+2=18/5. The lower u-regime is constant zero, and the potential is continuous across both regime boundaries. Hence (9) holds globally.

For clean regime A, equations (6)/(8)/(9) imply

\[
 \mathbb E|f(\widehat u,\widehat v)-f(u,w)|
 \le\frac{64}{15}\frac{\sqrt7}{3\sqrt n}
 \le\frac{512}{135\sqrt n}.
\tag{10}
\]

For regime B they give

\[
 \mathbb E|f(\widehat u,\widehat v)-f(u,w/2)|
 \le\frac1{\sqrt n}
   \left(\frac{128}{45}+\frac{9\sqrt3}{5}\right)
 \le\frac1{\sqrt n}
   \left(\frac{128}{45}+\frac{63}{20}\right)
 =\frac{1079}{180\sqrt n}.
\tag{11}
\]

The last step uses the exact rational comparison √3<=7/4. Bound (11) dominates (10). Consequently **for either hypothesis, either terminal regime, and every histogram/exceptional-noise state**, the conditional expected estimator error is at most 1079/(180√n).

Now define the actual, finite-sample **observable**

\[
 G_f=(-1)^{\text{special reported pair parity}}
       f(\widehat u,\widehat v).
\tag{12}
\]

It is a measurable function of the complete reported observations, and it is **the same test under both hidden hypotheses**. Since the two corrupted reported-output distributions are exactly equal, their expectations obey

\[
 \mathbb E_0 G_f=\mathbb E_1 G_f.
\tag{13}
\]

Replace the estimators inside each expectation by their ideal conditional coordinates (u,w) or (u,w/2). Because the mask is independent of the *current clean sample*, the clean terminal-match weights are precisely those calculated in BM-29. The difference of the two ideal expectations equals

\[
 \mathbb E_0G_f^{\rm ideal}
   -\mathbb E_1G_f^{\rm ideal}
   =\frac1{16}D[f],
\tag{14}
\]

where \(D=(2I+7S_*)\nu_0-(I+8S_*)\nu_1\) is the signed parity-measure defect of the **finite empirical directing measure**.

Each world contributes at most the conditional error (11), and the exceptional parity factor in (12) has absolute value one. Using (13)/(14) gives the **direct finite signed-defect bound**

\[
 \boxed{|D[f]|\le
 \frac{32}{\sqrt n}\frac{1079}{180}
 =\frac{8632}{45\sqrt n}.}
\tag{15}
\]

Equation (15) bypasses BM-31's with-replacement extension altogether. The directing measure used in (14) is the finite discrete distribution of C; **no infinite de Finetti limit, compactness or infinite measure disintegration is needed for this result**.

The [end-to-end verifier](direct_finite_concentration_BM34.py) reconstructs each actual BM-25/BM-26/BM-27 exact finite mask pair into its symmetrized empirical histogram law. It independently evaluates (12) under the complete corrupted output distributions, evaluates both ideal expectations directly from the A/B terminal weights, and verifies (14)/(15) using exact rational squares.

## 5. BM-34/T1: scalar rate via BM-33's robust pointwise dual

BM-33's explicit global pointwise overlap dual proved the following inequality for **every** physical common ordinary directing measure mu, hypothesis-specific exceptional parity signed measures nu_0,nu_1 and their common exceptional one-bit signed measure v:

\[
 8C_o+5C_s\ge\frac54-\frac54 D[f].
\tag{16}
\]

Here C_o is the ordinary bit flip rate and C_s the exceptional bit flip rate in the symmetrized empirical law. Both are bounded by the finite n erasure cap eta_n because the orbit averaging did not increase any marginal.

Therefore

\[
 13\eta_n
 \ge8C_o+5C_s
 \ge\frac54-\frac54 D[f],
\]

or equivalently

\[
 \eta_n\ge\frac5{52}
             -\frac5{52}|D[f]|.
\tag{17}
\]

Insert (15):

\[
 \eta_n\ge\frac5{52}
 -\frac5{52}\frac{8632}{45\sqrt n}
 =\frac5{52}-\frac{2158}{117\sqrt n}.
\tag{18}
\]

BM-27 already supplied an explicit legal **all-n** equalizing mask at 5/52, so \(\eta_n\le5/52\). Combining both inequalities proves (1) for every n>=1.

The coefficient and square-root manipulation are verified with exact rational identities:

\[
 \boxed{
 (5/52-\eta_n)^2
 \le\frac{(2158/117)^2}{n}.}
\tag{19}
\]

This is a conservative rational squared-gap certificate with no floating-point computation. It can be combined with any independently certified finite-n lower bound by taking the stronger of the two.

### Comparison with BM-33

| Property | BM-33 | BM-34 |
|---|---|---|
| Sampled ordinary paths | k=floor(n^(2/3)) | **all n** |
| Ordinary mask histogram | replaced by iid empirical mixture | **exact fixed histogram** |
| Additional finite-exchangeability TV loss | included | **zero** |
| Rate for eta_infinity−eta_n | O(n^(-1/3)) | **O(n^(-1/2))** |
| Infinite de Finetti limit needed to derive rate | no | no |
| Exact rational validation | yes | yes |

At n=10^12, (1) bounds the masking threshold gap by approximately 1.84×10^-5 in probability units, compared with the much looser BM-33 generic finite-window bound at that size. The new bound does **not** claim that finite-n minimax masking strategies themselves have converged in total variation at rate n^-1/2; BM-30's fixed-coordinate convergence remains qualitative.

## 6. Mathematical context and verification limits

The probabilistic principle is finite-population symmetrization: when an empirical mask histogram is fixed and the observed test is symmetric across all n path positions, the ordering of without-replacement mask types introduces no additional variance. This is related to the classical sampling-without-replacement concentration framework of [Hoeffding (1963)](https://doi.org/10.1080/01621459.1963.10500830) and [Serfling (1974)](https://doi.org/10.1214/aos/1176342611). The calculation here is explicitly model-specific and follows by direct conditional independence after fixing the type multiset.

New committed files:

- [direct_finite_concentration_BM34.py](direct_finite_concentration_BM34.py): exact four-point per-path moment table, exact conditional n-path variance, coordinatewise BM-33 potential norms, explicit finite O(n^-1/2) scalar certificate, and full-world masked-output versus latent-ideal observable checks.
- [test_direct_finite_concentration_BM34.py](test_direct_finite_concentration_BM34.py): independent one-path convolution/moment oracle, complete conditional-output enumeration for all histograms at n<=4, exact randomized coordinatewise Lipschitz controls, BM-25/26/27/30 full-mask witness checks, finite and trillion-path symbolic rate checks, malformed mask tests and comparisons against the prior BM-28 n16 lower certificate.

All computational checks use Python's standard-library `fractions.Fraction`, with no numerical optimizer or approximate integration. The theorem concerns the registered statistical masking experiment; it establishes **no live agent-control or alignment safety guarantee**, no independently authenticated root-state restoration and no Unique Games proof. Independent mathematical review and a Lean formalization would still be appropriate before making publication-level novelty claims.

The main remaining mathematical targets are a sharper n-dependent constant, a possible O(1/n) rate using structure beyond Lipschitz second-moment bounds, exact finite-n thresholds for n>=4, and higher-alphabet or longer-path generalizations.
