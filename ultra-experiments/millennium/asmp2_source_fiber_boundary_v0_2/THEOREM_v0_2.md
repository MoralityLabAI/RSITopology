# ASMP-2 source-fiber boundary and finite-source impossibility

## Scope

This packet proves a model-independent source-fiber theorem and a sharp
negative result for unrestricted smooth QMD continuation. It does not silently
replace the v0.1 candidate with a finite benchmark.

## Definitions

Let `M` be a finite registered set of environment families and `A` a finite
registered policy/monitor class. For `m in M`, let `Q_m` be the complete
population source law and define the globally good action set

```text
G_m = {a in A:
       sup_(theta in Theta_adv) L_s(a,P^m_theta) <= epsilon
       and
       inf_(theta in Theta_adv) U(a,P^m_theta) >= u_0}.
```

The source fiber at a population law `q` is

```text
C(q) = {m in M: Q_m=q}.
```

For a nonempty fiber `C`, define its randomized compatibility value

```text
alpha(C)
  = max_(pi in probability simplex over A)
      min_(m in C) pi(G_m).
```

This value is invariant under parameter coordinates, observation relabeling,
and action relabeling.

## Theorem 1: exact population source-fiber criterion

When the population source law is known exactly, the largest uniform
probability with which any source-only procedure can output a globally safe,
useful action is

```text
alpha_* = min over nonempty source fibers C of alpha(C).
```

Consequently:

1. a randomized `(epsilon,u_0,delta)` certificate exists if and only if
   `alpha_* >= 1-delta`;
2. a zero-error deterministic certificate exists if and only if every source
   fiber has a common good action:

   ```text
   intersection_(m in C) G_m is nonempty;
   ```

3. if one source fiber contains two models with disjoint singleton good-action
   sets, its exact randomized value is `1/2` and its deterministic value is
   zero.

For finite fibers, von Neumann/linear-programming duality also gives the
adversarial certificate

```text
alpha(C)
  = min_(lambda in probability simplex over C)
      max_(a in A) sum_(m in C) lambda_m 1{a in G_m}.
```

The primal distribution is a constructive randomized safe-action rule. The
dual distribution is a least-favorable mixture of source-indistinguishable
worlds. The exact-rational companion solver enumerates every primal and dual
vertex and verifies equality over the complete census with one to three worlds
and two to three actions.

### Proof

Conditional on observing a population law `q`, every source-only procedure
must use one action distribution `pi_q` for every model in `C(q)`. Its worst
success on that fiber is `min_(m in C(q)) pi_q(G_m)`, whose supremum is exactly
`alpha(C(q))`. Taking the least favorable fiber gives the upper bound
`alpha_*`. Conversely, choose a maximizing distribution independently on each
fiber; finiteness avoids measurable-selection issues and attains `alpha_*`.
The deterministic corollary restricts `pi` to point masses. The two-singleton
case is the exact program `max_(0<=p<=1) min(p,1-p)=1/2`.

## Theorem 2: smooth QMD witness with individual feasibility

Let `theta in [-1,1]`, source environments

```text
F = {-1/2,0,1/2},
```

world `s in {-1,+1}`, and action `a in {-1,+1}`. At every environment observe
the three independent Bernoulli channels `(Z,Y_-1,Y_+1)` with

```text
P(Z=1) = 1/2 + theta/8,

g(theta) = (16/9) theta^2 (theta^2-1/4)^2,

P_s(Y_a=1) = 1/2 + theta/16 + a s g(theta)/8.
```

Let safety loss be the corresponding `Y_a` mean, let utility be identically
one, set `u_0=4/5`, and set `epsilon=9/16`.

Then:

1. the two worlds have exactly equal complete source laws for every source
   sample allocation;
2. their source-law derivatives are also equal;
3. the reference Fisher information at `theta=0` is `3/32>0`;
4. every action-risk derivative at the reference is the nonzero value `1/16`
   and factors through the identified `Z` score with factor `1/2`;
5. all probabilities lie in a common compact subset of `(0,1)`, so the
   finite-alphabet polynomial families are dominated and QMD with common full
   support;
6. both worlds obey the finite risk-curvature bound `193/36`;
7. each world has one globally safe, useful action, but the good sets are
   opposite:

   ```text
   G_- = {+1},  G_+ = {-1}.
   ```

Therefore the exact minimax success probability of every source-only procedure
is `1/2`, regardless of the finite source sample sizes. Equivalently, minimax
sample complexity is infinite for every requested `delta<1/2`.

### Proof

The polynomial and its first derivative vanish at all three sources. This
makes every action-risk channel, its first derivative, and hence the full
product experiment identical across worlds. At zero, independent-channel
Fisher information adds:

```text
4[(1/8)^2 + 2(1/16)^2] = 3/32.
```

The maximum of `|g''|` on the interval is `386/9`, so the action-risk
curvature is bounded by `(386/9)/8=193/36`. For action `a=-s`,

```text
L_s(a,theta) = 1/2 + theta/16 - g(theta)/8 <= 9/16
```

throughout the interval. Action `a=s` has loss `11/16` at `theta=1`, so it is
not globally good. Theorem 1 now gives the exact `1/2` value. Since the
`n`-sample source laws remain identical for every `n`, sampling cannot change
that value.

## Theorem 3: sharp density boundary for unrestricted continuation

Let `Theta` be a compact Euclidean domain. Require every member of the
registered continuation class to be a continuous, full-support
finite-alphabet environment family. Also require bump richness: whenever an
open ball is disjoint from a proposed source closure, the class contains the
two opposite-sign full-support bump perturbations used below. The class of all
continuous full-support families is the canonical example; when `Theta` has
interior, the analogous smooth class is another. Equality of population laws
on a source set `F` determines the law throughout `Theta` for every pair of
families in such a class if and only if

```text
closure(F) = Theta.
```

### Proof

If `F` is dense, continuity makes two laws equal on all of `Theta` whenever
they agree on `F`. If `F` is not dense, there is an open ball disjoint from its
closure. A nonzero continuous bump supported in that ball—smooth when the
domain has interior—can be added with opposite signs to two full-support
Bernoulli action-risk channels. Scaling preserves any positive probability
floor and any finite prescribed curvature ceiling. The worlds remain identical
on every source but require opposite actions at the bump maximum.

Thus a finite source set cannot certify the unrestricted smooth continuation
class on a deployment domain containing an unsampled open set. This is a
topologically sharp boundary, not merely a failed algorithm.

## Corollary: finite active design without a margin

No finite deterministic population-law active design can uniformly certify
the unrestricted class on such a domain: along its common baseline transcript,
its finite selected set is not dense, so Theorem 3 supplies an indistinguishable
opposite-action pair after the design is fixed.

Assume additionally that `Theta` has arbitrarily large finite packings of
disjoint admissible bump regions, as does a positive-dimensional Euclidean
domain with nonempty interior. Then the same conclusion holds for randomized
`T`-query designs at confidence strictly above `1/2`. Pack `N` disjoint
candidate bump regions. A realization can inspect at most `T` of them, so some
region is inspected with probability at most `T/N`. Put the hidden bump there
and average the two worlds. Even granting perfect success when the region is
inspected, average success is at most

```text
1/2 + T/(2N).
```

Choose `N` large enough to make this smaller than `1-delta`. A fixed curvature
ceiling does not repair the result when no positive safety margin is frozen:
the bump amplitude can shrink quadratically with its width while still
crossing a threshold on which the baseline lies exactly.

A positive margin plus a quantitative smoothness bound changes the result by
imposing a minimum hazardous-region width; its covering number then becomes
the relevant environment complexity. Those constants are not bound in ASMP-2
v0.1.

## Consequence for the five obligations

- **Local characterization:** adjoint-score range/positive-information
  characterizations are established semiparametric theory; they do not imply
  a global safe-action intersection.
- **Global continuation:** Theorems 1 and 3 give the exact unrestricted
  boundary—fiber compatibility, and density when the continuation class is all
  continuous families.
- **Minimax sample bounds:** the hard QMD subclass has exact complexity
  `infinity` for `delta<1/2`.
- **Active design:** every finite design has the same lower bound without a
  registered positive margin/model restriction.
- **No free lunch:** Theorem 2 supplies the required individually feasible,
  non-inert, source-indistinguishable pair.

The result is negative: finite evaluation cannot solve the unrestricted
problem. Restricted positive theorems require a successor version to bind the
model class, margin, curvature, metric, action loss, and design budget.
