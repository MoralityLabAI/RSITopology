# BM-39: Exact finite-n distinguishability of the graded BM-27 eraser

**11 November 2026 | exact all-n TV formula for one explicit attacker family**

The prior BM-37 theorem proves a positive, conservative total-variation lower bound for matched-marginal correlated masks with a per-bit budget below the erasure frontier. BM-39 solves a **specific registered family exactly**: the BM-27 zero-TV hypothesis-aware eraser mixed with an unmasked report with probability lambda.

## Theorem

For any integer n>=1, define q8 clean output laws P0,P1 over n ordinary gain-zero two-edge paths and one exceptional gain-switched path. Let the graded world-aware XOR noise be Qh(lambda)=(1-lambda)Qh(BM27)+lambda*delta_zero, 0<=lambda<=1. BM-27 proves its full masked output law E is identical in both worlds. The graded outputs obey

P_h(lambda) = (1-lambda)*E + lambda*P_h(clean).

Then the EXACT complete-output total variation is

\[
\boxed{TV(P_0^\lambda,P_1^\lambda)=\frac{\lambda}{16}\left(1-\left(\frac34\right)^n\right).}
\]

This is valid for every finite n, without approximation, independent numeric optimization or asymptotic exchangeability assumptions. The per-bit readout flip cap of the explicit channel is (1-lambda)*5/52.

## Elementary proof

Let A=(7/8,0,0,1/8) and B=(3/4,1/8,1/8,0) be the two possible clean two-edge path output laws (tuple order 00,10,01,11). BM-27 supplies the exact clean mixtures:

P0(clean) = (1/8) A^tensor(n) tensor A + (7/8) B^tensor(n) tensor B.

P1(clean) = (1/8) A^tensor(n) tensor B + (1/8) B^tensor(n) tensor A + (6/8) B^tensor(n) tensor B.

Subtract and factor:

\[
P_0^{clean}-P_1^{clean}
=\frac18(A^{\otimes n}-B^{\otimes n})\otimes(A-B).
\]

Because A and B put positive mass on common pair outcomes only at 00, the product laws A^tensor(n) and B^tensor(n) overlap only at the all-00 sequence. Its masses are (7/8)^n and (3/4)^n respectively, so their overlap is (3/4)^n and TV(A^tensor(n),B^tensor(n))=1-(3/4)^n. Meanwhile TV(A,B)=1/4.

The L1 norm of a tensor product of signed measures equals the product of their L1 norms. Thus

TV(P0(clean),P1(clean)) = 1/16*(1-(3/4)^n).

Since the two BM-27 masked output laws are identical for every n, the graded output difference is lambda times the clean difference, completing the theorem.

## Statistical consequences and scope

The optimal equal-prior Bayes decision risk for one graded episode is exactly

\[
R^*=\frac12-\frac{\lambda}{32}\left(1-\left(\frac34\right)^n\right).
\]

For ANY randomized or deterministic monitor in this family and a declared **population** false-positive rate alpha,

\[
TPR \le \alpha + \frac{\lambda}{16}\left(1-\left(\frac34\right)^n\right).
\]

At lambda=1/2, limiting TV is 1/32=3.125%. Even the best detector cannot exceed 8.125% TPR at 5% population FPR in one episode. This differs from a finite held-out estimate of FPR, which is subject to sampling uncertainty.

Seventeen ordinary paths already yield more than 99% of the limiting TV, while increasing n beyond 25 changes the ceiling by less than 0.1%. This **saturation** is caused by the exceptional two-edge path remaining noisy after ordinary-path replication has nearly identified the latent clean regime. It motivates reducing graph size and enlarging independent episode counts for Control-Harness experiments.

At each cap eta in [0,5/52], set lambda=1-eta/(5/52). The formula gives an **attacker-achievable upper bound** on the minimum possible TV over all adversaries because the displayed graded channel is legal. There is no claim that this family minimizes TV at each cap. The all-mask question from BM-37 remains open. The theorem does not address deployed model monitoring.

## Verification

The pure-Fraction source exact_graded_visibility_BM39.py verifies BM-27's all-n convolution identity and the four-state support factors, computes the exact rational family TV for arbitrary n and lambda, and exposes the Bayes-error and population-TPR bounds. Independent tests enumerate full clean and masked output distributions for n=1,2,3 and five lambda values, check the original n=2 7/256 and 7/512 results and the 17-path 99%-saturation threshold, and inspect the explicit budget curve. An exact formula for a fixed family is a mathematical derivation, not a newly certified adversarial minimax theorem.
