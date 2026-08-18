# ASMP-9 resolution-obligation matrix after v0.39

## Verdict

**ASMP-9 remains unresolved.**

Version v0.39 completes the first item in the fixed sequence recorded after
v0.38: it moves from target-independent to target-correlated gauge selection
and separates observational leakage from an intervention that randomizes the
selection mechanism.

The resulting finite hierarchy is:

```text
decision-preserving reward transformation
  < target-independent ancillary assignment
  < target-aligned decision access
  < full target-by-nuisance reconstruction.
```

Neither “gauge” nor a scalar information score determines the correct access
class by itself.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.39 | Status | Missing resolution evidence |
| --- | --- | --- | --- |
| 1. Correct maximal identifiability object for each registered data source | Exact shaping quotients; v0.36 confusability relation/components; v0.37 risk-vs-expanded separation; v0.38 decision-relative comparison; v0.39 assignment-law and access-alignment separation | **Partial; four distinct objects are now separated** | Maximal classification for broad stochastic, history-dependent, strategic, non-expected-utility, and model-generated sources |
| 2. Necessary and sufficient queries/interventions | Sharp cycle, ordinal, MDP, offset, occupancy, and gluing cases; v0.38 half-gap threshold; v0.39 exact correlated-gauge leakage and aligned/intervened access values | **Sharp in multiple restricted grammars** | One theorem over broad compact reward/response classes, arbitrary finite channels, adaptive access, and interventions on the generating mechanism |
| 3. Sharp query, sample, and intervention-order bounds | Earlier exact widths/sample bounds plus v0.38–v0.39 zero- and positive-tolerance access values | **Substantial finite special cases** | Joint minimax complexity for recovering the decision-relative object under adaptive acquisition, dependence, and misspecification |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, approximate propagation, stochastic witnesses | **Partial and mostly synthetic** | Uniform robust transfer or matching no-go theorems over correlated/strategic nuisance and a valid physical measurement channel |
| 5. No-go theorem when no coherent latent value object exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | Two-sided classification of scalar, relational, and no-stable-target regimes with the correct replacement object |

## What v0.39 establishes

For an observed representative-selection bit with target-indexed Bernoulli
probabilities `p_theta`,

```text
delta_D(constant, observed gauge)
  = delta(constant, observed gauge)
  = (max p_theta - min p_theta)/2.
```

The reverse deficiencies are zero. Target-independent stochastic
intervention makes the value zero.

For equal-radius channels beside retained query `q1`, relative to `(q0,q1)`:

```text
aligned q0:     0
redundant q1:   (high-low)/2
transverse q2:  high*low*(high-low)
intervened:     (high-low)/2.
```

All ten gates passed on 25 disjoint confirmation rows, and an independent
exact replay revalidated all fifteen sealed inputs and every mathematical
identity.

## What v0.39 does not establish

- The binary gauge assignment is not a general reward-learning process.
- Target correlation need not be causal or stable under environment change.
- Randomizing the gauge variable erases information here; it does not
  generally improve identification.
- The scalar half-range does not classify arbitrary channel alignment.
- The three-policy zero-one loss is not a human-value model.
- No physical or transformer measurement channel is validated by this run.

## Fixed resolution-directed sequence

1. **Completed in v0.39:** correlated gauge assignment, observational leakage,
   and intervention-induced ancillarity.
2. Characterize decision-relative access alignment for arbitrary finite
   channels and broader finite policy-loss types, including when a
   channel/garbling, quotient, or convex-order representation exists.
3. Derive matching adaptive query and finite-sample bounds for recovering
   that comparison object rather than a raw reward vector.
4. Add a frozen misspecification neighborhood and prove robust transfer or a
   matching impossibility.
5. Extend the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered
   channel that passes availability and calibration gates.

## Claim boundary

The mathematical ingredients are classical. Version v0.39 contributes an
exact reward-access specialization and a disjoint confirmation of its
alignment-sensitive threshold. Neither it nor the accumulated finite suite
resolves ASMP-9.
