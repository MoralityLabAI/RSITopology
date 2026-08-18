# ASMP-9 resolution-obligation matrix after v0.40

## Verdict

**ASMP-9 remains unresolved.**

Version v0.40 completes the arbitrary-finite, registered-loss,
nonadaptive-access step:

```text
access sufficient at epsilon
  iff the full-access risk polytope lies in the
     epsilon-shifted upper risk polytope of that access.
```

The result also identifies a hard boundary: deterministic zero-error
classification access is exactly Minimum Test Cover, so finding the smallest
access family is NP-hard in general even before sampling, unknown links, or
strategic demonstrators enter.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.40 | Status | Missing resolution evidence |
| --- | --- | --- | --- |
| 1. Correct maximal identifiability object | Quotients, confusability relations, v0.37 separation, v0.38 relative deficiency, v0.39 alignment, and now the complete finite upper-risk-polytope object | **Sharp for arbitrary finite experiments relative to a registered finite loss type** | Continuous/compact classes, history dependence, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | Earlier sharp special cases; v0.39 observational/interventional separation; v0.40 exact subset criterion and complete tolerance antichain for any finite registry | **Complete for finite nonadaptive registered channels by exhaustive compilation** | Adaptive/sequential policies, interventions changing the data-generating process, unknown channels, and uniform infinite-class theorems |
| 3. Sharp query, sample, and intervention-order bounds | Exact finite widths/sample results; v0.40 Test Cover equivalence and NP-hard minimum-access boundary | **Structural complexity boundary established; many finite rates known** | Approximation/adaptive bounds for risk-polytope recovery, finite-sample channel estimation, and matching minimax rates under dependence |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses | **Partial and mostly synthetic** | Uniform robust transfer or matching no-go theorems over correlated/strategic nuisance and a valid physical channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | A two-sided scalar-versus-relation-versus-no-object classification with replacement objects |

## What v0.40 establishes

For every finite registered decision type `D`:

```text
delta_D(E,F)
  = inf {epsilon:
         R_d(F) subset
         R_d(E)+R_+^Theta+epsilon*1
         for every d in D}.
```

Thus every finite query subset has an exact necessary-and-sufficient access
certificate, and the inclusion-minimal access families form an antichain at
each tolerance.

For deterministic zero-one classification:

```text
delta_D = 1 - 1/(largest unresolved block size),
delta_D=0 iff access is a Test Cover.
```

For asymmetric binary group losses, a mixed block costs exactly
`c_fp*c_fn/(c_fp+c_fn)`. The disjoint confirmation showed that changing only
the loss type changed both zero-tolerance access and the full persistence
curve. All ten gates passed and an independent replay checked 64 rows.

## What v0.40 does not establish

- Exhaustive finite compilation is not an efficient general algorithm.
- Minimum exact access is NP-hard in the Test Cover special case.
- The registered decision type is assumed known and fixed.
- Query channels are known, nonadaptive, and population-level.
- No finite-sample estimation or channel uncertainty is included.
- No real-model measurement channel is validated.

## Fixed resolution-directed sequence

1. **Completed through v0.40:** correct finite decision-relative object,
   correlated-gauge/intervention separation, and arbitrary finite
   nonadaptive access characterization.
2. Extend risk-polytope access to adaptive query policies and derive
   approximation or hardness bounds beyond static Test Cover.
3. Add finite-sample channel estimation with matching confidence-valid upper
   and lower access certificates.
4. Add a frozen misspecification neighborhood and prove robust transfer or a
   matching impossibility.
5. Extend the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered
   calibrated channel.

## Claim boundary

All comparison and Test Cover ingredients are classical. Version v0.40
consolidates them into an exact ASMP-9 finite access compiler and confirms
decision-type dependence. The broader candidate problem remains open.
