# BM-03: exact finite-sample risk for noisy Boolean cycle monitoring

**Research addendum, 2026-11-09.** Status: exact finite statistical experiment and familiar hypothesis-testing bounds, with exhaustive independent checks. Related sources: [BM-01 observable quotient](BOOLEAN_MONITOR_QUOTIENT_BM01.md), [BM-02 active edge interventions](ACTIVE_PROBE_RECOVERY_BM02.md), [sharp clean single-shot TV](SHARP_VISIBILITY_AND_DECODING_BOUNDS.md), and the [provisional ASMP-14 candidate](CANDIDATES.md). This is an exact calculation inside a declared mathematical monitor grammar; it supplies no claim about trained AI monitors or physical intervention reliability.

## 1. Frozen experiment and sufficiency

Take one length-L cycle, an alphabet K=F2^s of cardinality q>=2, and one fixed connection whose holonomy is either zero (H0) or any nonzero element (H1). For each observation episode, draw a fresh independent uniform vertex labeling in K^V and emit the full Boolean vector of satisfied/unsatisfied edges. Each reported bit is optionally passed through an independent binary symmetric readout channel with known flip probability eta in [0,1]. The hidden connection, the graph and q are held fixed across episodes. The monitor receives neither the vertex labels nor the numerical nonzero residuals.

For any exact Boolean pattern with k unsatisfied edges, character orthogonality gives the number of compatible cycle residuals

    n0(k)=((q-1)^k+(q-1)(-1)^k)/q,        if flat;
    n1(k)=((q-1)^k-(-1)^k)/q,            if nonflat.

Each individual pattern has probability n_i(k)/q^(L-1). Thus its likelihood ratio depends only on k. The complete pattern can be replaced by the **failure count K** without losing any information for this pair of hypotheses.

Before readout noise, the exact count distribution is

    p_i(k)=choose(L,k) n_i(k)/q^(L-1).

With independent flips at rate eta, conditioned on j true failures, the noisy failure-count probability is

    T_eta(k|j)
      = sum_u choose(j,u) (1-eta)^u eta^(j-u)
             choose(L-j,k-u) eta^(k-u) (1-eta)^(L-j-k+u),

where max(0,k-(L-j)) <= u <= min(j,k). The noisy count law is
p_{i,eta}(k)=sum_j p_i(j)T_eta(k|j). Exchangeability is preserved, so k remains a sufficient observation under this declared **iid** bit-noise channel.

For N independent episodes, the histogram h_k of the N observed counts is sufficient and has the multinomial likelihood

    P_i(h)=N! / prod_k h_k! * prod_k p_{i,eta}(k)^h_k,
    with sum_k h_k=N.

Therefore the **exact optimal equal-prior Bayes error**, allowing randomized ties, is

    R_N^*(q,L,eta)= (1/2) sum_{h:sum h=N} min(P_0(h),P_1(h)).    (1)

This is computable by finite rational arithmetic on choose(N+L,L) histograms. It is an exact statistical optimum in the frozen model, not a general AI-audit sample bound. For a prescribed alpha<1/2, the least N with R_N^*<=alpha is its optimal fixed-sample count.

## 2. Binary parity channel: exact risk and sharp scaling

When q=2, the clean full-cycle laws are uniform on opposite parity cosets. Let

    t=|1-2 eta|^L.

Under H0 one appropriately oriented observed parity bit has mean +t; under H1 its mean -t. Every other detail of the full Boolean vector is ancillary for distinguishing these two hypotheses. For N independent episodes the optimal test compares the count S of favorable parity signs to N/2, with half-weighted randomization on ties. Thus

    S ~ Bin(N,(1+t)/2) under H0,
    R_N^* = Pr(S<N/2)+(1/2)Pr(S=N/2).                         (2)

The per-episode Hellinger affinity is exactly sqrt(1-t^2); the N-fold affinity is (1-t^2)^(N/2). The standard TV-affinity inequality yields

    TV(P0^N,P1^N) <= sqrt(1-(1-t^2)^N).

Consequently any method with equal-prior Bayes error at most alpha<1/2 requires

    (1-t^2)^N <= 4 alpha (1-alpha),
    N >= log(4 alpha (1-alpha))/log(1-t^2)                     (3)

when 0<t<1. In contrast, the majority test and Hoeffding yield

    R_N^* <= exp(-N t^2/2).

Together they prove the **fixed-confidence rate**
N=Theta(t^-2)=Theta(|1-2eta|^(-2L)) in the low-signal regime. This sharpens the earlier coupling-only necessary bound Omega(t^-1) for independent repetitions. When eta=1/2, t=0 and no number of observations distinguishes the two hypotheses; when eta=0 or 1, a single full-cycle parity is decisive.

### Exact frozen numerical witness

For L=4, q=2, eta=1/4, target Bayes error alpha=1/3:

    t=1/16;
    the Hellinger necessary sample count is 31;
    the exact first N at which the optimal Bayes error is <=1/3 is 47.

A 30-sample method necessarily exceeds target by the Hellinger argument. The 46-sample exact optimal test also exceeds target, while the 47-sample optimal majority test attains it. Tests verify the exact probabilities using rational arithmetic. The proof that the 47 threshold is minimal uses monotonicity of optimal risk under sample discard.

## 3. Multi-label exact optimal tests and one-sided probe cost

At q>2 the full Boolean observation remains count-sufficient for the binary **flat/nonflat** task, even though it cannot identify which nonzero holonomy is present. Formula (1) computes exact multi-episode risk without enumerating q^L vertex states. For q=4,L=4,eta=0:

| episodes N | exact Bayes error |
|---:|---:|
| 1 | 7/16 = 0.4375 |
| 2 | 205/512 = 0.400390625 |
| 3 | 24409/65536 = 0.37245178 |
| 5 | approximately 0.32485586 |
| 8 | 581854902983/2199023255552 = 0.26459698 |

In this example, N=5 is the first fixed sample count with equal-prior error at most 1/3. The BM-02 one-sided all-satisfied detection protocol is useful for *certifying equality of a candidate intervention*; its Bayes error under equal priors after eight shots is (1/2)*(63/64)^8, much larger than the optimal full-pattern likelihood test. This quantifies what the stronger observation processing purchases **without changing physical access**.

The optimal fixed-N likelihood test addresses the two hypotheses H0 and H1 with one chosen intervention. Recovering an unknown numerical h from several active candidate shifts x and controlling a **family-wise** error rate is a separate sequential/multi-hypothesis problem. The q-1 ideal equality-query worst-case bound from BM-02 does not imply that q-1 noisy Boolean episodes suffice.

## 4. Correlation and source-validity controls

At q=2,L=4, when the readout flips **every** bit together with probability 1/2, parity remains exact and the full-cycle observation laws have TV=1. Under independent flips at probability 1/2, their TV is zero. Both have marginal per-bit flip probability 1/2. Thus the iid/noise-correlation class is an essential part of the sampling theorem.

The monitor must specify whether the same hidden connection persists, whether labelings are independently refreshed, whether the intervention's shift is exact and externally bound, and whether enough edge indicators are jointly observed to calculate a cycle parity. Errors from repeated or adversarially correlated labels require a new experiment.

## 5. Executable checks

- [finite_sample_monitor.py](finite_sample_monitor.py) computes cycle failure-count laws, exact iid noise convolution, multinomial-optimal Bayes risk, the closed binary parity binomial risk and the exact Hellinger necessary sample threshold.
- [test_finite_sample_monitor.py](test_finite_sample_monitor.py) independently aggregates complete pattern laws, applies the earlier full-pattern bit channel, checks two-shot exhaustive likelihoods, reproduces q=4,L=4 multi-shot rational risks, validates exact binary majority risk and a correlated-noise null.
- Run: python -m unittest discover -s ultra-experiments/millennium/asmp_ugc_frontier_v0_1 -p 'test_*.py' -v
- The path-gated five-minute CPU workflow and exact-claim boundary are preserved.

## 6. Prior art, further research and ASMP admission

Le Cam/Bhattacharyya hypothesis-testing bounds, parity transmission under binary symmetric channels, Neyman–Pearson testing and sufficiency of exchangeable count statistics are established mathematics. See [Canonne, Assouad and Le Cam lower bounds](https://www.cs.columbia.edu/~ccanonne/files/misc/2015-assouadlecam.pdf) and [Zaslavsky's biased graphs](https://doi.org/10.1016/0095-8956(89)90063-4).

The potential **ASMP-14 novelty** is to classify the *uniform adaptive monitoring frontier* for costed access to nonlocal graph constraints when the monitor must simultaneously choose interventions, pay for joint observations, authenticate state restoration, tolerate correlated readout noise and maintain a live safety/performance criterion. BM-03 supplies a sharp baseline for one fixed cycle and iid noise. It establishes no broader minimax theorem or human/model safety property.
