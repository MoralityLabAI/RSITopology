# ASMP-9 finite-sample coherence protocol v0.9

## Status

Prospective CPU-only verification protocol. All theorem examples, unit-test
fixtures, seeds `909100` through `909105`, and the 1,024-replicate development
pilot are burned.

## Frozen estimand

For a fixed directed comparison graph, each edge receives `n` independent
Bernoulli comparisons. The population log-odds edge flow is scalar-coherent
exactly when every row of the deterministic fundamental-cycle matrix has zero
circulation.

The instrument uses a Bonferroni-uniform Hoeffding event over edge
probabilities, a registered probability-interior admission, and the logit's
interior Lipschitz constant to construct simultaneous cycle bands.

It returns exactly one of:

```text
certified_coherent_within_tolerance
certified_incoherent
inconclusive
unavailable_no_cycles
unavailable_probability_floor
unavailable_no_edges
```

Failure to certify either pole must remain `inconclusive`. A graph with
`beta_1=0` must remain unavailable.

## Frozen constants

```text
familywise alpha          = 0.05
probability floor         = 0.10
coherent tolerance        = 0.50
incoherent margin         = 0.60
planted circulation       = +/-1.20
replicates per cell       = 4,096
sample-bound multipliers  = 0.125, 0.25, 0.5, 1.0, 2.0
```

For every graph, the per-edge sample bound is derived before sampling from:

```text
delta_n <= min(
  d_p/2,
  eta(1-eta)/(2 k_max)
    * min(epsilon_coherent, Delta-epsilon_incoherent)
).
```

No empirical crossover is substituted for that bound.

## Fresh graphs and seeds

The fresh cells use:

| graph | seed | expected beta_1 | maximum fundamental-cycle length |
|---|---:|---:|---:|
| `cycle_3` | 990901 | 1 | 3 |
| `cycle_4` | 990902 | 1 | 4 |
| `cycle_6` | 990903 | 1 | 6 |
| `cycle_8` | 990904 | 1 | 8 |
| `theta_4` | 990905 | 2 | 4 |
| `complete_5` | 990906 | 6 | 3 |

The coherent arm has every true edge probability equal to `1/2`. The planted
arm adds `+1.2` log-odds to the first deterministic chord. Its sign-mirror
uses complementary counts and therefore supplies an exact implementation
symmetry control rather than an independent power estimate.

Forest control seed `990920` and probability-floor control seed `990921` are
fresh.

## Gates

- **G0 registration binding:** the registration commit, implementation
  ancestry, tracked-tree cleanliness, and every sealed hash agree.
- **G1 graph and bound arithmetic:** each graph has the frozen `beta_1` and
  maximum cycle length; every integer sufficient bound clears the analytic
  inequality and `n-1` does not.
- **G2 forest non-vacuity:** every forest replicate returns
  `unavailable_no_cycles`.
- **G3 probability-floor admission:** on every simultaneous event in the
  out-of-interior control, the result is `unavailable_probability_floor`.
- **G4 certificate safety:** on the simultaneous event, no coherent truth is
  certified incoherent and no planted alternative is certified coherent.
- **G5 sufficient-bound liveness:** at every multiplier at least `1.0`, every
  simultaneous-event sample returns its expected certificate.
- **G6 low-budget inconclusiveness:** at multiplier `0.125`, the one-sided 99%
  Clopper-Pearson lower bound on the inconclusive fraction exceeds `0.90` for
  every graph and arm.
- **G7 high-budget decisiveness:** at multipliers at least `1.0`, the
  one-sided 99% Clopper-Pearson lower bound on the expected-certificate
  fraction exceeds `0.99` for every graph and arm.
- **G8 sign mirror:** positive and negative planted arms have byte-equal
  status-count dictionaries in every cell.
- **G9 status closure:** every emitted status belongs to the frozen output
  set.

All gates passing yields:

```text
finite_sample_cycle_coherence_certificate_verified
```

## Claim boundary

This validates a conservative simultaneous certificate for independent,
fixed-count Bernoulli comparisons on six planted finite graphs. It is not a
minimax sample-complexity theorem, adaptive allocation result, human-response
model, unknown-link estimator, general IRL theorem, or ASMP-9 resolution.
Clopper-Pearson is used only to gate Monte Carlo liveness, not to create the
scientific cycle bands.

## Resources

CPU only; 2 GiB RAM; 180 seconds; no GPU.
