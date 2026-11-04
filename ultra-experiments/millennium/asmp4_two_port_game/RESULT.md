# ASMP-4 Exact Two-Port Game Result

## Decision

**PASS — open ASMP-5.**

The registered finite game produced an `exact_registered_architecture_phase_map`. This is an exact result for the frozen rational architecture, not evidence for an asymptotic data-rate theorem.

## Frozen execution

- Preregistered commit: `04c44f536d47e89180234e73a71467861cddd74e`
- Grid: 108/108 registered cells
- Feasible cells: 77/108
- Exact arithmetic: Python `Fraction`
- Runner wall time: 5.8828 seconds
- Peak traced Python allocation: 496,648 bytes
- Runner gates: G0--G7 passed
- Independent checks: 20/20 passed

## Load-bearing cells

At horizon 2, coupling `c=1/2`, and tangent rate `a_z=3/2`:

| read bits/step | write bits/step | feasible |
|---:|---:|:---:|
| 2 | 2 | yes |
| 0 | 2 | no |
| 2 | 0 | no |
| 0 | 0 | no |

Thus, within this registered architecture, a sufficient sum of nominal port capacity does not compensate for eliminating either finite interface. The continuous full-state/full-action control passes the same underbudget plant, separating information restriction from absent control authority.

The zero-coupling control is invariant to tangent growth across every registered horizon and port cell. The stable-plant, zero-rate control also passes. Every reported feasible policy replays over all nine initial states and every disturbance history, and feasibility is invariant under reversal of the sensor-symbol labels.

## Quantifier repair

The solver searches for one time-indexed memoryless decoder `(time, read_symbol) -> action` shared by all initial states and all disturbance histories. It does not select a different controller per initial cell. A sealed two-state trap confirms that per-cell feasibility can coexist with failure of a universal controller.

## Integrity

- `result_v0_1.json`: `97cb809845241d828596a075fbf8169e98af787ac5154ad80df4f1ab3d54382b`
- `receipt_v0_1.json`: `a0f69d30fda86a255ea2011da41263b1d5c0bd12a2777e30fa62fb39a500e8bf`
- `verification_v0_1.json`: `ed26f702cc84b1c5379d0dbecaf23e2d61489fb638180e6f66b284d410eeb64f`

## Claim boundary

This run establishes only the exact phase map and registered separations for the finite plant, state collar, horizons, sensor thresholds, action dictionaries, and disturbance alphabet in protocol v0.1. It does not prove an asymptotic split-channel lower bound, optimality outside the registered controller class, or applicability to learned systems.
