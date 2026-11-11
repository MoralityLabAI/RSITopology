# BM-40: Finite-replica Hellinger certificates for sequential monitoring

**11 November 2026 | exact rational affinity intervals, fixed graded q8 masking family**

BM-39 gives the complete-output one-episode total variation exactly for the graded BM-27 erasure channel. For repeated independent episodes, the relevant quantity is the Bhattacharyya (Hellinger) affinity

\[
B_n(\lambda)=\sum_{y}\sqrt{P_0^{(n,\lambda)}(y)P_1^{(n,\lambda)}(y)}.
\]

An exact arithmetic interval for B_n turns into an explicit upper bound on the optimal equal-prior Bayes error after m freshly and independently sampled episodes under the same world h.

## Finite histogram sufficiency

All ordinary two-edge path reports are exchangeable. Conditional on a clean-regime and mask-mixture branch b, they are iid with four-state probability vector R_(h,b). Let c=(c00,c10,c01,c11) be the four-outcome histogram, z the distinguished exceptional pair, and s_(h,b) its conditional probability vector. The exact complete-output likelihood is constant on every ordinary report orbit. Consequently the histogram and special pair are sufficient for the two-world likelihood-ratio test.

The exact joint histogram law is

\[
P_h(c,z)=\frac{n!}{c_{00}!c_{10}!c_{01}!c_{11}!}
\sum_b a_{h,b}\,s_{h,b}(z)\prod_j R_{h,b}(j)^{c_j}.
\]

There are 4 * binomial(n+3,3) histogram+special states, versus 4^(n+1) full outputs. The source uses pure Fraction arithmetic to reconstruct each P_h(c,z), and independently verifies the distribution against complete output convolution for n<=3.

## Exact radical interval

For every rational \(r=p/q\ge0\) and integer scale \(S=10^d\), compute

\[
a=\operatorname{isqrt}(\lfloor pS^2/q\rfloor).
\]

Then \(a/S\le\sqrt r\le(a+1)/S\), with equality detected by checking \(a^2q=pS^2\). Apply the bound to r=P0(c,z)*P1(c,z) at every overlapping histogram state. Summing the rational endpoints gives a certified interval \([L_n,U_n]\) for B_n whose width is at most the count of shared states times 10^(-d). Setting d=22 gives far more precision than needed for whole-number episode-count certificates.

The source also groups latent ordinary-component laws in the infinite-n limit, where the empirical frequencies almost surely identify the distinct four-state R distributions. This defines a separate asymptotic affinity B_infty for comparisons. Because the finite histogram is a statistic of the infinite sequence, B_n>=B_infty. The n25 Hellinger gap remains materially larger than the n25 TV gap to its limiting value.

## Sequential Bayes-risk theorem

Let m complete episodes be conditionally iid given the same hidden world h, with newly sampled vertex labels and newly sampled BM-27 graded masks each time. The m-episode distributions are products of the single-episode law, so their Hellinger affinity is B_n^m. Pointwise min(a,b)<=sqrt(ab) and the classical Hellinger–TV inequality give

\[
\frac{1-\sqrt{1-B_n^{2m}}}{2}
\le R_m^* \le \frac12 B_n^m.
\]

With the certified rational upper endpoint U_n, a sufficient episode count for target Bayes error \(\delta<1/2\) is the smallest integer m satisfying \(U_n^m\le 2\delta\). A binary search with Fraction arithmetic finds this integer exactly, without a numeric logarithm or probability simulation.

At lambda=0, the graded BM-27 eraser makes both output laws equal, B_n=1 exactly and no number of these observations identifies the world. At lambda>0, B_n<1 and repeated independent episodes eventually permit discrimination. These are **pair-specific optimal likelihood-ratio tests** for the registered graded family. FPR-constrained monitors and arbitrary history-adaptive mask selection have distinct guarantees.

## Experimental application

BM-38 measured the weakness of single-episode decoding even with thousands of ordinary paths. The present theorem quantifies why independent episode replication is a more important statistical resource. For n=25 and lambda=1/2, the sufficient number of independent episodes for the upper error guarantee at 5% is on the order of five hundred. At lambda=1 it is on the order of seventy. These are conservative Bhattacharyya upper certificates for the exact finite-n channel, and they do not imply a fixed 5% FPR threshold.

The results provide a synthetic control baseline for Control-Harness and StegoBench. Real model-generated trajectories would require an empirical measurement law and validation of independence/conditional caps. They are outside the mathematical theorem.

## Exact tests

A pure-stdlib verifier checks rational histogram masses, exact radical intervals, monotone finite-n affinity contraction, the infinite-n directing-law limit, explicit error-bound searches, and the zero-signal BM-27 erasure. Independent full-cube regressions cover n<=3. This module introduces no stochastic optimizer, numerical likelihood approximations or external numerical dependency.
