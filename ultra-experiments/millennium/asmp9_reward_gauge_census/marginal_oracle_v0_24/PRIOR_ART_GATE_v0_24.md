# ASMP-9 v0.24 prior-art gate

Status: development-only.  Complete before any prospective freeze.

## Results that own the ingredients

1. François Jaeger, Dirk L. Vertigan, and Dominic J. A. Welsh,
   ["On the computational complexity of the Jones and Tutte
   polynomials"](https://doi.org/10.1017/S0305004100068936),
   *Mathematical Proceedings of the Cambridge Philosophical Society* 108(1)
   (1990), 35-53.  Their dichotomy supplies the #P-hard Tutte evaluations
   inherited through v0.21 and v0.22.1.
2. Spencer Backman,
   ["Partial Graph Orientations and the Tutte
   Polynomial"](https://arxiv.org/abs/1408.3962), supplies the weighted
   partial-orientation/Tutte framework inherited through v0.22.
3. Alan D. Sokal,
   ["The multivariate Tutte polynomial (alias Potts model) for graphs and
   matroids"](https://arxiv.org/abs/math/0503607), supplies the classical
   multivariate random-cluster object used in v0.23.
4. Guy Bresler, David Gamarnik, and Devavrat Shah,
   ["Hardness of parameter estimation in graphical
   models"](https://arxiv.org/abs/1409.3836), is relevant methodological
   ancestry for recovering hard partition-function information from
   marginal/mean access.  Its model, approximation regime, and reduction are
   not the theorem proposed here.
5. Partition-function self-reduction and rational polynomial interpolation
   are standard techniques.  No novelty is claimed for the general principle
   that sufficiently rich exact marginal or ratio access can recover a
   normalizing constant.

## Reliability-allocation literature checked

Targeted searches on 2026-07-28 found broad redundancy-allocation and network
reliability optimization papers, including series-parallel component-mixing
models, multistate flow networks, correlated failures, and simultaneous
cost/reliability choices.  Those problems add component types, costs, weights,
capacities, or topology choices and are commonly labeled NP-hard.  None of
the inspected formulations matched all of the frozen ASMP object:

```text
fixed simple biconnected topology
+ identical fair Bernoulli repetitions
+ positive integer count allocation
+ fixed total count
+ strong residual-orientation availability.
```

Their hardness statements must not be imported into this problem.

## Proposed narrow contribution

The proposed v0.24 statement is an access-model translation:

```text
exact per-edge marginal ratios
  -> telescoped uniform-round ratios
  -> normalized availability polynomial
  -> count-floor T_G(0,2)
  -> #P-hard exact value.
```

The `P_G(0)=1` normalization is the step that makes ratios value-complete.
The claim is elementary once the predecessor chain is available.

## Allowed language

- exact one-edge marginal-ratio computation is #P-hard under polynomial-time
  Turing reductions on the declared biconnected-block domain;
- `m^2` exact local ratios reconstruct the entire uniform availability
  polynomial;
- exact local improvement values are not an efficient substitute for the
  v0.23 objective oracle unless FP=#P; and
- the theorem advances the optimizer-access boundary.

## Forbidden language

- optimizer search is NP-hard or #P-hard;
- comparing two marginal ratios is #P-hard;
- approximate marginal estimation is hard;
- greedy allocation cannot be implemented approximately;
- the generic marginal-to-partition-function principle is new; or
- the result resolves ASMP-9.

## Search still required before freeze

Before registration, inspect primary sources specifically for exact
random-cluster/Tutte edge-marginal oracle complexity and for reliability
allocation on fixed networks with identical parallel repetitions.  If the
same ratio-interpolation theorem is explicit, cite it and present v0.24 only
as the ASMP access translation.

