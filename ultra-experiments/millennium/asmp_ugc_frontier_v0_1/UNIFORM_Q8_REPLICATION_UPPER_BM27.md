# BM-27: Uniform hypothesis-aware erasure at 5/52 on growing q=8 theta graphs

> **Subsequent result, BM-29 (10 November 2026):** [The exact infinite-replication theorem](INFINITE_REPLICATION_LIMIT_BM29.md) proves **lim_n eta_n(8,2)=5/52** in the registered hypothesis-aware, current-clean-independent readout model. The open-limit statements below record the historical status before BM-29. Finite-n sharp formulas for n>=4 and a quantitative convergence rate remain open.


**10 November 2026 | exact infinite-family UPPER theorem, finite algebraic proof and independent controls.** This advances the limiting-cost question after [BM-26's exact q=8 third-replica threshold](THREE_REPLICA_Q8_BM26.md). It gives a **uniform upper bound strictly below the common-channel optimum**, valid with arbitrarily many repeated observation paths, using a finite signed-convolution identity and legal nonnegative mask laws.

The construction is exact under the registered observation and attacker contracts. It does **not** determine the asymptotic optimum: an independent lower-bound sequence approaching 5/52 is still required before a limiting-value theorem can be claimed. The group convolution and mixture manipulations are elementary finite probability mathematics.

## 1. Statement and two-bit clean building blocks

Let K=F2³, q=8. The graph has n>=1 ordinary two-edge paths between common terminals u,v and one exceptional two-edge path. The ordinary path gains equal zero in both worlds. The exceptional path's gain is zero in the flat world and a fixed nonzero gamma in the frustrated world. Each observation episode samples independently uniform vertex labels, and reveals only the complete Boolean vector of edge satisfaction reports.

The adversary can choose one **correlated readout-mask distribution under each hidden hypothesis**, independently of the *current clean report*. Every individual edge's mask-flip probability is capped by eta. The objective eta_n(8,2) is the smallest eta making the masked complete-output laws identical.

**BM-27/T1: a uniform erasure upper bound for every n>=1,**

    eta_n(8,2) <= 5/52 = 0.0961538461538... .          (1)

The existing BM-24 common-channel construction costs exactly 1/8=0.125. The new hypothesis-aware construction improves that universal upper budget by

    1/8 - 5/52 = 3/104,

a relative reduction of 3/13, approximately 23.08%.

Write a Boolean *pair* distribution as a vector ordered by masks (00,10,01,11). For a fresh uniformly sampled two-edge path, conditional on the shared terminal difference d, the satisfaction pair law is:

    A = (7/8, 0,   0,   1/8)   when d equals the path gain,
    B = (3/4, 1/8, 1/8, 0)    when d differs from the path gain.

These vectors also define legal XOR **noise** distributions, each having individual-bit flip probability 1/8. Define two more distributions:

    I = (1,   0,   0,   0)    zero noise,
    E = (1/2, 1/4, 1/4, 0)  unbiased one-hot parity eraser.

E has marginal flip probability 1/4 on either bit. Let * be XOR convolution of two pair distributions, let tensor denote independent path products, and put A_n=A^(tensor n), B_n=B^(tensor n), I_n=I^(tensor n).

Uniform endpoint differences give the exact clean probability laws

    P0 = (1/8) A_n tensor A + (7/8) B_n tensor B,
    P1 = (1/8) A_n tensor B
       + (1/8) B_n tensor A + (6/8) B_n tensor B.      (2)

The formulas follow by splitting the terminal difference into d=0, d=gamma and the other six values. Each ordinary path shares the same conditional A/B type but has independent internal labels given d.

## 2. Four tiny nonnegative noise components per ordinary regime

Define the following **world-specific masking laws**, where each term is a proper tensor-product probability distribution. Their coefficients are probabilities; each column sums to 13 before normalization.

| World h=0: flat | Mixture mass |
|---|---:|
| I_n tensor E | 3/13 |
| A_n tensor I | 1/13 |
| A_n tensor E | 1/13 |
| B_n tensor I | 6/13 |
| B_n tensor A | 2/13 |

| World h=1: frustrated | Mixture mass |
|---|---:|
| I_n tensor E | 3/13 |
| A_n tensor A | 2/13 |
| B_n tensor I | 6/13 |
| B_n tensor B | 2/13 |

Call these mask laws Q0 and Q1. **Within each mixture branch**, choose its ordinary mask pair independently on all n ordinary paths, using the same pair law A, B or I in each path. Choose the exceptional path's mask from I, A, B or E as indicated. This uses only the fixed 5/4 branch mixture and O(n) independent pair draws; there is no need to materialize the full 2^(2n+2) mask space.

### Exact marginal cost

A and B flip either given bit with probability 1/8, E with probability 1/4, and I with probability zero.

In both worlds the total mixture mass spent on ordinary mask distributions A_n or B_n is 10/13. Therefore **every ordinary edge** has readout flip probability

    (10/13)*(1/8) = 5/52.                              (3)

In world h=0, the exceptional mask is E with total mass 4/13 and A with mass 2/13; its bit marginal is

    (4/13)*(1/4) + (2/13)*(1/8) = 5/52.

In world h=1, the exceptional mask is E with mass 3/13 and A/B with total mass 4/13; its bit marginal is again

    (3/13)*(1/4) + (4/13)*(1/8) = 5/52.              (4)

Every component is nonnegative, normalized and chosen independently of the current clean sample, so both world-specific masks satisfy the registered threat contract.

## 3. Formal convolution identity (the entire all-n upper proof)

The crucial exact pair identities are

    E = 2B-I                                        (5)

as an equality of signed measures (the left is itself a legal
nonnegative distribution), and

    A*E = B*E.                                      (6)

The second identity holds because A and B have the same single-bit Walsh coefficients and E has zero full-pair Walsh coefficient. It can also be verified directly from all four entries:

    A*E = B*E = (7/16, 1/4, 1/4, 1/16).

Using distributivity and commutativity of XOR convolution, expand P0*Q0 and P1*Q1 from (2). For **ordinary paths**, each term is one of exactly five formal components:

    A_n, B_n, (A*A)^(tensor n),
    (A*B)^(tensor n), (B*B)^(tensor n).

(The pairwise * is applied independently at every ordinary path; tensor powers are taken afterward.) Group the output by these five components, retaining the exceptional two-bit distribution as its coefficient. The following equality is checked component-by-component, with common global denominator 104:

| Ordinary output component | P0*Q0 exceptional coefficient, numerator | P1*Q1 exceptional coefficient, numerator |
|---|---|---|
| A_n | 3(A*E) | 3(B*E) |
| B_n | 21(B*E) | 3(A*E)+18(B*E) |
| (A*A)^n | A+(A*E) | 2(A*B) |
| (A*B)^n | 6A+2(A*A)+7B+7(B*E) | 6B+2(B*B)+2(A*A)+12(A*B) |
| (B*B)^n | 42B+14(A*B) | 6A+36B+2(A*B)+12(B*B) |

Every row agrees exactly using (5) and (6). For example (5) gives A+(A*E)=2(A*B); (6) gives the cancellation relation 2(A*B)-A=2(B*B)-B. The other rows reduce to the same identities.

Therefore P0*Q0=P1*Q1 as formal tensor-power distributions for **every positive integer n**, proving the full output law equality without large-n approximation. Equations (3)/(4) establish the claimed per-edge upper budget (1).

The [executable BM-27 proof](replication_uniform_upper_BM27.py) checks every signed pair identity, all five exceptional coefficients and all marginal sums with exact `Fraction` arithmetic. This avoids an inference based only on high-order moment matching or finite pilot extrapolation.

## 4. Independent finite and symbolic verification

The [BM-27 independent regression suite](test_replication_uniform_upper_BM27.py) verifies:

- The clean conditional-mixture law (2) against the prior complete **uniform vertex-label census** on n=1,2,3, including both hypotheses.
- Each complete reported-output probability after direct XOR convolution of **independently expanded** world-dependent masks and clean laws, for n=1..4. The masks differ between worlds and each of their 2n+2 edge marginals is exactly 5/52.
- The BM-24 exact *path-histogram quotient* Fourier equalities for n=1..4, providing a separate independent verification method from the five-component formal expansion.
- Exact signed-convolution identities, branch normalization, equality of all five ordinary coefficient groups, malformed input rejection and deterministic small-branch sampling on n=250.
- The strict upper improvement over BM-24's 1/8 common mask and compatibility with BM-08, BM-25 and BM-26's sharper finite thresholds.

The large n test evaluates the **constant-size proof** at n=250 and n=1000 without constructing a clean full law, Fourier support table or readout mask distribution over the exponentially many complete bit vectors.

## 5. Improved asymptotic bracket and the remaining lower theorem

BM-26 proves the sequence eta_n(q,L) is nondecreasing: projecting a successful n+1-instance readout equalizer onto n ordinary paths gives a legal n-instance equalizer with the same per-bit cap. Therefore eta_n(8,2) has a limit.

The exact BM-26 third-replica lower result and this uniform upper construction now imply

    751225/13956626 <= eta_infinity(8,2) <= 5/52.  (7)

The corresponding decimal bracket is approximately

    0.0538256882 <= eta_infinity <= 0.0961538462.

Earlier exploratory finite LP solutions at n=10,12,14,16 (approximately 0.09206, 0.09346, 0.09437, 0.09488) approach 5/52 from below. Their precise values remain uncertified; they serve as motivation for an analytic **lower certificate approaching 5/52**, which has not yet been constructed.

**Candidate BM-27/C1:** for q=8,L=2 under the registered full hypothesis-aware correlated readout interface,

    lim_(n->infinity) eta_n(8,2) = 5/52.

The upper half is now proven. The lower half requires a uniform-in-n dual family or an exact infinite-exchangeability/mixture characterization, with a constructive finite degree approximation argument and rigorous rational error control. Numerical convergence alone cannot certify this claim.

The next useful proof strategy is to exploit conditional de Finetti mixing of the ordinary masks and the fact that the two worlds have the same marginal ordinary readout-mask distribution. The ordinary path distributions A and B have identical one-bit marginals and different pair-parity moments. The exceptional readout requires coupling those ordinary mask components differently under the two hypotheses. The finite convolution construction shows the effective tradeoff, while a new lower theorem must quantify its unavoidable cost over **all** legal mask distributions, rather than only the five-component family.

## 6. Prior art and scope

This result uses elementary XOR-group convolution, finite mixtures and exchangeable repeated observations. The underlying mathematics belongs to classical adversarial-channel symmetrizability and Fourier analysis. Relevant background: [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/), [Modak et al., *Hypothesis Testing for Adversarial Channels* (2026)](https://doi.org/10.1109/TIT.2026.3691175), and the prior BM-24–26 experiment notes.

The theorem is an exact **sufficient erasure construction** for a frozen adversary who knows the hidden hypothesis but cannot condition the mask on the current clean observation. It does not imply an optimal asymptotic value, a safety theorem about deployed AI systems, verified intervention/root restoration or a solution to the Unique Games Conjecture.
