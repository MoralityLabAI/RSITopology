# ASMP-9 contextual scalar-gluing verification v0.11.2

**Verdict:** `finite_contextual_scalar_gluing_geometry_verified_v0_11_2`

## Gates

- **G0_registration_binding:** PASS
- **G1_exact_census:** PASS
- **G2_census_liveness:** PASS
- **G3_seeded_coverage:** PASS
- **G4_quotient_and_sharpness:** PASS
- **G5_shared_controls:** PASS
- **G6_nongluing_controls:** PASS
- **G7_local_failure_and_status_liveness:** PASS
- **G8_minimality:** PASS
- **G9_resource_envelope:** PASS

## Exact three-context census

- graph tuples: 262144
- mixed-rank distribution: {"0": 736, "1": 4290, "2": 15015, "3": 37518, "4": 67405, "5": 82308, "6": 54872}
- live tuples: 261408
- forced-by-design tuples: 736

## Seeded decision cells

- cells: 4096
- status counts: {"local_scalar_failed": 4081, "shared_scalar_forced_by_design": 1, "shared_scalar_refuted": 4095, "shared_scalar_verified": 4095}
- implementation: exact GF(2) incidence rank with signed rational circulations

## Repair history

The registered v0.11 and v0.11.1 attempts exceeded the unchanged
wall-time cap and produced no scientific artifacts. Version
v0.11.2 preserves both failures and changes only exact
implementation bookkeeping.

## Claim boundary

Exact finite real-valued context-labelled graph theorem; not
ordinal rationalizability, finite-sample preference estimation,
human/model evidence, infinite-history analysis, or ASMP-9
resolution.
