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

1. Replace the illustrative hypothesis table with a finite model generated
   mechanically from v0.28-v0.32 objects.
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

## Claim boundary

The present code validates only the finite max-min information calculation
and its planted channel controls. It does not provide a new
pure-exploration theorem, a finite-sample upper bound, a real behavioral
model, a general reward-identifiability result, or a resolution of ASMP-9.
