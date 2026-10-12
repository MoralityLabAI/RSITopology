# ASMP-9 decision-relevance verification v0.29

**Verdict:** `decision_relevance_boundary_established_v0_29`

## Gates

- `G0_registration_binding`: PASS
- `G1_decision_gauge_precondition`: PASS
- `G2_quotient_regret_bound`: PASS
- `G3_sharpness_witness`: PASS
- `G4_policy_identity_margin`: PASS
- `G5_invalid_gauge_abstention`: PASS
- `G6_scale_target_bifurcation`: PASS
- `G7_measurement_to_decision_composition`: PASS
- `G8_prior_art_and_claim_boundary`: PASS
- `G9_resource_and_scope`: PASS

The import-independent verifier passed all 19 checks.

## Headline checks

The declared constant gauge was decision-null on every positive cell. A
varying-horizon control violated that precondition and returned
`decision_gauge_invalid`, with no numeric certificate.

The nonzero-regret cell returned:

```text
observed regret                  8
quotient error squared           25/8
selected occupancy distance^2    32
selected bound squared          100
```

A zero-regret control passed both registered bounds. The sharp two-policy
witness attained exact equality:

```text
regret                          22/13
regret squared                 484/169
selected bound squared         484/169
global bound squared           484/169
```

The strict-margin cell certified policy identity. The equality control
returned inconclusive as registered.

Both positive reward scales selected policy `1`, while the evaluated policy's
regret crossed the fixed-unit threshold:

```text
scale 1/5    regret 6/5    threshold pass
scale 7/3    regret 14     threshold fail
```

The v0.28 measurement-to-decision composition cell had quotient error squared
`25/8`, nonzero observed regret `8`, and predicted regret-bound squared `100`.

Runtime was 0.048 seconds, peak resident memory was 20,234,240 bytes, and no
GPU was used.

## Integrity

```text
implementation commit
  c54dde192b432b32feb41625a2db16f073e392b7

registration commit
  283c3420d940dcd1f8cf39df75a664d51555ce2c

registration SHA-256
  a2fe94f2be38ce9e4681de7a8466511172b5845dd408560db798b1901dc244f7

result SHA-256
  0d9b00cacfc4f6451df7dc5719636bff8b3533711e36b1de4b51a49ee7b5dd0e

run-receipt SHA-256
  485c3c73020f0bf8287b85cacf2c6162b32764141ab325343902f605bb80f878

independent-verification SHA-256
  7b91d202ba97f027bd1e3e220c9be420240ce306e7621c509aef1e6b35d10dae
```

## Claim boundary

This result validates an exact finite decision ledger. It does not establish
that a learned reward estimate is correct; that the policy family contains a
safe policy; that small reward regret implies broad safety; that real
interventions satisfy the v0.28 access assumptions; or that ASMP-9 is
resolved.
