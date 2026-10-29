# ASMP-9 calibrated occupancy verification v0.28

**Verdict:** `calibrated_occupancy_boundary_established_v0_28`

## Gates

- `G0_registration_binding`: PASS
- `G1_homogeneous_scale_obstruction`: PASS
- `G2_adaptive_scale_obstruction`: PASS
- `G3_unknown_numeraire_control`: PASS
- `G4_calibrated_numeraire`: PASS
- `G5_finite_mdp_realization`: PASS
- `G6_quotient_criterion`: PASS
- `G7_robust_conditioning`: PASS
- `G8_prior_art_and_claim_boundary`: PASS
- `G9_resource_and_scope`: PASS

The import-independent verifier passed all 18 checks.

## Headline checks

Two fresh homogeneous cells preserved their complete population laws under
all four registered positive reward rescalings. The same equality held over
768 exact adaptive transcript probabilities.

The unknown-value side-feature control remained scale-coupled under both
registered rescalings. The known-numeraire control broke the coupling under
both registered rescalings and localized every occupancy functional within
the registered tolerance:

```text
maximum localization error     1819/1720320
registered tolerance           5/2048
maximum bisection queries       14
```

Four fresh integer measurement matrices were realized by explicit
reward-independent deterministic finite MDPs:

```text
query initial states            19
deterministic transitions      144
states                         163
fixed horizons by matrix       4, 4, 3, 4
```

The quotient controls returned:

```text
connected constant gauge       identifiable, rank 4
disconnected constant gauge    not identifiable, rank 3
affine gauge                    identifiable, rank 3
```

The disconnected cell's registered non-gauge kernel witness was verified
exactly. Both robust cells retained full quotient rank, while the
ill-conditioned cell amplified Euclidean error by `2896.309` times the
well-conditioned control.

Runtime was 0.098 seconds, peak resident memory was 31,997,952 bytes, and no
GPU was used.

## Integrity

```text
implementation commit
  fcab52dd08ff88f382d3a33d585bd439bfa3c99d

registration commit
  9fdeaca64da1e59c13ca24e00f54bf2fe0022eeb

registration SHA-256
  a8cd1d8633c2e4017889dbd06ddb90db1c9d1799432deb09a8e593da38d466af

result SHA-256
  0f7b5bb876f8b7b6d58f7b891ed6e54b69f0c7168db5eb379ea8c21d675fad14

run-receipt SHA-256
  97b152cf7ab380823ecd33b89969dbb49e67bc30be6a1e1018ec92051f8996f6

independent-verification SHA-256
  f8336fb7b93724e34cc183b9d42c2fe7c97ed699d8d0b88b3195ef1343e6d2e3
```

## Claim boundary

This result validates an exact finite access ledger and its implementation. It
does not establish that money, tokens, or another practical consequence is a
stable cardinal numeraire; that a natural environment supplies the required
occupancy design; that real behavioral responses satisfy the link model; or
that ASMP-9 is resolved.
