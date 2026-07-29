# ASMP-9 resolution-obligation matrix after v0.43

## Verdict

**ASMP-9 remains unresolved.**

Version v0.43 closes the first rate question raised by v0.42.1. The
`O(h^2/g^2)` sample floor obtained by combining a root-`n` TV estimate with
an `h eta` union bound is not intrinsic on the registered sentinel family.
The correct exponent there is:

```text
n = Theta(h/g^2)
```

at fixed confidence. A general KL chain-rule argument also proves that the
specific proposed witness—`Theta(h delta)` risk motion with
`Theta(delta^2)` one-step KL—cannot exist uniformly in `h`.

## Canonical question

> What preference-query and environment-intervention access is necessary and
> sufficient to identify a reward or value model up to exactly the
> transformations that preserve the declared decision problem?

## Obligation ledger

| Obligation | Strongest evidence after v0.43 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Correct maximal identifiability object | v0.36-v0.39 separate confusability, quotient, deficiency, leakage, and alignment; v0.40-v0.43 use static/adaptive upper risk polytopes with confidence and rate layers | **Sharp for finite registered decision types, finite experiments, and fixed horizons** | Compact classes, history-dependent reward, strategic sources, non-expected-utility targets, and unknown decision type |
| 2. Necessary and sufficient queries/interventions | v0.40 exact static containment; v0.41 adaptive Bellman containment; v0.42.1 finite-sample three-state certificate | **Complete for finite known channels; confidence-valid sufficient/insufficient decisions for the registered iid estimator** | Unbounded horizons, interventions changing future laws outside the controlled experiment, continuous classes, and strategic response |
| 3. Sharp query, sample, and intervention-order bounds | Exact special-case query rates, adaptive/open-loop gap, v0.42 upper certificate, and v0.43 matching `h/g^2` sentinel exponents | **Sharp on the sentinel family; incomplete in general** | Minimax modulus over arbitrary finite channel libraries, cell-allocation dependence, optimal confidence regions, and efficient policy-search guarantees |
| 4. Robustness to behavioral misspecification | Unknown-link obstructions, coherence tests, robust gluing, stochastic witnesses | **Partial and mostly synthetic** | Uniform robust transfer or matching no-go theorems under correlated/adaptive/strategic nuisance and a valid physical channel |
| 5. No-go when no coherent latent value exists | Non-affine-link, context, ordinal, mechanics, interaction, and confusability witnesses | **Many named no-go instances** | A complete scalar-versus-relation-versus-no-object classification with replacement objects |

## What v0.43 establishes

### Policy-uniform regular-channel modulus

If each target/query cell satisfies:

```text
KL(P(.|theta,q) || P_hat(.|theta,q)) <= kappa(theta),
```

then every horizon-`h` adaptive policy with target-wise loss span `s(theta)`
satisfies:

```text
|R_pi(theta)-R_hat_pi(theta)|
  <= s(theta) min(1, sqrt(h kappa(theta)/2)).
```

### Impossibility of the proposed witness

Under `KL <= C delta^2`:

```text
risk_gap/(h delta) <= sqrt(C/(2h)).
```

Thus a uniform `Omega(h delta)` bounded-risk gap is incompatible with
quadratic one-step KL.

### Sharp sentinel exponents

For the exact repeated binary sentinel:

```text
D_h(p) = (1-p)^h / (1+(1-p)^h).
```

An exact two-point certificate yields `Omega(h/g^2)`, while an all-zero block
estimator yields `O(h log(1/alpha)/g^2)`. At fixed confidence, the horizon and
gap exponents match.

## What v0.43 does not establish

- `Theta(h/g^2)` is not proved minimax over all finite adaptive experiments.
- The worst-cell KL radius may still be loose when policy occupancy avoids
  uncertain cells.
- No sharp simultaneous directed-KL confidence region is supplied for
  arbitrary multinomial cells, especially at support boundaries.
- Exact policy-tree compilation remains exponential.
- Samples remain iid from a fixed synthetic channel.
- No source adapts strategically to the query policy.
- No real behavioral or model channel has passed calibration.

## Fixed resolution-directed sequence

1. **Completed through v0.43:** finite decision-relative object; static and
   adaptive known-channel characterization; simultaneous iid finite-sample
   certificate; sharp horizon/gap exponents on a sentinel family.
2. Replace `h max_q kappa(theta,q)` with the exact
   policy-occupancy-weighted information radius for an arbitrary finite
   channel library.
3. Prove a matching minimax lower construction for that general finite
   radius, or exhibit a finite library where another modulus is required.
4. Add a frozen correlated/adaptive/strategic misspecification neighborhood
   and prove robust transfer or a matching impossibility.
5. Extend the scalar-versus-relation-versus-no-object trichotomy.
6. Re-enter real-model measurement only through a prospectively registered,
   calibrated channel.

## Next load-bearing target

Version v0.44 should not add another sentinel or confidence sample size. It
should characterize the finite-library information radius:

```text
I_h(theta)
  = sup_pi
      E_P_pi [
        sum_{t=1}^h
          kappa(theta, q_t(H_{t-1}))
      ].
```

The chain rule already gives:

```text
risk radius <= loss_span sqrt(I_h(theta)/2).
```

The unresolved questions are:

1. whether the supremum can be compiled by a Bellman recursion jointly with
   the risk polytope;
2. whether the resulting radius is sharp for directed deficiency rather than
   only for fixed-policy risk;
3. how sample allocation across channel cells changes the minimax rate; and
4. whether a matching two-point construction can attain the
   occupancy-weighted bound.

This moves the rate question from a scalar horizon penalty to the exact
queries an admissible policy can actually visit.

## Claim boundary

Version v0.43 composes classical information inequalities into the ASMP-9
finite adaptive access object and corrects one rate exponent on an exact
family. It does not resolve arbitrary finite experiments, behavioral
misspecification, real reward/value identification, or ASMP-9.
