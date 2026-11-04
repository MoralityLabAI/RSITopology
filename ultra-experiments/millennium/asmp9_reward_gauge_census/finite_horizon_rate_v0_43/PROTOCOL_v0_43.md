# ASMP-9 v0.43 finite-horizon rate protocol

## Status

Prospective deterministic theorem confirmation. No stochastic sample outcome
is used. The grids below are frozen before the confirmation artifact is
generated.

## Question

Is the `O(h^2/g^2)` sample floor in v0.42.1 intrinsic to finite-horizon
decision-relative access?

## Registered answer shape

The protocol can establish only the following scoped answer:

1. under a per-step directed KL bound `kappa`, every adaptive policy's bounded
   terminal risk moves by at most `sqrt(h kappa / 2)` times the loss span;
2. therefore a risk separation of order `h delta` is incompatible with
   one-step KL of order `delta^2` uniformly in `h`;
3. on the registered binary sentinel family, the exact deficiency has a
   two-point lower certificate of order `h/g^2`; and
4. an all-zero block estimator achieves order
   `h log(1/alpha)/g^2`.

The intended status is
`finite_horizon_rate_characterization_established` only if every gate below
passes.

## Frozen universes

### Exact compiler agreement

```text
horizons = {1,2,3,4,5,6}
p = {0, 1/8, 1/4, 1/3, 1}
```

For all 30 cells, the closed form `D_h(p)` must exactly equal the v0.41
Bellman/LP compiler's directed deficiency to perfect revelation.

### Two-point certificates

```text
horizons = {2,3,4,8,16,32,64,128}
epsilon = {1/32,1/16,1/8,1/4}
```

All 32 cells must satisfy, in exact rational arithmetic:

```text
epsilon/16 <= deficiency_gap <= epsilon
chi_square <= 4 epsilon^2 / h
```

and emit the first sample size not ruled out by the Pinsker/Le Cam
certificate.

### No-linear-witness sequence

```text
horizons = {2,8,32,128}
C = 4
```

The bound `sqrt(C/(2h))` on
`risk_gap/(h delta)` must decrease strictly and the final value must be at
most one eighth of the first.

### Block upper-rate table

```text
horizons = {8,16,32,64,128}
gaps = {1/32,1/16,1/8}
alpha = 0.05
```

For each gap, the required block count must be identical across horizons, the
raw sample count must equal `h * blocks`, every radius must be strictly below
the gap, and `n g^2 / h` must be horizon-invariant up to binary-float
serialization.

## Gates

- `P0`: the exact preregistration pytest invocation reports 75 passing tests.
- `S0`: registration, environment, source, test, theorem, protocol,
  prior-art, runner, and verifier hashes match.
- `E0`: all 30 closed-form/compiler comparisons match exactly.
- `L0`: all 32 two-point exact certificates satisfy the frozen inequalities.
- `K0`: the four no-linear-witness ratios satisfy the frozen decay rule.
- `U0`: all 15 block-rate rows satisfy the frozen linear-horizon rule.
- `R0`: the artifact contains exactly 30 compiler, 32 lower-bound, 4
  no-witness, and 15 upper-bound rows.
- `RESOURCE`: elapsed time is at most 120 seconds and peak process working set
  is at most 512 MiB.

Any failed scientific gate returns
`theorem_or_implementation_failure`. A provenance mismatch returns
`invalid_provenance`. Resource failure returns `resource_gate_failed`.

## Claim boundary

This is a deterministic exact confirmation of an ASMP-9 specialization of
classical comparison-of-experiments, chain-rule/Pinsker, two-point, and
Hoeffding arguments. It does not establish optimal rates for all adaptive
experiments, arbitrary multinomial confidence sets, strategic or correlated
sources, real behavioral channels, or a resolution of ASMP-9.
