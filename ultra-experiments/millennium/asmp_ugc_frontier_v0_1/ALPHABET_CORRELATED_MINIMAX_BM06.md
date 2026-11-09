# BM-06: alphabet-general robust Boolean monitoring and two-sided error frontiers

**2026-11-09 | finite theorem packet.** This extends [BM-03](FINITE_SAMPLE_MONITOR_BM03.md) and [BM-05](ROBUST_MINIMAX_AND_AUDIT_BM05.md) to *arbitrary label-alphabet cardinalities* in a single episode. The complete noise minimax theorem here assumes one **common hypothesis-blind XOR readout mask distribution**, independent of the current uniformly sampled labeling. The q=2 conditional multi-episode adversarial theorem from BM-05 has a different noise contract. All numerical witnesses are exact rational computations.

## 1. One-dimensional character identity BM-06/T1

Let C be a cycle of length L>=1 in a gain graph over a finite abelian group K, q=|K|>=2. Generate one uniformly random vertex labeling and reveal all Boolean edge-satisfaction indicators X=(X_1,...,X_L). Define P_0 for zero holonomy and P_1 for any fixed nonzero holonomy. For any Boolean pattern x, let k(x) count its unsatisfied edges.

The gain-character count of compatible nonzero residuals, already derived in BM-03, yields

    P_0(x)-P_1(x)=(-1)^{k(x)}/q^(L-1).                  (1)

The right side is a single Walsh character of the Boolean observation space. Every nonzero K-holonomy value gives the same P_1 law. This isolates exactly the part of the passive Boolean observation that depends on whether the cycle is balanced.

Now let M be an arbitrary {0,1}^L-valued error mask, independent of X and governed by the *same* known or unknown distribution under both hypotheses, and observe Y=X XOR M. Define p=Pr[parity(M)=odd]. Since the Walsh parity character is an eigenvector of convolution by M,

    P_0^M(y)-P_1^M(y)
       = (-1)^{k(y)}/q^(L-1) * E[(-1)^{|M|}]
       = (-1)^{k(y)}/q^(L-1) * (1-2p).                 (2)

Summing half the absolute differences over all 2^L patterns gives the **exact full-data total variation**

    TV(P_0^M,P_1^M)
       = (2/q)^(L-1) * |1-2p|.                       (3)

The formula holds for arbitrary within-episode correlations and for nonexchangeable masks. It concerns the **entire Boolean pattern**; reducing it to parity yields the same optimal equal-prior *one-shot* decision when p<=1/2. For multi-episode likelihood multiplication, the full failure count can carry extra information and must be retained for the optimal test.

## 2. Sharp per-edge-cap minimax theorem BM-06/T2

Freeze caps eta_i in [0,1] with the noise law satisfying Pr[M_i=1]<=eta_i. Let s=sum_i eta_i. A mask of odd parity has at least one flipped coordinate, hence

    p <= min(1,s).

A lawful mask distribution with p_star=min(s,1/2) is built by choosing the all-zero mask with probability 1-p_star and choosing a one-hot error at coordinate i with probabilities p_i<=eta_i summing to p_star. Therefore the **minimum possible full-pattern TV** over this hypothesis-blind mask class is

    TV_min=(2/q)^(L-1) * max(0,1-2s).                (4)

The one-shot uniform-prior minimax Bayes error is

    R_1^*=[1-TV_min]/2.                               (5)

To prove the game minimax equality: if s<1/2, then p<1/2 for every legal mask and the fixed parity decision 'flat for even unsatisfied count, frustrated for odd' is Bayes optimal for **each** common mask distribution by (2). Its largest equal-prior risk is attained by the one-hot mask distribution and equals (5). If s>=1/2, the one-hot construction with p=1/2 makes P_0^M=P_1^M, so no decision rule improves on a fair-coin decision and the minimax risk equals 1/2.

These are classical Fourier convolution and union-bound facts combined in the declared gain-cycle experiment, serving as exact monitoring baselines. No general result about real AI systems follows without verified sampling, alphabet access and noise-law contracts.

**Examples:**
- q=4, L=3, caps (1/8,0,1/16): TV_min=5/32 and R_1^*=27/64.
- q=8, L=3, caps (1/8,1/8,1/8): TV_min=1/64 and R_1^*=63/128.
- q arbitrary, L=4, caps all 1/8: TV_min=0, so independent active-recovery strategies require a stronger readout or error assumption.
- Clean source cap eta_i=0 recovers the earlier TV=(2/q)^(L-1).

The executable [alphabet-general noisy-channel oracle](alphabet_correlated_channel.py) cross-checks arbitrary rational mask laws by direct full-pattern convolution. [Tests](test_alphabet_correlated_channel.py) exhaust all rational mask distributions on two bits with denominator six, verify 12 seeded masks per (L,q) for L<=5 and q in {2,3,4,8}, check heterogeneous cap allocations and emit the exact erasure witness.

## 3. Simultaneous false-positive and false-negative obligations

ASMP-14's declared certification target requires a **composite error region**, not merely equal-prior Bayes performance. For one randomized *parity-only* decision rule, let a=Pr[declare nonflat|observed even parity] and b=Pr[declare nonflat|observed odd parity]. With e_j(p)=Pr[observed even parity|H_j,parity-mask rate p], the conditional errors are

    FP(p) = a e_0(p)+b(1-e_0(p)),
    FN(p) = (1-a)e_1(p)+(1-b)(1-e_1(p)).             (6)

The clean values e_j(0) are exact cycle character sums and

    e_j(p)=e_j(0)(1-p)+(1-e_j(0))p.

For the registered common error-mask class p ranges over [0,p_max], with p_max=min(1,sum_i eta_i). Every p in that interval is realizable by a zero/one-hot mixture, so the exact worst conditional errors of a given parity-only rule are the maxima at **p=0 and p=p_max**. Both inequalities FP<=alpha and FN<=beta are linear in (a,b), defining an exact 2D convex polygon intersected with [0,1]^2. The independent [rational polygon feasibility oracle](alphabet_correlated_channel.py) enumerates line-pair intersections to return a randomized test or a definite infeasibility result *within the parity-only decision class*.

The p_max check matters when s>1/2. Although the equal-prior minimax adversary erases information already at p=1/2, legal masks can achieve larger odd parity rates, reversing the preferred parity label for a deterministic decision. The exact composite region must include those errors.

### Clean q=8,L=3 example: two-sided risk exposes extra information

The clean distribution of the count k of unsatisfied edges is

    flat:       (1/64,0,21/64,21/32),
    frustrated: (0,3/64,9/32,43/64).

Even-parity probabilities are 11/32 (flat) and 9/32 (frustrated). The equal-prior Bayes-optimal parity rule declares flat for even and frustrated for odd and achieves average error 15/32. Its **separate** conditional errors are FP=21/32 and FN=9/32, making it unsuitable for a symmetric safety/error gate.

If the monitor is restricted to randomized parity-only rules, the best symmetric worst-hypothesis error is 21/44, attained by a=0 and b=8/11. The exact robust-parity polygon reports that simultaneous caps alpha=beta=15/32 are infeasible.

If the monitor retains the **full failure count k** under this clean law, a randomized Neyman-Pearson likelihood-ratio test achieves the strictly smaller symmetric minimax risk

    R_clean_composite=1281/2720.                      (7)

The test declares nonflat for k=1, flat for k=0 or 2, and randomizes with probability 61/85 for k=3. Its false positive and false negative rates both equal 1281/2720. A separate **dual optimality certificate** takes the weighted error multiplier lambda=43/85 and proves that every randomized count-based decision rule has maximum error at least

    sum_k min(lambda*p_flat(k),
              (1-lambda)*p_frustrated(k))=1281/2720. (8)

The exact [composite decision module](composite_cycle_decision.py) computes both primal and dual witnesses and tests them across q in {2,3,4,8,16}, L=1..5. This demonstrates an important distinction: one-shot parity is Bayes optimal for equal priors but can discard information needed to enforce asymmetric or separate worst-hypothesis error bounds.

This count-based clean solution is a Neyman-Pearson theorem application. It is not an optimal full-pattern test under unknown correlated masks; that robust composite frontier remains open.

## 4. A necessary noise-contract counterexample

Common-channel noise independence is load-bearing. If nature chooses a *different* mask law after seeing the true hypothesis, even the fixed parity decision above can fail catastrophically. At q=8,L=3, caps 1/8 per bit, let the flat world use the zero mask and the frustrated world use the one-hot extremal mask. Both individually satisfy the cap, but the parity test that is optimal in the common-channel model has **equal-prior error 141/256 > 1/2**. In the common-channel class, its certified minimax error is only 63/128. The new negative test verifies these exact probabilities.

A broad safety guarantee must therefore freeze whether the adversary's observation channel is hypothesis-blind and shared, or hypothesis-dependent after seeing the state. The BM-05 binary conditional multi-episode theorem has its own stronger adversarial contract and must be applied with its original assumptions.

## 5. Forward ASMP-14 target

The next difficult mathematical step is to characterize the **entire** joint error region under hypothesis-dependent, adaptive and correlated readout masks, with intervention shifts chosen from a charged strategy class and independently verified restorations. Its certificate should distinguish:

- equal-prior Bayes risk from worst-case per-hypothesis false-positive/false-negative rates;
- common-channel and hypothesis-dependent noise classes;
- one-episode exact Fourier identities and multi-episode interactive hypothesis testing;
- a known applied shift from unverifiable latent restoration drift.

Such a result would connect the exact noisy-gain-cycle statistics to ASMP-7's transformation-closed attestation and ASMP-14's prospective active oversight frontier. Novelty must be judged against Fourier analysis on the Boolean cube and classical Neyman-Pearson/robust sequential experimental design, rather than the elementary identities proved here.

## Primary antecedents

- [Zaslavsky, Biased graphs. I. Bias, balance, and gains (1989)](https://doi.org/10.1016/0095-8956(89)90063-4).
- [Ryan O'Donnell, Analysis of Boolean Functions](https://www.analysisofbooleanfunctions.org/), particularly Walsh characters and noise operators.
- [Polyanskiy and Wu, Information Theory chapter on Neyman-Pearson tests](https://people.lids.mit.edu/yp/homepage/data/itbook-export.pdf).
- [RSITopology ASMP-9 reward-gauge source](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/asmp9_reward_gauge_census/README.md).

No model weights, GPU budget, behavioral transcript, or trusted actuation is touched by this work.
