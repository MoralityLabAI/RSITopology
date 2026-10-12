# ASMP-9 joint approximate verification v0.31

**Verdict:** `joint_approximate_boundary_established_v0_31`

## Execution chronology

The original registered v0.31 runner completed its in-memory mathematical
calculation but failed in the Windows resident-memory query before writing
any output. The empty attempt is preserved in `FAILURE_v0_31.md` and
`failure_receipt_v0_31.json`; it is not scientific evidence.

Version v0.31.1 was separately registered as a resource-only repair. It
imports the sealed v0.31 runner, substitutes only the already validated
Windows memory helper, and calls the original entry point. The original
scientific source, fixtures, protocol, thresholds, gates, and verifier remain
hash-bound.

## Gates

- `G0_registration_binding`: PASS
- `G1_context_projection`: PASS
- `G2_joint_source_coverage`: PASS
- `G3_mechanical_contraction`: PASS
- `G4_semantic_incidence`: PASS
- `G5_support_sharpness`: PASS
- `G6_policy_handoff`: PASS
- `G7_source_ablation`: PASS
- `G8_shape_advantage`: PASS
- `G9_context_rank_no_go`: PASS
- `G10_prior_art_and_claim_boundary`: PASS
- `G11_resource_and_scope`: PASS

The original import-independent verifier passed all 29 checks. The repair
verifier passed all 10 repair-integrity checks.

## Headline exact checks

The context projector produced:

```text
projected design rank           3
LA                              identity
LC                              zero
context-confounded control      unavailable, projected rank 0
```

The primary joint certificate returned:

```text
mechanical gain lambda          1/50
additive radius a               37/1500
reward radius R_theta           18197/11760
theta_hat                       (5967/4000, -1193/2400, 5949/8000)
```

All seven registered audit directions covered the planted realization. In
direction `(2,-3,1)`, the support

```text
90263/588000
```

was attained exactly by the stored row-source and semantic-source vertex.

The primary policy calculation selected policy `4`, certified every strict
competitor margin, and returned robust regret zero over the outer set. The
separate risk fixture attained both actual and certified regret `9/10`.
Equality at the support boundary remained inconclusive.

The liveness controls returned:

```text
mechanical gain-one cell
  Delta = -1 erased theta = 0 and theta = 37 to the same observation

shared semantic-cell control
  structured support            0
  independent-row surrogate     1/5

anisotropic policy control
  exact zonotope support         1/100
  policy margin                  1/5
  scalar-box radius              9/10
  zonotope decision              certified
  scalar-box decision            not certified
```

Each of the four source classes—mechanical, localization, non-context
midpoint, and semantic—was exercised by a planted `1/10` cell. The full
certificate covered every cell; deleting the sole active source exposed the
error in every case.

Runtime was 0.0156254 seconds, peak resident memory was 19,697,664 bytes, and
no GPU was used.

## Integrity

```text
original implementation commit
  896904058fd80a0343f2c0ef4ee736f0edd2738c

original registration commit
  7af9a09a9db9677aea542aea5e1e4d6f015a5611

original registration SHA-256
  4a3d57e5c71335d157fe3e1bd65a4f0b184515dc3be06a143bcca3f019b81379

repair implementation commit
  c50659e9c21b9c34783d2f89ec7757a4aef94f97

repair registration commit / run commit
  50593abf361afcf867f753b2039261a01434725c

repair registration SHA-256
  d9c044c9b477478a54b55c79d2111d1efca4b7ee2932190dbe718259ef54310c

result SHA-256
  f07ee0b7ef11339f97b2862987495a9d4088e44f55b58c7d708ba9ee0d578e94

run-receipt SHA-256
  f73b10d3e9e06196c230400b77feab8f13f6b4e4640c0d8a6f4cf5fe51d83918

independent-verification SHA-256
  618373a9a5430aa74fc88512be1c5733cc3b9ed4f6d275bf78c3f856aecbde84

repair-verification SHA-256
  3612669c29965fd8ade4288d48c1aa5acc220408d6bd204fbca27a1287a8e235
```

## Claim boundary

The run validates one deterministic finite composition certificate with
registered source bounds. It does not derive those bounds from behavior,
establish stochastic sample complexity, solve a robust MDP, characterize
maximal reward equivalence, show that a real semantic numeraire exists, or
resolve ASMP-9.
