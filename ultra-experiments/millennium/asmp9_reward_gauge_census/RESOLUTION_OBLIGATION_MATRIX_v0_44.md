# ASMP-9 resolution-obligation matrix after v0.44

## Verdict

**ASMP-9 remains unresolved.**

Version v0.44 closes the policy-occupancy composition target from the v0.43
matrix, after correcting its scalar formulation. With repeatable queries:

```text
sup_pi I_pi(theta) = h max_q kappa(theta,q),
```

so a pre-optimization occupancy supremum cannot improve the worst-cell bound.
The correct object retains information on each risk-polytope generator and
performs robust containment over generator-specific boxes.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.44 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Correct maximal identifiability object | v0.36-v0.39 separate confusability, quotient, deficiency, leakage, and alignment; v0.40-v0.44 use static/adaptive upper risk polytopes with statistical, rate, and generator-specific robustness layers | **Sharp for finite registered decision types, finite experiments, and fixed horizons** | Compact classes, history-dependent reward, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | v0.40 exact static containment; v0.41 adaptive Bellman containment; v0.42.1 finite-sample three-state certificate; v0.44 exact pathwise query budgets | **Complete for finite known channels and registered iid box certificates** | Unbounded horizons, interventions changing future laws outside the controlled experiment, continuous classes, and strategic response |
| 3. Sharp query, sample, and intervention-order bounds | Exact special-case query rates, adaptive/open-loop gap, v0.43 matching `h/g^2` sentinel exponents, and v0.44 policy-specific information boxes | **Sharp on named families; incomplete in general** | Optimal sample allocation, simultaneous KL-region constants, a general minimax deficiency modulus, and efficient policy-search guarantees |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses, and v0.44 rectangular generator boxes | **Partial and synthetic** | Uniform transfer or matching no-go theorems under correlated/adaptive/strategic nuisance and a valid physical channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | A complete scalar-versus-relation-versus-no-object classification with replacement objects |

## What v0.44 establishes

For each policy `pi`, target `theta`, center risk `r_pi`, and information
occupancy:

```text
I_pi(theta)
  = E_center,pi sum_t kappa(theta,q_t(H_{t-1})),
```

the corresponding perturbed risk lies inside:

```text
r_pi(theta)
  +/- loss_span(theta) min(1,sqrt(I_pi(theta)/2)).
```

For source generator boxes `G_minus,G_plus` and reference boxes
`F_minus,F_plus`:

```text
D(G_minus,F_plus)
  <= D_true
  <= D(G_plus,F_minus).
```

The interval is computed by the existing exact deficiency LP.

On the matched horizon-two fixture:

- four-class policy-specific uncertainty was strictly below uniform
  uncertainty at all four perturbation levels;
- the root-group decision had an exact zero-width certificate because its
  optimal policy avoided every uncertain query;
- 72 source/reference box vertices were contained; and
- the unrestricted maximum-information control exactly collapsed to the
  original `h max kappa` scalar.

## What v0.44 does not establish

- Information tolls are supplied by a known rational chi-square upper bound,
  not inferred through an optimal simultaneous confidence construction.
- The generator boxes may be conservative relative to the exact coupled
  uncertainty image.
- The policy tree enumeration remains exponential.
- No minimax lower theorem matches the general generator-specific interval.
- Channel uncertainty is rectangular and nonstrategic.
- No real behavioral or model channel has passed calibration.

## Fixed resolution-directed sequence

1. **Completed through v0.44:** finite decision-relative object; static and
   adaptive known-channel characterization; finite-sample certificate; sharp
   sentinel rate; generator-specific information/robust-containment layer.
2. Make sample allocation decision-relative: choose cell counts to minimize
   the robust deficiency upper endpoint under a total acquisition budget.
3. Prove a matching lower construction or characterize the gap between
   rectangular generator boxes and the exact uncertainty image.
4. Add a frozen correlated/adaptive/strategic misspecification neighborhood
   and prove robust transfer or a matching impossibility.
5. Extend the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered,
   calibrated channel.

## Next load-bearing target

Version v0.45 should not add another perturbation level. It should freeze a
finite acquisition design:

```text
n(theta,q) >= 0
sum_theta,q n(theta,q) <= N,
```

with simultaneous cell-information bounds `kappa_n(theta,q)`, then solve:

```text
min_n
  robust_deficiency_upper(
    {r_pi, I_pi(kappa_n)}
  ).
```

The decisive controls are:

1. a decision-directed allocation versus uniform allocation at equal total
   samples;
2. two loss types on the same channel library whose optimal allocations
   differ;
3. an oracle allocation lower benchmark;
4. a matched family where every policy uses every cell, forcing equality with
   uniform allocation; and
5. a two-point lower certificate showing whether the achieved allocation rate
   is minimax or merely constructive.

This is the remaining finite sample-complexity frontier before moving to
strategic misspecification.

## Claim boundary

Version v0.44 composes classical information and robust-optimization tools
inside the ASMP-9 finite risk-polytope object. It does not resolve general
sample design, strategic or misspecified demonstrators, real reward/value
identification, or ASMP-9.
