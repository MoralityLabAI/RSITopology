# ASMP-9 heterogeneous-midpoint verification v0.27

**Verdict:** `heterogeneous_midpoint_boundary_established_v0_27`

## Gates

- `G0_registration_binding`: PASS
- `G1_shared_midpoint_link_shape`: PASS
- `G2_arbitrary_midpoint_obstruction`: PASS
- `G3_context_factorization_and_gauge`: PASS
- `G4_cycle_liveness`: PASS
- `G5_forest_chord_ledger`: PASS
- `G6_robust_spectral_bound`: PASS
- `G7_prior_art_and_claim_boundary`: PASS
- `G8_resource_and_scope`: PASS

The import-independent verifier passed all 16 checks.

## Headline checks

```text
fresh localized thresholds                         5,207
cell-specific link-sign checks                       585
link-sign mismatches                                   0
maximum localization error                       19/4096
maximum bisection queries                              12

arbitrary-midpoint witness edges                        6
maximum utility displacement                           10
effective-threshold mismatches                          0

fresh graph cells                                       4
live cyclic refutations                                 3
tree cells correctly marked unavailable                 1
```

Both registered noisy reconstruction cells respected the exact pseudoinverse
operator-norm bound:

```text
fresh_hexagon_with_leaf:
  quotient error  0.0676229
  bound           0.1249869

fresh_complete_2_by_3:
  quotient error  0.0509627
  bound           0.0679338
```

Runtime was 0.329 seconds, peak resident memory was 31,313,920 bytes, and no
GPU was used.

## Claim boundary

This result validates the implementation of a classical finite incidence
theorem under a prospectively registered ASMP-9 access grammar. It does not
establish that human or model demonstrators have shared or context-only
midpoints, that practical interventions supply cardinal offsets, that a tree
validates the factor model, or that ASMP-9 is resolved.

