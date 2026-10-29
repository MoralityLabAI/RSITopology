# Holonomy causal path-transfer falsification v0.1

## Outcome

Registered decision: **`pass`**. All gates pass:
`true`.

The canonical CPU fixture transports one rank-four signed coordinate to the
same target by two paths. One direct-sum block is either flat or curved while a
second block remains flat, providing exposed and low-exposure directions in one
bundle. The downstream map is `tanh(Jz)`, so its registered Lipschitz bound is
known exactly within the edit space.

## Primary results

- Rows: `3456` across `12` loops.
- Maximum two-path/loop identity error:
  `9.992e-16`.
- Maximum causal-bound excess: `0.000e+00`.
- Maximum flat displacement: `0.000e+00`.
- Maximum curved exposed displacement:
  `0.982108`.
- Maximum curved exposed response disagreement:
  `1.183766`.
- Bound-authorized coverage: `91.291%` with
  `0` false authorizations.
- Grouped held-out relative SSE reduction from the frozen holonomy features:
  `0.890005`, grouped-bootstrap 90% interval
  `[0.849073,
  0.923200]`.
- Seeded permuted-holonomy relative SSE reduction:
  `0.052462` (descriptive leakage null).

## Gates

- `G0_matched_local_lineage`: **pass**
- `G1_path_identity`: **pass**
- `G2_bound_coverage`: **pass**
- `G3_flat_negative_control`: **pass**
- `G4_curved_positive_control`: **pass**
- `G5_incremental_prediction`: **pass**
- `G6_bound_authorization`: **pass**
- `G7_energy_invariance`: **pass**
- `G8_gauge_invariance`: **pass**
- `G9_orientation_reversal`: **pass**

## Interpretation

This establishes that the proposed measurement and analysis recover a planted
causal path-dependence signal that local lineage and Jacobian visibility do not
fully encode. It also calibrates a conservative signed-control bound. It does
not show that a transformer contains the measured bundle. The real-model entry
condition remains a target-blind, lineage-connected, noise-valid loop universe
with a third untouched causal split.

Manifest SHA-256: `4ff3b221aa3ab8de28c18f8d3582f46c7e422c60225381f6b08c7f8a34e14652`.

## Claim boundary

CPU-synthetic causal path-transfer calibration only; no transformer, capability, self-improvement, or RSI claim.
