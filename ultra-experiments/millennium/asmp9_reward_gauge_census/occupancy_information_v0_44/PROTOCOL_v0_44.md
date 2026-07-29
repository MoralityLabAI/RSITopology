# ASMP-9 v0.44 policy-specific information protocol

## Status

Prospective deterministic theorem confirmation. The perturbation grid,
decision problems, gates, and row counts are frozen before the confirmation
artifact is generated.

## Question

Can finite-sample channel uncertainty be propagated through directed
deficiency without assigning every risk generator the uncertainty of the
worst admissible policy?

## Frozen objects

### Query library

The deterministic v0.41 four-target tree:

```text
root=(0,0,1,1)
left=(0,1,0,0)
right=(0,0,0,1)
horizon=2.
```

The root remains exact. Left and right receive symmetric flip probability:

```text
eta={1/100,1/50,1/20,1/10}.
```

Cell information costs are the exact rational chi-square upper bounds on
directed KL from the deterministic center to the perturbed channel.

### Decision problems

1. four-class zero-one identification;
2. binary root-group zero-one identification.

Perfect revelation is the exact reference in both primary controls.

### Robust-box control

A separate two-target rational risk registry exhausts:

- eight selected source-box vertices with exact reference; and
- all 64 source/reference-box sign vertices.

Every exact deficiency must lie inside the generator-specific robust interval.

### Query-budget control

For one uncertain repeatable query at horizon two:

```text
unrestricted maximum information = 2/19
one-use path budget maximum       = 1/19.
```

## Gates

- `P0`: the exact pytest invocation reports 20 passing tests.
- `S0`: every registered source, inherited compiler, environment, runner, and
  verifier hash matches.
- `C0`: center envelope risks and the inherited v0.41 compiler are
  deficiency-equivalent for both decision problems.
- `X0`: the unrestricted policy-information supremum exactly equals
  `h max kappa`, recording the scalar-collapse control.
- `B0`: all registered source/reference box vertices lie inside their exact
  robust intervals.
- `Q0`: the one-use query-budget control reduces maximum information from
  `2/19` to `1/19`.
- `I0`: for all four perturbation levels, each actual four-class deficiency
  lies inside the policy-specific interval and its upper endpoint is strictly
  below the uniform endpoint.
- `D0`: for all four perturbation levels, root-group actual deficiency and
  policy-specific interval are exactly zero while the uniform upper endpoint
  is positive.
- `R0`: the artifact contains exactly two center rows, four classification
  rows, four root-group rows, eight exact-source box rows, 64
  source/reference box rows, and one query-budget row.
- `RESOURCE`: elapsed time is at most 120 seconds and peak process working set
  is at most 768 MiB.

All gates must pass for:

```text
policy_specific_information_containment_established.
```

A provenance mismatch returns `invalid_provenance`. A resource failure returns
`resource_gate_failed`. Any other gate failure returns
`theorem_or_implementation_failure`.

## Claim boundary

This is an exact finite composition of classical policy occupancy,
chain-rule/Pinsker, robust optimization, and comparison-of-experiments
ingredients. It does not establish optimal statistical confidence regions,
sharp deficiency moduli for every finite library, efficient policy search,
nonrectangular or strategic uncertainty, real reward/value identification, or
an ASMP-9 resolution.
