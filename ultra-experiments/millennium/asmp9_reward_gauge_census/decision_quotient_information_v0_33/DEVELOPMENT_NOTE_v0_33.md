# ASMP-9 v0.33 decision-quotient information development

## Status

Unregistered and unrun as a claim-bearing experiment.

This note identifies the next load-bearing ASMP-9 obligation after v0.32:
sharp joint stochastic policy complexity. It deliberately imports established
controlled-sensing and pure-exploration results rather than claiming them as
new.

## Finite stochastic access model

Let `Theta` be a finite registered set of complete reward, mechanics,
behavioral-link, and nuisance instances. Let `Q` be a finite set of
experiments. Each pair `(theta,q)` defines a finite observation law
`P_theta,q`.

Queries may include:

- global-ruler behavioral comparisons from v0.32;
- compound-lottery mixture-affinity audits;
- environment or policy interventions that estimate occupancy information;
- context-link observations; and
- held-out decision probes.

Let `a(theta)` be the declared downstream answer: for example, the uniquely
optimal policy in a registered family, a regret band, or `not_certified`.
Reward-gauge aliases and every other transformation preserving this answer
belong to the same answer class.

## Exact decision-identifiability boundary

The finite model is decision-identifiable exactly when:

```text
for every theta,theta' with a(theta) != a(theta'),
there exists q with P_theta,q != P_theta',q.
```

This is weaker than parameter identification by design. Two observationally
identical reward representatives are harmless when they induce the same
registered answer. An observationally identical policy-changing alternative
makes any error target below one half impossible.

## Fixed-confidence information lower bound

For truth `theta`, define:

```text
C*(theta) =
max over w in Delta(Q)
min over theta' with a(theta') != a(theta)
sum_q w_q KL(P_theta,q || P_theta',q).
```

For any adaptive sequential procedure that is `delta`-correct on every
registered instance, the bandit change-of-measure inequality gives:

```text
E_theta[tau]
>= kl(1-delta,delta) / C*(theta).
```

The proof applies the change-of-measure inequality to the event that the
procedure returns `a(theta)`, then normalizes expected query counts into an
allocation `w`. If `C*(theta)=0`, the lower bound is infinite.

Classical Chernoff and Track-and-Stop theory supplies first-order asymptotic
achievability under its regularity conditions. Version v0.33 must not claim a
new achievability theorem without proving the exact conditions for the
registered composite model.

## Channel-necessity control

The development fixture has reward bit `r`, mechanics bit `m`, and answer:

```text
a(r,m)=r XOR m.
```

The behavioral query observes Bernoulli probability `0.2` or `0.8` according
to `r`. The mechanics query observes `0.25` or `0.75` according to `m`.

At truth `(0,0)`, the two nearest policy-changing alternatives differ along
separate query channels. Writing:

```text
d_B = KL(Bernoulli(0.2) || Bernoulli(0.8))
    = 0.6 log(4),

d_M = KL(Bernoulli(0.25) || Bernoulli(0.75))
    = 0.5 log(3),
```

the registered two-query game has the analytic solution:

```text
w_B = d_M/(d_B+d_M),
w_M = d_B/(d_B+d_M),
C*  = d_B d_M/(d_B+d_M).
```

Removing either query family leaves one policy-changing alternative
indistinguishable and forces `C*=0`. A duplicated same-answer hypothesis has
identical observation laws: it makes full parameter identification
impossible while leaving decision identification unchanged. This is the
finite reward-gauge control.

## What a prospective v0.33 must add

The first development successor now replaces the XOR table with a finite
model generated from:

- v0.29's registered composition cell: quotient measurement rows, two policy
  occupancies, true reward, and the decision-null third-coordinate gauge;
- v0.28's rational calibrated-occupancy response law;
- v0.32's consistent and distorted compound-lottery residuals; and
- v0.31's and v0.32's registered matrix dimensions.

It includes reward-changing, mechanics-changing, validity-changing, and
same-policy gauge-alias hypotheses. Return, mechanics, and mixture-audit
query families are each individually necessary.

This source inspection also identified a missing composition object. The
v0.31 primary certificate has eight localized observation rows. The v0.32
cross-difference operator produces six semantic residuals from twelve cells.
No registered `8 x 6` map says how those semantic residuals enter the v0.31
observations. The current fixture therefore uses v0.29's complete
measurement-to-policy cell and reports the v0.31-v0.32 coupling as
unavailable rather than inventing it.

Under the temporary equal-cost convention, the native fixture has three
separate policy-changing alternatives. Their live information values are:

```text
reward flip      d_R = (1/2) log(3)
mechanics flip   d_M = (1/2) log(3)
mixture failure  d_A = (1/2) log(289/288)
```

The max-min game is therefore solved analytically by:

```text
C* = 1 / (1/d_R + 1/d_M + 1/d_A),
w_i = C*/d_i.
```

This sends approximately `99.37%` of the equal-cost budget to the
mixture-affinity audit. The number is not an operational recommendation: it
is a consequence of the registered `1/16` violation, the imported rational
link, and the one-unit-per-observation convention. The implementation now
accepts a positive cost for every query and interprets its allocation as
fractions of total cost. A prospective protocol must freeze those costs or
report a sensitivity surface.

A prospective v0.33 must now:

1. register an observation-to-semantic coupling, or prove a result quantified
   over a declared coupling class;
2. State whether the result is a nonasymptotic lower bound, an asymptotically
   matching characterization, or only a computable design criterion.
3. Include at least one policy-changing alternative for each access channel,
   plus same-policy gauge aliases.
4. Compare joint optimal allocation with uniform, channel-ablated, and
   staged plug-in allocations.
5. Keep mixture-affinity and response-model failures as explicit
   `not_certified` answer states rather than conditioning them away.
6. Audit all zero-probability support cases; infinite KL cannot be silently
   passed to the numerical LP.
7. Separate outcome-independent design computation from any simulated
   sequential run.
8. Freeze query costs or a cost-sensitivity family before interpreting the
   optimal allocation.

## Claim boundary

The present code validates only the finite max-min information calculation
and its planted channel controls. It does not provide a new
pure-exploration theorem, a finite-sample upper bound, a real behavioral
model, a general reward-identifiability result, or a resolution of ASMP-9.
