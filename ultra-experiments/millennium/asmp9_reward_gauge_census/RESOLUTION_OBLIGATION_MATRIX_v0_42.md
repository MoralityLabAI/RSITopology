# ASMP-9 resolution-obligation matrix after v0.42.1

## Verdict

**ASMP-9 remains unresolved.**

Version v0.42.1 adds a confidence-valid finite-sample layer to the exact
finite-horizon object from v0.41. On one simultaneous channel event:

```text
finite channel confidence set
  -> uniform risk radius for every adaptive policy tree
  -> confidence interval for directed deficiency
  -> pass / fail / inconclusive access decision.
```

The theorem is general over finite target, query, outcome, action, and
fixed-horizon registries. The registered run confirms the complete pipeline on
one synthetic iid binary-channel fixture.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.42.1 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Correct maximal identifiability object | v0.36-v0.39 separate confusability, quotient, deficiency, leakage, and alignment; v0.40-v0.42 use static/adaptive upper risk polytopes with confidence-valid perturbation | **Sharp for finite registered decision types, finite experiments, and fixed horizons** | Continuous/compact classes, history-dependent reward, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | v0.40 exact static containment; v0.41 adaptive Bellman containment; v0.42.1 finite-sample three-state certificate | **Complete for finite known channels; confidence-valid sufficient/insufficient decisions for iid estimated channels when bounds clear** | Unbounded horizons, interventions changing later channel laws outside the controlled experiment, continuous classes, and strategic response |
| 3. Sharp query, sample, and intervention-order bounds | Exact special-case rates, Test Cover boundary, adaptive/open-loop gap, and v0.42 upper sample rate | **Finite upper certificate established** | Matching minimax lower rates, sharp horizon dependence, optimal confidence regions, and efficient policy-search/approximation guarantees |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses | **Partial and mostly synthetic** | Uniform robust transfer or matching no-go theorems under correlated/adaptive/strategic nuisance and a valid physical channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | A complete scalar-versus-relation-versus-no-object classification with replacement objects |

## What v0.42.1 establishes

If all registered finite-channel cells satisfy simultaneous TV bounds
`eta(theta,q)`, then every horizon-`h` adaptive policy has target-wise risk
error at most:

```text
b(theta)
  = loss_span(theta)
    min(1, h max_q eta(theta,q)).
```

The directed deficiency between a sampled source and reference is therefore
within:

```text
max_theta [b_source(theta) + b_reference(theta)]
```

of its population value. This produces a total strict-boundary access rule:

```text
upper < tolerance - margin -> pass
lower > tolerance + margin -> fail
otherwise                  -> inconclusive.
```

The registered 48,000-sample fixture passed all nine gates and the independent
exact replay.

## What v0.42.1 does not establish

- The `h max eta` coupling/union bound is not proved sharp.
- The resulting `O(h^2/g^2)` sufficient sample rate has no matching lower
  bound.
- Bonferroni/Hoeffding-Weissman regions are not optimal multinomial
  confidence sets.
- Exact policy-tree compilation remains exponential.
- Samples are iid from a fixed synthetic channel.
- No source adapts strategically to the query policy.
- No real behavioral or model channel has passed calibration.

## Fixed resolution-directed sequence

1. **Completed through v0.42.1:** finite decision-relative object; static and
   adaptive known-channel characterization; simultaneous iid finite-sample
   access certificate.
2. Derive the sharp local modulus of directed deficiency under channel
   perturbations.
3. Either prove a matching lower rate for deciding access across a positive
   margin, or replace the horizon union bound with the sharper recursion the
   lower witness demands.
4. Add a frozen correlated/adaptive/strategic misspecification neighborhood
   and prove robust transfer or a matching impossibility.
5. Extend the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered,
   calibrated channel.

## Next load-bearing target

Version v0.43 should not add another sample size to the same fixture. It should
resolve whether:

```text
n = Theta(h^2 / g^2)
```

is genuinely necessary for finite-horizon access certification at containment
gap `g`, or is an artifact of applying `h max eta` before the Bellman geometry
is considered.

A valid outcome is either:

1. a two-point finite experiment whose access deficiency changes by
   `Theta(h delta)` while the per-sample channel divergence is
   `Theta(delta^2)`, yielding a matching lower bound; or
2. a strictly sharper policy-uniform dynamic perturbation theorem and an
   explicit witness showing the v0.42 horizon factor is loose.

## Claim boundary

Version v0.42.1 composes classical concentration and simulation ingredients
into the ASMP-9 finite adaptive access object. It closes a finite iid
confidence-certificate gap, not the broader reward/value identifiability
problem.
