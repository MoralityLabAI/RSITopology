# BM-29: Exact infinite-replication erasure threshold at q=8

**10 November 2026 | asymptotic theorem with a measure-theoretic lower proof and an exact attaining family.**

This resolves **BM-27/C1**, the limiting-value conjecture left open by [BM-27's all-n upper construction](UNIFORM_Q8_REPLICATION_UPPER_BM27.md) and [BM-28's n=16 rational lower certificate](RATIONAL_N16_LOWER_BM28.md).

> **Theorem BM-29/T1.** In the frozen full-Boolean gain-graph readout model over K=F₂³, with n ordinary two-edge u–v paths of gain 0 in both worlds and one exceptional two-edge path whose gain changes from 0 to a fixed nonzero element, let eta_n be the least uniform per-bit flip budget of a hypothesis-aware, arbitrarily within-episode correlated **XOR mask independent of the current clean sample** that makes the two complete output laws equal. Then
>
> \
> **lim_(n→∞) eta_n = 5/52 = 0.0961538461538... .**         (1)
>
> The limit is approached from below because projection makes eta_n nondecreasing. BM-27 supplies the matching legal, explicit **all-n** upper bound eta_n≤5/52.

The analytic lower proof uses finite-n Fourier **marginal rigidity**, compactness, the classical de Finetti theorem for an infinite exchangeable sequence with a distinguished exceptional pair, and a sharp inequality for signed measures linked by the dyadic map w→w/2. The proof is written below in standard measure-theoretic terms; the accompanying standard-library code verifies all exact finite algebraic lemmas and the equality case. **It is not a machine-checked formalization of the de Finetti/disintegration steps.** Independent peer review of the measure argument remains appropriate before publication.

## 1. Conditional two-edge path distributions and Fourier positivity

For an ordinary two-edge path, conditional on the difference between the terminal labels, its two Boolean satisfaction bits have distribution

    A = (7/8,0,0,1/8) when that difference matches the path gain,
    B = (3/4,1/8,1/8,0) otherwise,

with pair outcomes ordered (00,10,01,11). The exact XOR Walsh transforms, indexed by the empty, first, second and both-bit characters, are

    hat A=(1,3/4,3/4,1),
    hat B=(1,3/4,3/4,1/2).                           (2)

The first three coefficients agree and are strictly positive. The full-pair parity coefficient differs by a factor of two.

The joint clean law of the **n ordinary paths alone** is the same under both hidden worlds:

    P_ord = (1/8) A^(tensor n) + (7/8) B^(tensor n). (3)

For any Fourier character on the ordinary paths, let b be the number of paths with exactly one reported bit selected, and r the number with both bits selected. Its Fourier coefficient is

    hat P_ord(S)=(3/4)^b [1+7*(1/2)^r]/8 >0.        (4)

Adding one selected bit from the exceptional two-edge path multiplies this coefficient by 3/4, independently of the exceptional path gain. Thus for **any** S drawn from the ordinary reports, and either special bit j,

    W_0(S)=W_1(S)>0,
    W_0(S+{special_j})=W_1(S+{special_j})>0.        (5)

### Lemma BM-29/L1: finite-n noise marginal rigidity

Suppose the two masked *complete* Boolean output laws agree. XOR convolution multiplies Fourier coefficients, so (5) forces

    hat Q_0(S)=hat Q_1(S),
    hat Q_0(S+{special_j})=hat Q_1(S+{special_j})

for **every** ordinary-edge Fourier subset S, and for each j separately. Walsh inversion gives the stronger **equality of entire noise marginal distributions**

    (Q_0)_{ordinary}=(Q_1)_{ordinary},
    (Q_0)_{ordinary+special_j}
       =(Q_1)_{ordinary+special_j},   j=1,2.       (6)

Thus a legal hypothesis-aware equalizer can change its **coupling of the two special noise bits conditional on the ordinary noise**, while all ordinary-noise correlations and the joint noise law of the ordinary bits with **each** special bit are the same across worlds. This is true for every finite n, regardless of correlated masking, and is independently verified by the finite witnesses of BM-25, BM-26 and BM-27 in [test_infinite_replication_rigidity_BM29.py](test_infinite_replication_rigidity_BM29.py).

The proof of (6) uses only nonvanishing shared clean Fourier coefficients. The condition holds at q=8; it need not hold at alphabets where those coefficients vanish.

## 2. From finite equalizers to an infinite exchangeable mask law

BM-26 already established that eta_n is nondecreasing under projection of ordinary paths, and BM-27 established eta_n≤5/52. Hence the limit eta_inf exists.

For each n choose an attaining pair of finite mask distributions at eta_n, which exists because the finite probability simplex and constraints are compact. Average the two mask distributions under swaps within each ordinary path, permutations of the ordinary paths and swaps of the exceptional pair's bit coordinates. Both clean laws are invariant under this group, so symmetrization preserves exact output equality and cannot increase the largest bit-flip marginal.

Take a sequence n→∞. For every fixed number k of ordinary paths and the exceptional pair, their projected mask distributions live in finite compact probability simplices. A diagonal subsequence converges simultaneously for both worlds and every k. The resulting laws form **consistent infinite exchangeable sequences of two-bit ordinary noise pairs**, each augmented with the distinguished exceptional two-bit noise Z_h. Every finite projected **masked output law** remains equal across the worlds, and its bit costs remain at most eta_inf. The finite rigidity lemma (6) passes to all the limits.

By the classical finite-alphabet de Finetti–Hewitt–Savage representation, the infinite ordinary noise sequence has a random **directing pair distribution** M on {00,10,01,11}, conditional on which the ordinary mask pairs are i.i.d. The common ordinary mask law in (6) makes the distribution mu of M identical in both worlds. Since the whole array is invariant under independent within-pair bit swaps, M is a.s. symmetric in its two bit positions. Conditional on M, the distinguished exceptional mask Z_h has an arbitrary distribution depending on h and M, and the ordinary noise pairs remain i.i.d. The conditional distribution of each **single exceptional noise bit** is identical in the two worlds, again by (6).

Write the two nontrivial ordinary-noise Fourier coordinates of M as

    u(M) = E_M[(-1)^first bit]
          = E_M[(-1)^second bit],
    w(M) = E_M[(-1)^(first+second bit)].           (7)

Symmetric physical nonnegative two-bit mask probabilities are

    M(00)=(1+2u+w)/4,
    M(10)=M(01)=(1-w)/4,
    M(11)=(1-2u+w)/4.                              (8)

In particular, all physical M satisfy

    2u−1 <= w <=1.                                 (9)

Let C_o be the unconditional flip probability on either ordinary noise bit. With the common directing law mu,

    C_o = (1/2) integral (1-u) dmu <= eta_inf.      (10)

### Conditional exceptional-mask measures

For h=0,1, define a signed measure nu_h on the space of directing states M by

    dnu_h(M) =
       E[(-1)^(Z_(h,1)+Z_(h,2)) | M] dmu(M).        (11)

Thus -mu<=nu_h<=mu. Define the **common** signed measure v by

    dv(M)=E[(-1)^Z_(h,1) | M] dmu(M)
         =E[(-1)^Z_(h,2) | M] dmu(M),               (12)

which is independent of h, by the finite rigidity lemma and exceptional-edge symmetry. The exceptional bit-flip budget is

    C_s=(1-integral dv)/2 <=eta_inf.                 (13)

For a fixed state M, nonnegativity of the exceptional-mask event Z_h=(1,1) gives the measure inequality

    2v <= mu+nu_h,    h=0,1.                        (14)

Let nu_0 wedge nu_1 denote the pointwise minimum of their Radon–Nikodym densities relative to mu. By taking both inequalities (14),

    2v <= mu+(nu_0 wedge nu_1).

Writing

    H=integral d(nu_0 wedge nu_1),

and integrating, we obtain the useful budget lower bound

    C_s >= (1-H)/4.                                (15)

The remaining task is to control the signed-measure overlap H in terms of the ordinary noise cost C_o.

## 3. The exact dyadic signed-measure equation

Conditional on the directing ordinary mask M, the clean ordinary path distribution is A or B according to the common terminal difference. XOR convolution multiplies Fourier coefficients. By (2), an ordinary output pair has single-edge Fourier coordinates (3/4)u in both terminal regimes, and full-pair parity coordinate

    w   when clean ordinary regime is A,
    w/2 when clean ordinary regime is B.           (16)

With infinitely many conditional-i.i.d. ordinary output pairs, the empirical output pair distribution almost surely identifies these coordinates. The exceptional **output** two-bit parity character remains a finite observable carried alongside that limiting empirical pair law.

Let S be the measurable injective dyadic map on the (u,w) coordinate plane,

    S(u,w)=(u,w/2),                                 (17)

and write S_*nu for its pushforward of a signed measure. The clean conditional weights and exceptional parity coefficients are:

| World | Ordinary A regime | Ordinary B regime |
|---|---|---|
| Flat h=0 | weight 1/8, special parity coefficient 1 | weight 7/8, special parity coefficient 1/2 |
| Frustrated h=1 | weight 1/8, special parity coefficient 1/2 | weight 7/8, average special parity coefficient 4/7 |

Equality of the infinite output empirical-measure distribution **jointly with exceptional parity** therefore yields

    (1/8) nu_0 + (7/16) S_*nu_0
      = (1/16) nu_1 + (1/2) S_*nu_1,

or equivalently

    **(2 I+7 S_*) nu_0 = (I+8 S_*) nu_1.**          (18)

This is a signed-measure identity; it does not assume that nu_h is pointwise nonnegative. It holds separately in every fiber of u, because S preserves u. All independence used here follows from the frozen requirement that the readout mask be independent of the **current** clean vertex labels.

## 4. BM-29/L2: a sharp dyadic overlap bound

**Lemma.** Suppose mu is a probability measure on physically feasible symmetric ordinary pair-mask states (u,w), nu_0,nu_1 are signed measures dominated in absolute value by mu, and they obey (9) and the dyadic relation (18). Then

    **H <= (16/5) integral (1-u) dmu.**             (19)

Here H=integral min(dnu_0,dnu_1), with densities taken relative to mu. The inequality holds on an arbitrary continuous or atomic directing measure, including arbitrary correlations between its parameters.

**Proof.** Disintegrate over the coordinate u; the dyadic map S does not change u. We prove the inequality for each u-fiber.

**Case A: u<=11/16.** Since nu_h<=mu, their pointwise minimum is at most mu. Because

    (16/5)*(1-u) >= (16/5)*(5/16)=1,

the claimed inequality holds immediately, without using (18).

**Case B: u>3/4.** The physical constraint (9) forces w>1/2. Since w/2<1/2, the original signed measures and their dyadic images are supported in disjoint w-ranges. Restricting (18) to the original and pushed ranges gives, respectively,

    2nu_0=nu_1,   7nu_0=8nu_1.

Thus nu_0=nu_1=0 and the overlap is zero.

**Case C: 11/16<u<=3/4.** Put a=2u−1, so 3/8<a<=1/2. Every feasible w lies in [a,1]. Divide this interval into its high half W_H=(1/2,1] and low half W_L=[a,1/2]. Under S, the image of W_L lies at or below 1/4, outside [a,1], because a>3/8. Moreover an image of W_H can fall within [a,1] only in W_L. Thus every interacting dyadic chain has **at most two feasible levels**, and any isolated high state must carry zero signed parity mass.

Let c denote the restriction of nu_0 to the high interval, treated as a signed measure. Restrict (18) successively to the high interval, the low interval, and the image of the low interval. The resulting equalities are

    nu_1(high)=2c,
    nu_0(low)=8 S_*c,
    nu_1(low)=7 S_*c.                               (20)

Any part of c whose image is outside the feasible low interval must vanish, so (20) captures all possible signed mass. Since |nu_h|<=mu, we have

    mu(high)>=2|c|,
    mu(low)>=8 S_*|c|,

where the inequalities are between positive measures. Hence the total mass of this fiber is at least 10||c|| in total variation.

The pointwise minimum of c and 2c on the high interval, together with the minimum of 8c and 7c on the low interval, integrates to at most 8||c||: positive c contributes 1+7=8 units, while negative c contributes a negative 2+8=10 units. Therefore

    H_u <= 8||c|| <= (4/5) mu_u(total).             (21)

Since u<=3/4, we have (16/5)(1-u)>=4/5, giving the desired bound on this fiber.

All cases are exhausted. Integrating the fiberwise inequalities proves (19). □

The coefficient **16/5 is sharp**: BM-27's attaining channel has a high/low dyadic chain at u=3/4 with masses 2/13 and 8/13, signed exceptional-parity mass ratio (nu_0,H,nu_1,H,nu_0,L,nu_1,L)=(1,2,8,7)/13. In that chain (21) holds with equality.

## 5. BM-29/T1 lower proof, matched by BM-27

Combine (10), (15) and (19):

    8 C_o + 5 C_s
      >= 4 integral (1-u)dmu
           + (5/4)(1-H)
      >= 4 integral (1-u)dmu
           + (5/4) -(5/4)*(16/5) integral (1-u)dmu
      = 5/4.                                       (22)

Each individual readout-bit marginal is bounded by eta_inf. In particular, C_o<=eta_inf and C_s<=eta_inf, so

    13 eta_inf >= 8 C_o+5 C_s >=5/4,

and hence

    **eta_inf >= 5/52.**                            (23)

BM-27 independently constructs admissible legal mask pairs at **exactly 5/52 for every finite n**, so eta_inf<=5/52. Combining gives (1). This completes the limiting-value proof.

### Exact equality case and its interpretation

The BM-27 world-dependent mask mixtures induce the following common directing law and exceptional parity measures:

| Ordinary mask M | u | w | mu(M) | nu_0(M) | nu_1(M) |
|---|---:|---:|---:|---:|---:|
| I=(1,0,0,0) | 1 | 1 | 3/13 | 0 | 0 |
| A=(7/8,0,0,1/8) | 3/4 | 1 | 2/13 | 1/13 | 2/13 |
| B=(3/4,1/8,1/8,0) | 3/4 | 1/2 | 8/13 | 8/13 | 7/13 |

The exceptional **single-bit** signed measure v has masses (3/26, 3/26, 15/26) at I,A,B respectively. Thus

    H=0+1/13+7/13=8/13,
    C_o=(1/2)*[(2/13+8/13)*(1/4)]=5/52,
    C_s=(1/2)*(1-21/26)=5/52.

The dyadic relation (20) holds exactly on the A↦B chain, while the I atom is an isolated high-u state with zero exceptional parity moment. Consequently

    8*(5/52)+5*(5/52)=5/4,

so **every bound used in the asymptotic lower proof is attained**. The attached [BM-29 exact algebra code](infinite_replication_rigidity_BM29.py) derives these rational masses from the original BM-27 legal masks, checks the 1:2:8:7 dyadic signed-parity ratio and confirms equality in (19) and (22).

## 6. Verification and scope

New additions:

- [infinite_replication_rigidity_BM29.py](infinite_replication_rigidity_BM29.py): exact four-state Walsh transforms, ordinary/single-special Fourier positivity, physical symmetric-mask feasibility, finite two-level signed-measure recurrence, low-u and isolated-high-u inequalities, BM-27 directing-atom extraction and exact equality of the weighted costs.
- [test_infinite_replication_rigidity_BM29.py](test_infinite_replication_rigidity_BM29.py): independent reconstruction of the q8 clean Walsh coefficients using BM-24, exact finite marginal rigidity on **BM-25 n=2**, **BM-26 n=3**, and **BM-27 n=1..3** world-specific masks, the signed dyadic convolution equation on BM-27's atoms, rational chain inequalities including negative signed parity, and all equality-case costs.
- Earlier [BM-27](UNIFORM_Q8_REPLICATION_UPPER_BM27.md) supplies the legal all-n upper masks, while [BM-28](RATIONAL_N16_LOWER_BM28.md) supplies a finite, independent exact lower certificate below the limit.

**What is now established:** the exact q8 two-edge growing-theta limit is **5/52** under the specified fresh-uniform-label observation law, world-aware but current-clean-independent correlated readout adversary, and full-output erasure requirement. Finite-n optima for n>=4 and a quantitative convergence rate are still open. The proof relies on infinite exchangeability; if readout masks are allowed to inspect the **current clean report**, the de Finetti/independence calculation breaks and a different adversarial model is needed.

**Mathematical antecedents:** the infinite exchangeability and directing-measure steps use de Finetti–Hewitt–Savage, a classical theorem for finite-alphabet exchangeable sequences; see the [Berkeley de Finetti survey](https://www.stat.berkeley.edu/~ryantibs/papers/defin.pdf) and [elementary proof of de Finetti's theorem](https://www.sciencedirect.com/science/article/pii/S0167715219300902). The remainder is elementary finite XOR Fourier analysis and a new model-specific signed-dyadic-overlap inequality. Publication novelty against adversarial symmetrizability and exchangeable-channel literature has not been independently certified. Neither a new Unique Games proof nor an empirical alignment, trusted-restoration or AI-control claim follows from this mathematical theorem.
