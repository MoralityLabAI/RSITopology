# BM-30: Rigidity, uniqueness and stability of the optimal q=8 masking channel

**10 November 2026 | asymptotic equality-case theorem, quantitative infinite-measure stability, exact finite checks.**

This continues [BM-29's exact infinite-replication theorem](INFINITE_REPLICATION_LIMIT_BM29.md), which proves

    eta_infinity(8,2) = lim_(n→infinity) eta_n(8,2)
                      = 5/52.

The new result identifies the **entire equality family** of BM-29's weighted lower inequality, proves that its *minimax* attaining infinite channel is unique after symmetry averaging, and establishes qualitative convergence of finite optimum-mask projections. It also gives an explicit quantitative *infinite-channel* stability inequality localizing the directing measure near the two optimal ordinary-noise regimes.

The model remains frozen: q=8, n ordinary two-edge paths with total gain zero in both hidden worlds, one exceptional two-edge path with total gain zero/nonzero, fresh uniform vertex labels, full Boolean satisfaction readouts, and a hypothesis-dependent arbitrarily correlated XOR error mask **independent of the current clean sample** with a uniform per-bit error cap. The present work relies on the de Finetti/measure-theoretic steps proved in BM-29 and supplies independently checkable exact finite algebra. These measure steps are **not formalized in Lean**.

## 1. The BM-29 measure-level quantities

After ordinary path and within-pair permutation symmetrization, any infinite ordinary-noise sequence has a common de Finetti directing measure mu on symmetric, physically realizable two-bit noise distributions M. Parametrize M by its equal single-bit Walsh moments u and its pair-parity Walsh moment w:

    M(00)=(1+2u+w)/4,
    M(10)=M(01)=(1-w)/4,
    M(11)=(1-2u+w)/4,                             (1)

with the physical inequality

    2u-1 <= w <= 1.                                 (2)

Let nu_0 and nu_1 be the exceptional-noise pair-parity signed measures in the two hidden worlds. The finite-output rigidity lemma forces the two hypotheses to share mu and a signed single-exception-bit measure v, and the infinite-output parity identity is

    (2I+7S_*) nu_0 = (I+8S_*) nu_1,
    S(u,w)=(u,w/2).                                 (3)

Write

    J=integral (1-u) dmu,
    H=integral min(dnu_0,dnu_1),
    C_o=J/2,
    C_s=(1-integral dv)/2.                           (4)

Here the minimum of the two signed measures is defined using their Radon–Nikodym densities with respect to common dominating mu.

BM-29 established

    H <= (16/5)J,                                    (5)
    2v <= mu + (nu_0 wedge nu_1).                     (6)

The first is a dyadic signed-measure overlap inequality, and the second follows from nonnegative probability on the exceptional mask event (11) in each world.

## 2. BM-30/T1: exact characterization of all weighted-dual equality channels

**Theorem.** Among infinite exchangeable, hypothesis-aware full-output equalizers in this model, the weighted equality

    8 C_o + 5 C_s = 5/4                             (7)

holds if and only if the common directing law is supported on the following three ordinary pair-noise distributions, with a single parameter 0<=c<=1/10:

    I=(1,0,0,0),
    A=(7/8,0,0,1/8),
    B=(3/4,1/8,1/8,0),

and the masses and exceptional parity signed measures are

| Ordinary mode | (u,w) | mu | nu_0 | nu_1 |
|---|---|---:|---:|---:|
| I | (1,1) | 1-10c | 0 | 0 |
| A | (3/4,1) | 2c | c | 2c |
| B | (3/4,1/2) | 8c | 8c | 7c |

The common signed single-special-bit measure is forced by equality in (6):

    v(I)=(1-10c)/2,
    v(A)=3c/2,
    v(B)=15c/2.                                    (8)

When an atom has zero mass, the corresponding conditional probabilities are immaterial. Otherwise the *conditional exceptional noise distribution*, indexed by hidden world, is uniquely determined by its equal single-bit Fourier moments and pair-parity moment:

| Ordinary mode | Special noise in flat world | Special noise in frustrated world |
|---|---|---|
| I | E | E |
| A | (I+E)/2 | A |
| B | (3I+A)/4 | (3I+B)/4 |

Here E=(1/2,1/4,1/4,0) is the two-bit fair one-hot eraser. Each table entry is a legal nonnegative four-state distribution.

**Proof of necessity, including the endpoint cases.** Introduce two nonnegative defects:

    G=(16/5)J-H >=0,
    T=integral [ (dmu + d(nu_0 wedge nu_1))/2 - dv ] >=0.  (9)

Directly expanding (4) gives the **exact gap identity**

    8 C_o+5 C_s-5/4
       = (5/4)G + (5/2)T.                           (10)

Thus (7) forces G=T=0.

We sharpen BM-29's dyadic overlap proof by making its pointwise deficits explicit. Disintegrate the measure over u.

- **u<=5/8:** domination yields H_u<=mu_u; since (16/5)(1-u)>=6/5, this fiber has strictly positive G unless mu_u=0.
- **5/8<u<=3/4:** physical w>=2u-1>1/4, so the feasible interval [2u-1,1] cannot contain three distinct successive dyadic levels w,w/2,w/4. Every nonzero signed solution of (3) is therefore supported on a two-level high/low chain. If c denotes its signed high-level nu_0 measure, the full recurrence is exactly
      (nu_0(high),nu_1(high),nu_0(low),nu_1(low))
         =(c,2c,8 S_*c,7 S_*c).
  Physical dominance requires mu(high)>=2|c| and mu(low)>=8 S_*|c|. The overlap is at most 8||c|| and hence H_u<=(4/5)mu_u. When u<3/4, (16/5)(1-u)>4/5, so any positive mu mass gives a strict G deficit.
- **u>3/4:** physical w>1/2, so no two feasible dyadic levels coexist. Equation (3) forces nu_0=nu_1=0 and H_u=0. As long as u<1, (16/5)(1-u)>0 and the G deficit is strict.

Consequently, G=0 forces mu to concentrate **only on u=3/4 and u=1**. At u=1, (2) enforces w=1 and the signed exceptional parity masses vanish. At u=3/4, feasible w lies in [1/2,1]; a two-level dyadic chain exists only for w=1 and w/2=1/2. Equality H_u=(4/5)mu_u forces the high signed measure c to be *nonnegative* and the directing masses to be their minimum physical values **2c and 8c**, with no extra mass at unrelated w. Normalization then requires mu(I)=1-10c and 0<=c<=1/10. These conditions give the displayed mu and nu tables.

Equality T=0 in (10) forces v=(mu+nu_0 wedge nu_1)/2, giving (8). A symmetric physical two-bit exceptional mask is uniquely determined by its equal one-bit Fourier moments and its pair-parity moment, via the inverse of (1), yielding the conditional special-noise table. This proves necessity.

**Proof of sufficiency.** The given tables are normalized and physical for every 0<=c<=1/10. They satisfy the dyadic measure identity (3) and the shared exceptional single-bit condition. They also have a direct finite-n realization. Let `I_n` denote the all-zero ordinary mask, and let `Q_active,h` be the non-I branch of BM-27's world-h construction, renormalized from its total 10/13 mass to one. Define

    Q_h(c) = (1-10c) [I_n tensor E] + 10c Q_active,h.    (11)

Both `I_n tensor E` and `Q_active,h` independently equalize the full reported output laws: the former kills the only potentially unequal special pair-parity character, while the latter follows by subtracting the first equalizer from BM-27's already proven convolution identity. Thus every convex mixture (11) is a legal **complete-output equalizer for all n**, and it produces precisely the displayed directing masses and conditional special laws. Direct substitution gives equality in (5), (6) and (7). □

### The exact frontier of corruption costs

For every 0<=c<=1/10, the two types of readout bit have exact marginal error costs

    C_o(c)=5c/4,
    C_s(c)=1/4-2c.                                  (12)

As c increases, ordinary-path masking increases and exceptional-path masking decreases. Every channel on this family obeys

    8 C_o(c)+5 C_s(c)=5/4,                          (13)

which is the sharp weighted lower inequality from BM-29. The minimax error allowance is

    eta(c)=max(5c/4,1/4-2c).

There is a unique intersection at

    5c/4=1/4-2c  <=>  c=1/13,

giving

    **eta_minimax=eta(1/13)=5/52.**                 (14)

At that point the directing masses are mu(I,A,B)=(3,2,8)/13, exactly the BM-27 construction. This proves that **the symmetrized infinite-replica optimal readout channel is unique as an entire joint distribution**, rather than merely having a uniquely determined scalar noise budget.

It is useful to distinguish (13) from minimax optimality: the endpoint c=0 is a legal channel with ordinary cost zero and exceptional cost 1/4; the endpoint c=1/10 is a different legal channel with costs 1/8 and 1/20. Both attain the weighted *equality* while having larger maximum per-bit costs. The balanced choice c=1/13 uniquely minimizes that maximum.

## 3. BM-30/T2: finite optimal-mask projections converge to the BM-27 channel

**Theorem.** Let Q_(0,n),Q_(1,n) be any sequence of admissible, complete-output equalizing n-ordinary-path mask pairs whose maximum per-edge errors eta_n' converge to 5/52. Symmetrize each mask law under permutations of ordinary paths, within-pair swaps and exceptional-pair swaps. For any fixed k>=1, project the resulting n-th mask pair onto its first k ordinary paths and the exceptional two-bit mask. Then **both projected distributions converge in total variation to the corresponding k-path projection of BM-27's mask pair**.

This includes sequences of exact finite-n minimizers, because BM-29 proved eta_n↑5/52.

**Proof.** For fixed k and both worlds, the projected masks live in a finite-dimensional probability simplex, hence are compact. Take an arbitrary subsequence of n values. By the diagonal subsequence argument across all k and both worlds, extract a subsubsequence whose complete finite-coordinate projections converge. Its projective limit is an infinite exchangeable ordinary-noise sequence with a distinguished exceptional pair. All finite complete-output equalities and clean-current-sample independence conditions pass to the limit, and its bit costs are at most 5/52.

BM-30/T1 together with BM-29's lower bound forces the directing measure to have c=1/13 and the unique conditional exceptional pair laws of the table in section 2. The conditional ordinary pairs are i.i.d. with that directing measure by de Finetti. Thus the entire infinite joint mask law agrees with BM-27. Every subsubsequential limit therefore has the same projected distribution. Compactness implies convergence of the original projected sequence. Since the projected sample space is finite, ordinary weak convergence equals **total variation convergence**. □

This convergence is a **qualitative theorem**. It supplies neither an explicit dependence on n nor an exponential/polynomial convergence rate.

## 4. BM-30/T3: quantitative stability for near-optimal infinite channels

The exact defect identity (10) also gives a meaningful quantitative bound under the same infinite exchangeable threat model.

**Theorem.** Suppose a legal infinite exchangeable equalizer has a uniform per-bit mask cap

    eta <= 5/52+delta,    delta>=0.                  (15)

Then the overlap defect G and special-atom positivity defect T obey

    **G <= (52/5)delta,**
    **T <= (26/5)delta.**                            (16)

Indeed (10) is nonnegative, and its left side is at most 13eta-5/4<=13delta. Bounding its two nonnegative terms separately proves (16).

### A quantitative localization bound on ordinary noise

The same dyadic case analysis yields a stronger *fiberwise* estimate. Define

    g(u) =
      16(1-u)/5 - 1,       u<=5/8,
      16(3/4-u)/5,         5/8<u<=3/4,
      16(1-u)/5,           3/4<u<=1.                (17)

The overlap proof gives

    G >= integral g(u) dmu(u,w).                     (18)

The nonnegative function g vanishes only at **u=3/4 and u=1**, exactly the two ordinary single-bit Walsh values of the optimal channel.

For 0<epsilon<=1, on the set of u values at distance at least epsilon from both 3/4 and 1, formula (17) gives

    g(u)>=min(1,16epsilon)/5.

Markov's inequality applied to (16)/(18) then yields the explicit stability estimate

    **mu{dist(u,{3/4,1})>=epsilon}
        <= min(1, 52delta/min(1,16epsilon)).**      (19)

This is a quantitative **infinite-channel directing-measure** localization statement, with a clean and fully explicit dependence on delta and epsilon. It controls the total probability assigned to ordinary mask modes whose *single-bit* Fourier coordinate lies far from both optimal values. It does not by itself bound total variation to the full BM-27 directing measure when delta>0, because distinguishing values of w and the exceptional coupling requires further stability estimates.

For instance, with delta=1/1000 and epsilon=1/32, (19) bounds the outlying directing mass by 13/125, approximately 10.4%. The bound is conservative; its value lies in its universal validity over arbitrary legal infinite exchangeable equalizers.

### What remains open

The exact limiting value and unique limit channel are established under the registered threat model. A **quantitative finite-n rate** for eta_n approaching 5/52, and a rate for the total variation convergence of projected finite optimal masks in section 3, require a finite-exchangeability approximation with controlled losses in the exceptional-mask compatibility relation. Existing finite de Finetti bounds may assist, but the signed dyadic-overlap inequality would need a robust finite-n version. An explicit convergence-rate claim has therefore not been added.

## 5. Reproducibility and prior-art boundary

The committed exact-Python modules are:

- [optimal_channel_rigidity_BM30.py](optimal_channel_rigidity_BM30.py): complete one-parameter directing law, exact exceptional conditional pair masks, an **all-n finite legal mask sampler representation** for the entire equality family, full small-n output and marginal verification, unique minimax intersection, dyadic local-gap function and quantitative stability formulas.
- [test_optimal_channel_rigidity_BM30.py](test_optimal_channel_rigidity_BM30.py): complete output-law equality for multiple rational parameters c on n=1,2,3, independent signed dyadic pushforward verification, exact moment accounting, exceptional pair reconstruction, unique minimax cost tests, stability bound controls, and hostile malformed-input checks.
- [BM-29 complete limit proof](INFINITE_REPLICATION_LIMIT_BM29.md) supplies the infinite exchangeability construction and global signed-measure overlap inequality. [BM-27 legal all-n masks](UNIFORM_Q8_REPLICATION_UPPER_BM27.md) provide the equality case used as the limit.

The group-averaging and de Finetti portions belong to classical exchangeability theory; see [Hewitt and Savage, *Symmetric measures on Cartesian products* (1955)](https://doi.org/10.2307/1969818) for the general representation theorem, and [Diaconis and Freedman, *Finite exchangeable sequences* (1980)](https://doi.org/10.1214/aop/1176994663) for quantitative finite-exchangeability background. The equality-family and dyadic stability analysis are specialized to the finite q8 gain-graph readout channel and need independent mathematical/prior-art review before novelty claims.

No Lean formalization of infinite measure theory, operational AI model evaluation, verified external restoration root, or new Unique Games result is included in BM-30.
