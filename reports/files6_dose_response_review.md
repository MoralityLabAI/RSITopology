# Review of Fable `files(6).zip`

Source archive SHA-256:
`1A02EE20345D41AC81D833020253F74475DDF9513ABB0035909E2D1624F4EFAD`.

## Result retained

The one-seed unit sweep validates the intended shape of the within-band
identity-rotation control. Mean chordal lineage is strictly decreasing;
minimum occupancy varies by less than `9e-16`; and policy uplift is almost
linear in lineage through `50 degrees` (`R^2 = 0.9941`). Policy passes through
`25 degrees` and first fails at `30`; the edit gate passes through `45` and
first fails at `50`. These flip locations are fixture observations, not
candidate thresholds.

At `5 degrees`, lineage loss is about `0.00757`, several times larger than the
maximum observed chordal-versus-cos-squared residual. Thus this construction
has an early-warning region before either downstream gate fails.

## Audit corrections

The archive describes a 5-degree grid but contains 16 rather than 19 rows;
`65`, `75`, and `85 degrees` are absent. Chordal lineage tracks the analytic
`cos^2(theta)` curve closely, but the maximum absolute residual is `0.00195`,
not four-decimal agreement at every point. This residual is expected because
the reference consensus is only approximately the planted subspace under
nonzero context geometry.

The `+0.05` standardized uplift at `80` and `90 degrees` is evidence of a
possible unit-fixture noise floor, not a calibrated estimate: there are only
two reported tail cells and `85 degrees` is missing.

## Integrated standing calibration

`lineage_angle_calibration_v0_1.json` freezes a complete `0:5:90` grid and
three seeds. The runner checkpoints every seed-angle cell, records band labels
and margins under v0.2.2, verifies occupancy/candidate/outcome invariants, and
reports cos-squared residuals and downstream gate behavior descriptively. It
refuses to execute unless the strict wrapper sets
`RSI_TOPOLOGY_HARD_CAPS_ENFORCED=1`.

The calibration has been prepared and syntax/unit checked but not run: CPU and
I/O cgroup delegation remains unauthorized. The imported sweep remains
external diagnostic evidence.

## Governance synthesis

The fixture pair now separates two monitoring failures. Band failover is an
abrupt re-anchoring that a categorical identity label catches. Common
within-band rotation is continuous, leaves occupancy perfectly green, and is
visible through principal angles well before utility gates fail. A governance
regime therefore needs both immutable anchor labels and continuous lineage
checks; either one alone has a constructed blind spot.
