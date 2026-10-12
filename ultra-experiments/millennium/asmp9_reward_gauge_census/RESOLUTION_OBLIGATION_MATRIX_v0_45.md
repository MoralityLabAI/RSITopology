# ASMP-9 resolution-obligation matrix after v0.45

## Verdict

**ASMP-9 remains unresolved.**

Version v0.45 closes the finite shared-parameter allocation target from the
v0.44 matrix. It proves that the exact acquisition design depends on the
declared decision loss, while a matched all-query policy recovers uniform
allocation. The result optimizes a registered conservative confidence
objective; its two-point benchmark explicitly does not establish minimaxity.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.45 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Correct maximal identifiability object | v0.36-v0.39 separate confusability, quotient, leakage, alignment, and decision equivalence; v0.40-v0.45 use static/adaptive risk polytopes with statistical and design layers | **Sharp for finite registered decision types and experiments** | Compact classes, history-dependent reward, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | v0.40 exact static containment; v0.41 adaptive Bellman containment; v0.42.1 confidence-valid finite samples; v0.44 pathwise information occupancy; v0.45 exact pooled acquisition design | **Complete for finite known channels and one shared-parameter iid design grammar** | Target-dependent nonparametric cells, unbounded horizons, interventions changing future laws, continuous classes, and strategic response |
| 3. Sharp query, sample, and intervention-order bounds | Exact special-case query rates, adaptive/open-loop gap, v0.43 matching `h/g^2` sentinel exponents, v0.44 policy boxes, and v0.45 exact integer allocation plus a two-point confidence lower benchmark | **Sharp for the registered upper objective; minimax gap remains** | Optimal simultaneous constants, a matching general deficiency lower bound, coupled uncertainty, and efficient policy search |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses, and rectangular generator boxes | **Partial and synthetic** | Correlated/adaptive/strategic nuisance, exact coupled uncertainty images, uniform transfer, and a valid physical channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | Complete scalar-versus-relation-versus-no-object classification with replacement objects |

## What v0.45 establishes

For pooled query counts `n_q` under the shared-flip grammar:

```text
kappa(n_q)
  = ceil_1e-12(log(3(n_q+1)/0.05)/n_q).
```

Every policy generator receives:

```text
I_pi(theta;n)
  = sum_q omega_pi(theta,q) kappa(n_q),

b_pi(theta;n)
  = loss_span(theta)
    min(1,sqrt(I_pi(theta;n)/2)).
```

Exhausting all positive allocations with total 60 gives unique exact optima:

```text
four-class : (26,17,17)
root-group : (58,1,1)
serial     : (20,20,20).
```

The first two improve their robust endpoints over uniform by 1.324% and
37.173%, respectively. The serial control proves that the unequal designs
arise from decision-relative occupancy rather than from the concentration
formula alone.

## What v0.45 does not establish

- Target rows can be pooled only because the frozen grammar shares one
  symmetric flip parameter per query.
- The method-of-types/Pinsker endpoint is confidence-valid but not minimax.
- Generator-wise rectangles ignore that one channel parameter moves many
  policy risks jointly.
- The classification constructive formula is conservative on 1,325 of 1,711
  allocations, although it never underbounds and selects the exact optimum.
- Policy compilation remains exponential.
- No strategic or real behavioral source is present.

## Fixed resolution-directed sequence

1. **Completed through v0.45:** finite decision-relative object; static and
   adaptive known-channel characterization; finite-sample certification;
   sharp sentinel rate; generator-specific information boxes; exact
   shared-parameter integer sample allocation.
2. Replace independent generator rectangles with the exact coupled uncertainty
   image induced by shared channel parameters, and quantify the conservatism
   gap.
3. Prove a matching deficiency lower construction or a sharp modulus for a
   declared finite channel class.
4. Add a frozen correlated/adaptive/strategic misspecification neighborhood
   and prove robust transfer or a matching impossibility.
5. Extend the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered,
   calibrated channel.

## Next load-bearing target

Version v0.46 should freeze a small rational uncertainty polytope for the three
shared flip parameters and compare:

```text
rectangular upper
  = D({r_pi + independent b_pi},F)
```

against the exact joint image:

```text
coupled upper
  = sup_{p in P}
      D({r_pi(p): all pi},F).
```

The experiment must:

1. preserve one common parameter vector across every policy generator;
2. compute the coupled supremum exactly or with certified rational bounds;
3. include a product uncertainty family where rectangles are exact;
4. include a shared-parameter family where rectangles are strictly
   conservative;
5. determine whether the optimal allocation changes when the coupled image
   replaces the rectangular relaxation; and
6. keep a two-point lower benchmark separate from the robust upper.

This is the remaining finite statistical-modulus frontier before strategic
misspecification.

## Claim boundary

Version v0.45 composes classical optimal-design, finite-type concentration,
Pinsker, exact risk-polytope, and two-point-testing tools inside one finite
ASMP-9 grammar. It does not resolve general value identifiability, behavioral
misspecification, real preference access, or ASMP-9.
