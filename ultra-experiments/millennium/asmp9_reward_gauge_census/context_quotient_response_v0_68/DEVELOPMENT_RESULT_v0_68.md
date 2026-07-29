# ASMP-9 context-quotient response development result v0.68

Status: **unregistered development result; not claim eligible**.

## Verdict

The v0.67.1 stop does not require abandoning all physical response
measurement. It requires changing the estimand.

Under an arbitrary additive common-mode nuisance for every fixed
`(scenario, display order, tensor shape)` block:

- absolute baseline signs are not identifiable;
- within-block arm contrasts form a maximal invariant;
- every admissible linear endpoint has coefficients summing to zero inside
  each nuisance block; and
- one global response effect is an additional intersection/generalization
  hypothesis, not a prerequisite for reporting context-local contrasts.

These are classical fixed-effects facts specialized as an ASMP-9 instrument
admission layer.

## Exact development verification

The exact rational implementation passed:

```text
measurement matrices                 729
offset vectors                        25
quotient-invariance checks        18,225
maximality checks                     729
linear-estimand checks                729
pytest tests                           10
```

The planted falsification control is arm-by-order interaction. A valid quotient
must retain it. The implementation does.

## Burned v0.67 construction reanalysis

The v0.68 coordinates were chosen after the v0.67 construction result was
known. The following is therefore design evidence only.

Across 20 scenario-by-target cells:

| Endpoint | Positive in both display orders | Opposed or zero orders | Median order mean | Median order half-range |
|---|---:|---:|---:|---:|
| content effect | 20 / 20 | 0 / 20 | 1.0703 | 0.1563 |
| bare-label effect | 4 / 20 | 16 / 20 | 0.1250 | 0.4844 |
| content-minus-label specificity | 20 / 20 | 0 / 20 | 0.9336 | 0.4648 |
| post-washout effect | 6 / 20 | 14 / 20 | 0.0703 | 0.0938 |

The content and specificity directions are live after forming matched
within-order contrasts, even though the v0.67 absolute baselines were unstable
in every scenario.

The two-order ranges do **not** admit one common scalar across all cells:

| Endpoint | Max lower endpoint | Min upper endpoint | Intersection margin |
|---|---:|---:|---:|
| content effect | 1.1250 | 0.6250 | -0.5000 |
| bare-label effect | 0.2188 | 0.0469 | -0.1719 |
| specificity | 0.8594 | 0.4063 | -0.4531 |
| post-washout effect | 0.1719 | 0.0625 | -0.1094 |

This is exactly the distinction v0.68 was designed to expose: a robust
directional local response can coexist with rejection of one global
magnitude/state object.

The ranges above are not confidence intervals. They are the min/max of two
display-order contrasts in burned data. They cannot establish the successor
hypothesis.

## Consequence for the next physical bridge

A successor should:

1. use byte-identical singleton repeats to calibrate computation separately
   from semantics;
2. form contrasts within display order;
3. admit endpoints by the exact blockwise zero-sum criterion;
4. retain order interactions as possible scientific heterogeneity;
5. report a context-indexed response family by default; and
6. permit a global response claim only through a separate held-out
   compatibility gate.

The draft protocol implements this architecture but deliberately does not yet
freeze sample sizes or statistical margins.

## ASMP-9 claim boundary

This development identifies a maximal invariant for one declared measurement
nuisance action. It does not prove that the nuisance action is complete, that
next-token choice is a value, that model responses reveal a reward-shaping
orbit, or that context-local effects correspond to coherent preferences. It
does not resolve ASMP-9 and authorizes no model run.
