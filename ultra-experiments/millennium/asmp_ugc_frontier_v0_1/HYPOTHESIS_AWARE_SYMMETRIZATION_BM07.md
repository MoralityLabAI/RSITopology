# BM-07: hypothesis-aware symmetrization of gain-cycle Boolean monitors

**2026-11-09 | finite mathematical theorem packet.** This extends [BM-06](ALPHABET_CORRELATED_MINIMAX_BM06.md) by letting a readout attacker select a different correlated mask distribution depending on the true hidden holonomy. Such an attack is expressly outside BM-06's **common hypothesis-blind channel**. The output is a frozen finite-game access theorem, not an analysis of live agent behavior, and its novelty must be assessed against adversarial channel symmetrization and composite hypothesis testing.

## 1. Frozen access contract

Fix an oriented cycle C of length L>=2 (two parallel edges are allowed when L=2), K=F2^s, q=2^s, and one of the two hypotheses H0: Hol(c)=0 or H1: Hol(c)!=0. Each episode draws a **fresh, independent, uniform** vertex labeling in K^V, then emits all L Boolean edge-satisfaction indicators. The monitor sees graph, alphabet and full Boolean output, but cannot inspect labels, numerical nonzero residuals, or hidden holonomy.

The adversary sees H0/H1, the monitor's chosen known edge shift, and the previous transcript. It may use a different distribution Q0 or Q1 on XOR readout masks M in {0,1}^L, even conditioned on the observation history. The mask is independent of the **current** clean edge-satisfaction vector. Each bit's conditional flip probability, under either hypothesis and any permitted history, is at most eta. Noise is allowed to be correlated across the edges within an episode. The intervention itself is externally known and restored accurately; imperfect restoration is the separate BM-05 case.

This threat model is **hypothesis-aware** but **clean-sample-oblivious**. A clean-sample-adaptive adversary or one allowed to change vertex labels directly has a different feasible set.

## 2. BM-07/T1: exact one-shot minimax for a two-edge cycle

Let L=2, with two parallel constraint occurrences. Under a uniform vertex labeling, the clean Boolean satisfaction patterns have exact laws

| observed (X1,X2) | flat H0 | frustrated H1 |
|---|---:|---:|
| (0,0) | 1-1/q | 1-2/q |
| (0,1) | 0 | 1/q |
| (1,0) | 0 | 1/q |
| (1,1) | 1/q | 0 |

Let E denote the mixed-bit event X1!=X2. Under H0, E can occur after readout only when M has odd parity, so

    Pr(E|H0) <= Pr(M odd|H0) <= 2 eta.                (1)

Under H1, the clean probability of E is 2/q, so for p1=Pr(M odd|H1),

    Pr(E|H1) = 2/q + (1-4/q) p1.                     (2)

For q>=4, the coefficient is nonnegative and hence Pr(E|H1)>=2/q. The mixed-event test gives one-shot Bayes error at most (1-2/q+2eta)/2 for eta<1/q.

This is **sharp**. With r=min(eta,1/q), define Q0 and Q1 by

    Q0(00)=1-2r; Q0(01)=Q0(10)=r,
    Q1(00)=1-r;  Q1(11)=r.                            (3)

Every coordinate's flip probability is exactly r. Direct convolution shows

    TV(P0*Q0,P1*Q1) = 2/q-2r.                         (4)

When eta>=1/q the two outputs coincide exactly. The minimax theorem follows from the explicit separating mixed-bit test and the explicit attacking pair: for **equal priors**, the game value is

    min_rule max_(legal Q0,Q1) P(error)
      = [1-max(0,2/q-2eta)]/2,         q>=4.          (5)

For q=2, the analogous sharp construction uses a **common** one-hot mask with Q0=Q1, Q(01)=Q(10)=r, Q(00)=1-2r and r=min(eta,1/4). Its exact minimax TV is max(0,1-4eta).

**Eight-label witness:** q=8, eta=1/8. The flat world uses Q0(00)=3/4, Q0(01)=Q0(10)=1/8; the nonflat world uses Q1(00)=7/8,Q1(11)=1/8. Both observed laws are

    Pr(00)=21/32, Pr(01)=1/8, Pr(10)=1/8, Pr(11)=3/32.

Thus TV=0. Under the hypothesis-blind/common-channel cap, BM-06 instead gives one-shot minimum TV=(2/q)(1-4eta)=1/8. The greater attack power is exactly the *state-dependent channel choice*.

## 3. BM-07/T2: explicit symmetrization on simple cycles of every length

For any L>=2 and q=2^s>=4, define

    D = (q-2)^L + c_L*2^L,
    c_L = q-1 when L is even; c_L=1 when L is odd,
    a = q/D,
    eta_construct = 2^(L-2) a.                        (6)

Construct a flat-world mask Q0 and a nonflat-world mask Q1:

- Q0 gives mass a to **each nonzero mask whose Hamming-weight parity is opposite to L's parity**, and all remaining mass to the zero mask.
- Q1 gives mass a to **each nonzero mask whose Hamming-weight parity agrees with L's parity**, and all remaining mass to the zero mask.

Both have exactly 2^(L-2) masks containing any fixed edge position, so their marginal bit error probabilities are eta_construct. The zero-mask probabilities are nonnegative for q>=4.

**Claim:** the complete masked Boolean observation distributions are exactly equal:

    P0 * Q0 = P1 * Q1,                                 (7)

so the entire output TV is zero even though the connection's holonomy differs. This is an **explicit achievable erasure cap**, with a proven value for this construction. Its global optimality for L>=3 among all legal hypothesis-aware mask laws is an open problem.

### Fourier proof

Let hat denote the Walsh transform on {0,1}^L, with 1 standing for a satisfied edge. For every proper nonempty Walsh-coordinate set S, the corresponding edge subset is acyclic, so the clean bits are independent Bernoulli(1/q) and

    hat P0(S)=hat P1(S)=(1-2/q)^|S|.                 (8)

At the full set S=[L], expanding prod_e (1-2 X_e) gives

    hat P0([L])=[(q-2)^L+(q-1)(-2)^L]/q^L,
    hat P1([L])=[(q-2)^L-(-2)^L]/q^L.               (9)

For the constructed mask distributions, all proper nonempty Walsh coefficients agree, because a sum over one complete mask-parity class vanishes on these Fourier characters (and removing the zero mask changes both channels equally). The common proper coefficient is 1-2^(L-1)a.

At S=[L]:
- If L is even, Q0 has only odd nonzero masks and hat Q0=1-2^L a, while Q1 has even masks and hat Q1=1. Substitute a=q/D from (6) into (9) to obtain hat P0*hat Q0=hat P1*hat Q1.
- If L is odd, Q0 has only even masks and hat Q0=1, while Q1 has odd masks and hat Q1=1-2^L a. Again (6),(9) yield the equality.

At S=empty both transforms are one. Every Walsh transform coefficient of P0*Q0 and P1*Q1 therefore matches, and Fourier inversion proves (7).

### Size of the observation blind spot

| q | cycle length L | eta_construct | common-channel threshold 1/(2L) |
|---:|---:|---:|---:|
| 8 | 2 | 1/8 | 1/4 |
| 8 | 3 | 1/14 | 1/6 |
| 8 | 4 | 1/44 | 1/8 |
| 8 | 5 | 1/122 | 1/10 |
| 16 | 3 | 1/86 | 1/6 |
| 16 | 4 | 1/604 | 1/8 |

For every fixed q>4 the construction approaches

    eta_construct ~ (q/4)*(2/(q-2))^L               (10)

as L grows. This is an exponentially small *sufficient* error rate that erases the entire cycle signal under a hypothesis-aware channel; the common-channel erasure threshold falls only as 1/(2L).

A triangle (L=3) is a simple graph with no parallel edges. At q=8 its Q0 masks assign 25/28 to 000 and 1/28 each to 011,101,110; Q1 assigns 24/28 to 000 and 1/28 each to 001,010,100,111. Both have per-edge flip probability 1/14, and direct convolution gives identical full 3-bit observation laws.

## 4. BM-07/T3: adaptive known-shift tomography can lose all information

Suppose the monitor chooses a known edge shift x_t in K before each episode, and the hidden holonomy is h. Then after shifting the cycle it is flat if h=x_t and nonflat otherwise. An adversary that knows h and observes x_t can choose the mask law Q0 or Q1 from theorem T2. The resulting output distribution R is **identical under every h and every x_t**.

For a monitor choosing x_t adaptively from previous observations, induction on t shows

    Law(transcript | h) = Law(transcript | h')       (11)

for every pair of hidden gains h,h'. Under a uniform prior over q gains, even infinitely many restored interventions and independently resampled observations leave the best exact-h identification success at 1/q. This is a real information-theoretic impossibility *within the declared hypothesis-aware readout interface*. It assumes the adversary can condition on h and the chosen x_t, and that the monitor sees only the corrupted Boolean bits.

## 5. BM-07/T4: a constructive conditional-monitor recovery regime

For the two-edge case q>=4 with eta<1/q, let Y_t be the event that the two observed indicators disagree. Under the conditional noise budget and fresh uniform labelings, even if nature adapts the mask law after each history,

    Pr(Y_t=1 | H0, history) <= a=2eta,
    Pr(Y_t=1 | H1, history) >= b=2/q,                (12)

with b>a. If N observations are taken, declare H1 when at least k of them have mixed bits. Monotone coupling bounds its worst-case false-positive and false-negative probabilities by

    FP <= Pr[Bin(N,a)>=k],
    FN <= Pr[Bin(N,b)<k].                            (13)

These bounds are **sharp for this fixed threshold rule**, attained by the stationary extremal Q0/Q1 pair (3), even though nature is allowed history-dependent masks. A fixed fraction threshold at (a+b)/2 gives the simpler Hoeffding bound

    max(FP,FN) <= exp(-N (b-a)^2/2).                (14)

The code computes the exact binomial thresholds and a legal stationary witness. Example: q=8, eta=1/16, N=31, k=6 yields FP <= 0.183718 and FN <= 0.176416, meeting 20% separate error targets. At eta>=1/q, theorem T1 shows there can be zero information for this target and channel.

The monitoring theorem here certifies flat versus nonflat, with two parallel constraints; turning it into an original-state safety certificate still requires BM-05's independent state-restoration attestation and explicit costs. It also does not prove a general multi-episode minimax optimum for arbitrary decision rules on the complete 2-bit output.

## 6. Implementation and independent checks

- [Two-edge exact minimax oracle](hypothesis_aware_two_edge.py) and [tests](test_hypothesis_aware_two_edge.py): full rational laws, extremal channels, exhaustive small mask-grid search, q=8 erasure witness, adaptive two-action transcript invariance and exact binomial bounds.
- [All-length erasure construction](hypothesis_aware_cycle_erasure.py) and [tests](test_hypothesis_aware_cycle_erasure.py): complete Fourier coefficient equality and independent direct-label enumeration on a q=8 triangle, legal masks through cycle length six and alphabet size 32, and adaptive simple-cycle transcript invariance.
- All code uses Python standard library, deterministic finite arithmetic and a five-minute CPU workflow. There are no GPU/model actions or assumed empirical audit error rates.

## 7. Relation to existing theory and next ASMP-14 theorem

Symmetrizable arbitrarily varying channels and robust hypothesis testing already study state-dependent jamming, channel ambiguity and common-randomness assumptions. In particular, [Modak et al., *Hypothesis Testing for Adversarial Channels: Chernoff-Stein Exponents*, IEEE Transactions on Information Theory 72(7), 2026](https://doi.org/10.1109/TIT.2026.3691175) directly studies deterministic, privately randomized and shared-randomness transmitter strategies. See also [*Detecting Symmetrizability in Physical Systems*, GLOBECOM 2025](https://doi.org/10.1109/GLOBECOM59602.2025.11431861). The exact cycle-specific formulas above are specializations within that mathematical tradition. Novelty must be evaluated against these sources before classifying BM-07 as a standalone ASMP result.

A candidate ASMP-14 admission theorem should characterize the minimax observation/intervention cost for a **frozen policy target** on graph families rather than an isolated cycle, with explicit adversary knowledge (hidden state, chosen shift and readout), potential authenticated private randomness, constrained intervention damage, state-restoration attestations and correlated observations. BM-07 supplies an exact symmetrization obstruction that such a theorem must survive.
