# ASMP-9 behavioral rectangle verification v0.32

**Verdict:** `behavioral_rectangle_boundary_established_v0_32`

## Gates

- `G0_registration_binding`: PASS
- `G1_population_acquisition`: PASS
- `G2_rectangle_algebra`: PASS
- `G3_complete_coverage`: PASS
- `G4_shared_uncertainty_geometry`: PASS
- `G5_three_state_semantics`: PASS
- `G6_mixture_affinity_liveness`: PASS
- `G7_access_no_go`: PASS
- `G8_finite_sample`: PASS
- `G9_v031_handoff`: PASS
- `G10_prior_art_and_claim_boundary`: PASS
- `G11_resource_and_scope`: PASS

The import-independent verifier passed all 20 checks.

## Headline exact checks

The 3x4 primary rectangle used twelve centered dyadic values at depth four.
Each cell was recovered in four binary standard-gamble queries:

```text
population query count         48
binary transcript lower bound  48
operator shape                 6 x 12
operator rank                  6
additive residuals             all zero
planted interaction residual   1/16
```

Each of the twelve missing-cell controls preserved every observed cell and
created a nonzero cross-difference.

The continuous-width control returned:

```text
cell radius                    1/16
each coordinate support        1/4
registered structured support  1/4
independent-residual surrogate  1/2
```

The three-state rectangle evaluator returned certified, rejected, and
inconclusive on its respective fixtures.

The mixture-affinity controls returned:

```text
consistent                     residual 0, certified
distorted                      residual 1/16, rejected
uncertain                      residual 1/12,
                               support 1/24,
                               tolerance 1/16,
                               inconclusive
```

The ordinal-only witness preserved the complete ranking while changing the
cross-difference from zero to `4/9`. The row-local-ruler witness preserved
both normalized row coordinates while changing global additivity.

For 48 queries, correct-sign floor `3/4`, and family error `1/100`, exact
binomial arithmetic found 43 as the smallest passing odd repeat count. The
41-repeat predecessor failed, and chance-level responses correctly returned
unavailable.

The handoff exposes the 6x12 semantic incidence matrix, twelve cell widths,
and six shared columns needed for downstream set-valued propagation.

Runtime was 0.0555525 seconds, peak resident memory was 21,557,248 bytes, and
no GPU was used.

## Integrity

```text
implementation commit
  899cee20ce171f996f9c2adf4774a5beeb58fc01

registration commit / run commit
  f2fb9565996ae604aa1b3ba90fd7d4073aa1d835

registration SHA-256
  95eb63461eec234601b6bc0caa0d20238d1e534ff4acbd5633baa8ea9940c5f9

protocol SHA-256
  d7ec8ecb3f5c3ea4ced0b0b193ea35f55f9018c76ca7e6f9b911bfb9944a73e0

result SHA-256
  5729d7909fbf31b2de7b7260f6a30677a5d1f0d367613e37eb6938085b05819f

run-receipt SHA-256
  7862f69eafbe7f04371842b15c3ee5ad1014f4e00bef68d5ead14bbe60023501

independent-verification SHA-256
  4892d81ba700738c5eb4d78a8fead9e538b579e3d9232a07131e595cae3cf972
```

## Claim boundary

The run validates a finite standard-gamble access ledger under registered
mixture-affine, common-anchor, common-midpoint, independent-response, and
margin assumptions. It does not validate those assumptions for humans or
models, prove a general statistical or conjoint-measurement theorem,
establish a practical semantic numeraire, or resolve ASMP-9.
