# BM-28: A certified 16-replica lower bound for the q=8 masking limit

> **Subsequent result, BM-29 (10 November 2026):** [The exact infinite-replication theorem](INFINITE_REPLICATION_LIMIT_BM29.md) proves **lim_n eta_n(8,2)=5/52** in the registered hypothesis-aware, current-clean-independent readout model. The open-limit statements below record the historical status before BM-29. Finite-n sharp formulas for n>=4 and a quantitative convergence rate remain open.


**10 November 2026 | exact rational dual lower certificate with a frozen integer witness.**

This strengthens the q=8 replication-limit problem following [BM-26](THREE_REPLICA_Q8_BM26.md) and the new [BM-27 all-n 5/52 upper construction](UNIFORM_Q8_REPLICATION_UPPER_BM27.md). It establishes a sharp *interval* for the infinite-replication value by certifying a far stronger finite-n lower bound using only exact integer arithmetic at verification time. The n=16 **optimum itself is not claimed exact**.

## 1. Registered observation and adversary

Let K=F2³, q=8. There are **16 ordinary two-edge u-v paths** with path gain zero under both hidden hypotheses, and one exceptional two-edge path whose gain changes from zero to a fixed nonzero element. The graph has 19 vertices and 34 Boolean edge-satisfaction reports. Each observation episode samples fresh independent uniform vertex labels.

A world-aware adversary may choose one correlated XOR mask distribution under each hypothesis. Each mask remains independent of the current clean report; every bit has flip probability at most eta. The exact full-output erasure threshold for n ordinary paths is eta_n(8,2).

**BM-28/T1 (verified lower certificate):**

    eta_16(8,2) >= 4743879/50000000 = 0.09487758.     (1)

BM-27 provides the rigorous upper eta_n(8,2)<=5/52 for every n. Projection from larger n onto the 16-ordinary-path instance gives eta_n>=eta_16 for every n>=16. The monotone limit exists by BM-26, so the rigorous asymptotic bracket is now

    4743879/50000000
       <= eta_infinity(8,2)
       <= 5/52.                                         (2)

The exact interval width is

    5/52 - 4743879/50000000
      = 829573/650000000
      ≈ 0.001276266154.                                (3)

On the percentage scale, this is approximately **9.487758% to 9.615385%**, a gap of 0.127627 percentage points. The lower bound is a verified rational LP dual; the upper bound is BM-27's explicit legal mask construction. Equality at the upper endpoint is still conjectural.

## 2. The BM-24 path-histogram quotient and matrix

The sixteen ordinary paths have identical joint type (L=2, g0=0, g1=0), while the exceptional path has joint type (L=2,g0=0,g1=gamma). BM-24 proves that both complete clean laws are invariant under permutations of the two edges within each path and all sixteen ordinary paths among themselves. Therefore the **exact** hostile-readout LP has

    3 * binomial(16+2,2) = 459

mask orbit classes per hidden hypothesis, together with 919 primal variables including eta, 460 normalization/Fourier equalities, and four per-type marginal cap inequalities. The 34-bit original mask space has **2^34** atoms per hypothesis; the quotient preserves its full optimum.

An orbit signature is (h,t), where h=(h0,h1,h2) with h0+h1+h2=16 counts ordinary paths having 0,1,2 selected/flipped edges, and t in {0,1,2} counts special-path selected/flipped edges. The exact normalized one-path Krawtchouk matrix, with rows selected degree s and columns mask weight t, is

       t=0  t=1  t=2
    s=0  1    1    1
    s=1  1    0   -1
    s=2  1   -1    1 .

For ordinary selected signature s=(s0,s1,s2), the integer ordinary kernel numerator at mask histogram t is the coefficient

    [x0^t0 x1^t1 x2^t2]
      (x0+x1+x2)^s0
      (x0−x2)^s1
      (x0−x1+x2)^s2.                                (4)

Its denominator is the multinomial coefficient 16!/(t0!t1!t2!). The complete mask kernel multiplies (4) by the special-path Krawtchouk entry. The verifier reconstructs every one of these signed integer coefficients **independently of the BM-24 hypergeometric implementation**, and checks its normalized values against BM-24 on small q=8 instances.

For the clean q8 Fourier coefficients, write r=s2 (number of complete ordinary paths), b=s1 (number of singly selected ordinary paths) and alpha=3/4. Under either hypothesis h, the special degree-zero and degree-one coefficients are equal:

    W_h(s,0)=(3/4)^b*(1+7*2^-r)/8,
    W_h(s,1)=(3/4)^(b+1)*(1+7*2^-r)/8.

At special degree two,

    W_0(s,2)=(3/4)^b*(1+(7/2)*2^-r)/8,
    W_1(s,2)=(3/4)^b*((1/2)+4*2^-r)/8.             (5)

Equation (5) follows from conditioning on the shared terminal difference being zero, the exceptional gain, or one of the six remaining values. The verifier evaluates these as exact rational numbers and scales every coefficient by 2^(3*16+6)=2^54, yielding an integer.

## 3. The frozen rational dual

The dual has a free equality multiplier for every nonempty Walsh histogram signature, a normalization multiplier for each hidden hypothesis, and four nonpositive signed marginal multipliers (flat ordinary, flat exceptional, frustrated ordinary, frustrated exceptional). For any proposed candidate, its dual inequality at world h and mask orbit t is

    y_norm,h + (-1)^h sum_s
      y_s W_h(s) Phi(s,t)
      + z_(h,ord) * [t1+2t2]/(2*16)
      + z_(h,exc) * t_exc/2 <=0.                   (6)

Here Phi is the exact orbit Krawtchouk kernel, including special degree.

The certificate was **discovered numerically**, using a HiGHS LP solution, then converted to rationals at a fixed common scale

    D = 100000000.

The four signed marginal **integer numerators** are

    (-29001113, -37951043, -33047844, 0),

which sum to -D and are all nonpositive. The two normalization integer numerators are

    (9487759, -1),

whose sum over D is exactly the theorem's bound:

    (9487759-1)/100000000
       = 4743879/50000000.                           (7)

The 459 signed Walsh-orbit integer numerators are stored in the [frozen certificate archive](BM28_N16_RATIONAL_DUAL.b64) as losslessly zlib-compressed, base64-encoded **little-endian int64 values**. The compressed file has a SHA-256 checksum in the verifier; its decoded raw 3672 bytes have digest

    47bd694403aa4ce43d1e8e8b501b7ca05d2b2f1dbe97dd1e0152cbdc1835ec16.

Of the 459 entries, **441 are nonzero** and the trivial Fourier entry is zero. The compressed representation is a file-size choice, not an approximate or opaque proof step: the [pure-stdlib verifier](n16_rational_lower_BM28.py) decompresses, checks the SHA-256 digest, unpacks each signed coefficient, and independently checks all LP inequalities. The source gives the integer construction formulas and can print/recover every stored multiplier for inspection. No trust in the numerical solver is needed.

### Exact integer verification

Every dual slack in (6) is multiplied by the strictly positive integer

    D * 2^54 * multinomial(16;t0,t1,t2) * 32.

After this scaling, each of the dual inequalities is an integer sum of four terms: a normalization term, a signed Fourier-character sum from (4)/(5), an ordinary-path mask-cost term, and an exceptional-path mask-cost term. The verifier computes those integers and demands that **all** are nonpositive, for every one of

    2 * 459 = 918

hypothesis/mask-orbit cases. The two normalization multipliers were reduced slightly after rational reconstruction to leave a conservative feasible lower proof; some exact slacks can be strictly negative. This is a conventional independently checkable approximate-optimum dual certificate with **exact feasibility**.

The LP quotient symmetrization theorem upgrades these 918 exact mask-orbit checks to a universal lower bound against **every possible correlated, world-aware full 34-bit mask pair**, including those with no ordinary-path exchangeability.

For independent verification, the [new tests](test_n16_rational_lower_BM28.py) compare the integer polynomial ordinary mask kernel with BM-24's separate exact hypergeometric oracle on smaller repeated-path graphs, and compare all q8 clean Walsh formulas with BM-24's independent terminal-conditioning oracle for n=2,3,4,8. Malformed input and certificate checks are included. The full archive and all 918 integer inequalities are checked by CPU-only standard-library CI.

## 4. What this resolves about the conjectured limit

The previous **certified** n=3 lower bound from BM-26 was

    751225/13956626 ≈ 0.0538256882.

Equation (1) now strengthens the asymptotic lower endpoint to **0.09487758**, using n=16 and a completely checkable rational dual. BM-27 independently proves the all-n upper endpoint **5/52≈0.0961538462** with a five-component legal masking mixture. The remaining gap is only about **1.33% of the candidate upper endpoint**.

The exploratory numerical LP for n=16 gave eta≈0.0948776078. That value motivated the rational certificate, but the exact theorem here claims only the slightly smaller verified lower 0.09487758. It does **not** claim an exact n=16 optimum, a matching n=16 primal, an asymptotic rate, or a proof that the limit equals 5/52. BM-27/C1 remains an open limiting-value conjecture.

A next analytic problem is to find a uniform-in-n lower certificate whose objective tends to 5/52, perhaps by exploiting the infinite exchangeable ordinary-path mask law and its conditional two-bit parity coupling to the exceptional path. The finite 459-orbit witness supplies a stringent numerical calibration for proposed asymptotic inequalities.

## 5. Mathematical and safety scope

The certificate uses classical permutation-orbit LP, Boolean Fourier/Krawtchouk transforms and weak LP duality. The exact checks concern a finite stylized statistical observation experiment with fresh uniform vertex labels and readout errors independent of the current clean sample. No conclusions are drawn about actual model reward hacking, operational AI alignment, authenticated intervention or root state, or the Unique Games Conjecture. Independent prior-art review is necessary before asserting publication novelty.
