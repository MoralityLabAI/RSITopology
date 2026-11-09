# BM-08: Sharp hypothesis-aware erasure threshold for every binary-vector gain cycle

**10 November 2026 | proposed finite theorem, exact construction and lower bound.**

This closes the optimality question left open in [BM-07](HYPOTHESIS_AWARE_SYMMETRIZATION_BM07.md) for the frozen **two-hypothesis cycle-monitor experiment**. The result is an exact specialization of standard Fourier analysis and adversarial channel symmetrizability, rather than a claim to resolve the full ASMP-14 monitoring problem. The prior BM-07 construction is optimal for q>=8. For q=4 it was generally suboptimal; the correction below is part of the result.

## 1. Access, adversary, objective and theorem

Fix one cycle of length L>=2, including two parallel edges when L=2, with labels in K=F2^s and q=|K|=2^s. A uniformly random labeling is freshly drawn for each observation. Let P0 and P1 be the complete Boolean edge-satisfaction pattern laws when the cycle has respectively zero and a fixed nonzero holonomy. As before, all nonzero holonomies induce the same P1.

Under hypothesis h=0 or 1, the readout adversary chooses a probability distribution Q_h on XOR masks M in {0,1}^L, independently of the **current clean satisfaction vector**. The mask law can depend on h and the monitored system's previously known state and interventions. The per-edge constraint is

    Pr_(M~Q_h)[M_i=1] <= eta,     for all h in {0,1}, i=1..L.

The goal is to find the **smallest uniform eta** such that

    P0 * Q0 = P1 * Q1,                                    (E)

an equality of the entire 2^L-output distributions. Equation (E) makes the passive full-pattern monitor, and any adaptive sequence of known-shift actions when the adversary can choose the matching Q_h after each action, uninformative about this two-hypothesis predicate.

Let

    c_L(q) = q-1 if L is even, and 1 if L is odd,
    D_L(q) = (q-2)^L + c_L(q) 2^L,
    eta_BM07 = q 2^(L-2) / D_L(q),
    eta_common = 1/(2L).

**Theorem BM-08/T1 (exact uniform erasure cost):**

    eta_star(2,L) = eta_common,
    eta_star(4,L) = eta_common,
    eta_star(q,L) = eta_BM07,     q>=8 a power of two.       (1)

Equivalently, for q>=4 the sharp erasure cost is

    eta_star(q,L) = min(eta_common, eta_BM07).              (2)

This theorem concerns equality of **complete single-episode distributions**. It is not a full multi-hypothesis composite minimax theorem for arbitrary noisy live systems; it is precisely the statistical symmetrization threshold for the two signed cycle states. Unchanged alphabet, known graph, fresh uniform labels, correct applied shifts, mask independence from current clean pattern, and per-hypothesis error caps are premises.

## 2. Upper bounds: two explicit achieving channels

**Common one-hot channel (all q).** Draw zero mask with probability 1/2. With probability 1/2 choose exactly one of the L positions uniformly and flip it. Let Q0=Q1 equal that distribution. Each coordinate has flip probability 1/(2L). The mask parity is an unbiased bit, and the clean difference P0-P1 is a single parity Fourier character, so P0*Q0=P1*Q1 exactly.

**Hypothesis-aware BM-07 parity classes (q>=4).** Put a=q/D_L(q). Let Q0 assign mass a to each nonzero mask whose Hamming parity is opposite to L, Q1 assign mass a to each nonzero mask whose Hamming parity equals L, and put the remaining mass at the zero mask in each world. All probabilities are nonnegative for q>=4. Each coordinate is flipped in exactly 2^(L-2) masks of the selected parity class; hence both per-bit marginals equal eta_BM07. Walsh calculations in BM-07 show P0*Q0=P1*Q1.

Equation (2) is therefore an **achievable** upper bound. The following arguments prove it is a lower bound too.

## 3. Complete lower bound for q>=4

### Step 1: Fourier rigidity of the two mask laws

Write chi_S(x)=(-1)^(sum_(i in S) x_i) on the Boolean cube. The clean laws satisfy for every nonempty proper edge subset S

    hat P0(S) = hat P1(S) = (1-2/q)^|S|.                 (3)

Since q>2 this number is nonzero. Taking the Walsh transform of (E) implies hat Q0(S)=hat Q1(S) on every proper S. Both are probability distributions and agree at the empty character too. Fourier inversion therefore forces

    Q0(m)-Q1(m)=c*(-1)^|m|,    for EVERY mask m,        (4)

for a single scalar c, positive, negative or zero.

Put a=|c| and R(m)=min(Q0(m),Q1(m)). Let r be the total R mass on **odd** masks. Every nonzero proper coordinate appears in exactly 2^(L-2) masks of either parity class. By (4), in each Q_h there is forced a mass on exactly one complete parity class, plus the common remainder R. The expected number of flipped bits therefore obeys

    E_Qh |M| >= L * 2^(L-2) * a + r.                  (5)

Because every coordinate has probability of a flip at most eta,

    eta >= 2^(L-2) * a + r/L.                          (6)

This is a universal consequence of the exact output-law equality and the declared noise constraint, regardless of correlation or the number of higher-weight masks.

### Step 2: the full-cycle Walsh equation fixes the forced mass

Set A=hat P0([L]) and B=hat P1([L]). Exact character counting gives

    A = [(q-2)^L+(q-1)(-2)^L]/q^L,
    B = [(q-2)^L-(-2)^L]/q^L.                          (7)

Let p_h=Pr_Qh[|M| odd]. The full-character equality in (E) requires

    A(1-2p0)=B(1-2p1).                                 (8)

First consider any eta < eta_common=1/(2L). A union bound shows p0,p1<=L eta<1/2, so both parity biases 1-2p_h are strictly positive.

For q=4:
- If L is odd, A=-B<0 while B>0. Equation (8) is impossible with positive parity biases.
- If L is even, A>0 and B=0. Equation (8) again requires 1-2p0=0, contradicting p0<1/2.

Therefore eta_star(4,L)>=eta_common. The common one-hot construction attains equality.

For q>=8, L>=2, both A and B are positive. Their strict order alternates with cycle parity: A>B for even L, A<B for odd L. Consequently (8) forces c<0 for even L and c>0 for odd L; the sign says which Q_h carries the forced odd-mask mass. In terms of the common odd mass r from R,

    p0 = r + 2^(L-1)a,   p1 = r,                  (L even)
    p0 = r,              p1 = r + 2^(L-1)a,      (L odd).

Substitute these expressions into (8), using (7). The result in both cases is the exact identity

    a = [q / D_L(q)] * (1-2r).                          (9)

In particular 0<=r<1/2 in the present eta<eta_common regime.

### Step 3: optimize the unavoidable noise mass

Insert (9) into (6):

    eta >= eta_BM07*(1-2r)+r/L
        = eta_BM07 + r*(1/L-2 eta_BM07).                (10)

For all q>=8 (powers of two) and L>=2,

    eta_BM07 <= eta_common.                              (11)

One elementary proof is: t=(q-2)/2>=3, t^2>=q for q>=8, and t^(L-2)>=L/2 for L>=2. Hence t^L>=qL/2, and therefore D_L(q)>=q L 2^(L-1). Rearranging gives (11). Equation (10) now yields eta>=eta_BM07.

If eta>=eta_common, (11) already implies eta>=eta_BM07. Hence the BM-07 construction is globally optimal for all q>=8, including L>=3. No hidden restriction to parity-class or permutation-invariant masks is required: the full proper-Walsh argument (4) covers **every** legal correlated mask law.

### Step 4: binary labels q=2

For q=2, the clean full Boolean pattern supports are the even and odd parity cosets. After masking, their output parity distributions have probabilities 1-p0 and p1 of even parity, respectively (with the appropriate parity convention). Equality of full output laws forces p0+p1=1. The union bound gives p_h<=L eta, so 1<=2L eta, establishing eta>=1/(2L). The common one-hot channel from section 2 attains this value.

This completes BM-08/T1.

## 4. Exact corrections, finite values and interpretation

| q | L=2 | L=3 | L=4 | L=5 | mechanism |
|---:|---:|---:|---:|---:|---|
| 2 | 1/4 | 1/6 | 1/8 | 1/10 | common one-hot |
| 4 | 1/4 | 1/6 | 1/8 | 1/10 | common one-hot |
| 8 | 1/8 | 1/14 | 1/44 | 1/122 | hypothesis-aware parity classes |
| 16 | 1/16 | 1/86 | 1/604 | 1/4202 | hypothesis-aware parity classes |

**Correction to BM-07:** the BM-07 parity-class construction remains a valid *achievable* threshold for q=4, but is not generally optimal: for odd lengths its cap is 1/2, and for even lengths it is 1/4, while the sharp threshold is 1/(2L). For q>=8 the prior values and exponential asymptotic formula are both valid and now proven optimal.

For fixed q>4,

    eta_star(q,L) ~ (q/4) * (2/(q-2))^L,   L -> infinity.

Thus a readout adversary allowed to choose a different mask distribution according to the hidden flat/nonflat state can erase **all** statistical information using a vanishing per-edge budget on long cycles. The threshold describes per-bit readout errors, not the probability of attacking a real monitoring system or an agent's likelihood of reward hacking.

## 5. Reproducibility and independent checks

- [sharp_erasure_optimality.py](sharp_erasure_optimality.py) computes exact sharp thresholds, explicit attaining mask pairs, the correct q=4 branch, clean Walsh coefficients and necessary overlap/noise accounting for arbitrary erasing mask pairs.
- [test_sharp_erasure_optimality.py](test_sharp_erasure_optimality.py) verifies complete masked pattern-law equality and per-bit budget equality for q in {2,4,8,16,32} and lengths 2..7. It checks the q=4 correction, the BM-07 optimality witness for q>=8, the full-Walsh sign conditions, the overlap lower bound and exact nontrivial convex mixtures of erasing channels.
- The preceding BM-07 independent direct-label and Fourier tests remain in [test_hypothesis_aware_cycle_erasure.py](test_hypothesis_aware_cycle_erasure.py).
- An independent symmetric-mask linear program can be written with variables u_j,v_j for weight-j masks under the two hypotheses and eta. The constraints are sum_j u_j=sum_j v_j=1, u_j,v_j>=0, sum_j j*u_j/L<=eta, sum_j j*v_j/L<=eta, and equality of output probabilities for each observed Hamming weight k. Numerical LP checks on q=4,8,16 and small cycle lengths agree with (1), but the proof above is exact and does not depend on numerical optimization.

Run the bounded standard-library suite with the existing 5-minute CPU CI workflow. No gradient training, GPU job, hardware experiment or external authenticated monitor is involved.

## 6. Prior art and next ASMP-14 problem

Walsh-character convolution, biased gain graphs and adversarial-channel symmetrizability are established mathematics. The finite threshold is a cycle-specific exact corollary of those ideas. It requires an independent novelty audit before any publication claim. Relevant references:

- [Modak et al., *Hypothesis Testing for Adversarial Channels: Chernoff-Stein Exponents* (IEEE TIT 2026)](https://doi.org/10.1109/TIT.2026.3691175).
- [Detecting Symmetrizability in Physical Systems (GLOBECOM 2025)](https://doi.org/10.1109/GLOBECOM59602.2025.11431861).
- [O'Donnell, *Analysis of Boolean Functions*](https://www.analysisofbooleanfunctions.org/).
- [Zaslavsky, *Biased Graphs I*](https://doi.org/10.1016/0095-8956(89)90063-4).

The open frontier for **ASMP-14** is now sharper: classify the *joint* minimax monitor/intervention/attestation cost for connected graph families with interacting cycles, with hypothesis-dependent errors conditional on real adaptive histories and explicit externally verified root-state restoration. The one-cycle erasure threshold is a precise negative control any proposed safety certificate must survive. It does not solve that multi-cycle theorem.
