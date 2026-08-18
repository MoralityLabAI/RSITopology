# ASMP-9 coupled shared-channel protocol v0.46

## Status and development disclosure

This protocol freezes the disjoint `N=66` confirmation. The `N=60` shared
channel census was computed while developing the symbolic compiler and is
burned. It selected `(26,17,17)` for four-class loss and `(58,1,1)` for
root-group loss. Neither its endpoints nor its allocation decisions may
satisfy a v0.46 confirmation gate.

## Frozen universe

- Four targets.
- Binary queries `(root,left,right)` with deterministic signatures inherited
  from v0.41.
- Horizon two and the complete adaptive policy class.
- One shared symmetric flip rate per query.
- Zero observed known-target calibration errors.
- Simultaneous familywise level `alpha=0.05`.
- Method-of-types toll

  ```text
  kappa(n) = ceil_1e-12(log(3(n+1)/0.05)/n).
  ```

- Exact shared rate bound

  ```text
  p_max(n) = min(1/2, 1-exp(-kappa(n))),
  ```

  enclosed by an exact rational interval and rounded outward to `1e-12`.
- Total confirmation budget `N=66`, with at least one sample per query.
- Exactly `C(65,2)=2,080` labelled positive allocations per decision
  problem.

## Decision problems

1. `4_class_identification`: zero-one loss on all four targets.
2. `root_group`: zero-one loss for `{0,1}` versus `{2,3}`.

The inherited v0.45 rectangle is evaluated on the same allocation universe.
For the classification problem, every allocation receives the inherited exact
robust-deficiency LP. For root-group loss, the structurally exact v0.45 closed
form is exhausted over all allocations.

## Frozen predictions

Extrapolating the burned `N=60` allocation pattern gives:

```text
coupled four-class optimum : (28,19,19)
coupled root-group optimum : (64,1,1)
rectangular four-class     : (28,19,19)
rectangular root-group     : (64,1,1)
uniform reference          : (22,22,22).
```

The primary structural prediction is:

```text
coupled endpoint < rectangular endpoint
```

for both decision problems at their coupled optimum and at uniform
allocation. The allocation-agreement prediction is separate: a strict
endpoint improvement does not logically require the integer optimizer to
change.

## Product-family control

A two-generator, two-target family has four independently variable generator
coordinates. All 16 vertices are realizable and are enumerated exactly. The
exact product supremum must equal the inherited rectangular upper endpoint.
This control distinguishes shared-parameter coupling from an implementation
artifact.

## Gates

Every gate is deterministic.

| Gate | Frozen requirement |
|---|---|
| `P0` | exactly 21 dedicated tests pass |
| `S0` | all registered source, protocol, theorem, prior-art, environment, runner, test, verifier, and inherited-source hashes match |
| `U0` | exactly 2,080 positive allocations per decision problem; totals and query order exact |
| `E0` | 3,748 unique degree-two policy polynomials; inherited compiler agreement on all registered spot checks |
| `X0` | every exponential bracket is outward, no wider than `1e-15` before grid rounding, and every probability bracket is no wider than `1e-12` |
| `B0` | every allocation receives a certified lower bound; the selected allocation receives exact lower and upper LP certificates; no competitor overlaps its upper endpoint after allowed exact sharpening |
| `C0` | coupled four-class optimum is uniquely `(28,19,19)` |
| `G0` | coupled root-group optimum is uniquely `(64,1,1)` |
| `R0` | exact rectangular optima are uniquely `(28,19,19)` and `(64,1,1)` |
| `K0` | the coupled upper endpoint is strictly below the rectangular exact endpoint for both losses at the coupled optimum and uniform allocation |
| `O0` | the exact coupled-versus-rectangular allocation comparison is reported; predicted outcome is no change |
| `PC0` | all 16 product-control vertices are evaluated and the product supremum equals the rectangular upper |
| `RESOURCE` | wall time at most 600 seconds, aggregate working set at most 1.5 GiB, at most four rectangle-audit workers |

`P0`, `S0`, `U0`, `E0`, `X0`, `B0`, and `PC0` are instrument-validity
gates. Failure returns `invalid_coupled_instrument`. A valid instrument with a
failed endpoint or allocation prediction returns
`coupled_prediction_not_established` and preserves the exact result. Only all
gates passing returns `coupled_image_conservatism_established_allocation_unchanged`.

## Reproducibility

The confirmation writes:

- all coupled allocation-bound rows and their canonical hash;
- the inherited exact rectangle audit and its canonical hash;
- the summarized gate/result object;
- a run receipt binding every input and output;
- an independent replay result; and
- a release manifest.

The independent verifier recomputes the scientific payload and requires exact
agreement after removing runtime-only fields.

## Claim boundary

The result concerns one finite iid, zero-error, three-parameter symmetric-flip
grammar. It does not establish a general nonrectangular robust-control theorem,
efficient policy search, minimax confidence constants, strategic or adaptive
misspecification robustness, a real preference channel, or resolution of
ASMP-9.

