# ASMP-9 conservative-numeraire verification v0.30

**Verdict:** `conservative_numeraire_boundary_established_v0_30`

## Gates

- `G0_registration_binding`: PASS
- `G1_structural_product_extension`: PASS
- `G2_mechanical_negative_controls`: PASS
- `G3_semantic_calibration`: PASS
- `G4_semantic_negative_controls`: PASS
- `G5_constraint_rank_and_omission`: PASS
- `G6_mechanics_only_and_scale_no_go`: PASS
- `G7_approximate_calibration`: PASS
- `G8_v028_eligibility`: PASS
- `G9_prior_art_and_claim_boundary`: PASS
- `G10_resource_and_scope`: PASS

The import-independent verifier passed all 23 checks.

## Headline checks

The exact product extension preserved four stationary-policy occupancies over
four consequence levels, for 16 exact checks. All levels shared mechanics
hash:

```text
f9248a1e529d4067f9b65155be6b4ff1c2b70e697c4447393228a3d24b1b3740
```

Four negative controls were rejected:

```text
horizon control              horizon
policy-feasibility control   action_sets, features, transitions
transition control           transitions
feature control              features
```

The semantic controls returned:

```text
calibrated table             calibrated_additive
unknown coefficient          separable_unknown_scale, 9/7
interaction table            context_interaction, residual 5/19
incomplete table             incomplete_semantic_table
```

The calibrated five-by-four table passed 15 anchored constraints. The
separate five-by-six constraint matrix had exact rank 25, and all 25
single-constraint omission witnesses passed.

Three distinct semantic classes shared one mechanics hash. The unknown-scale
population law matched under both registered positive rescalings.

The approximate cell attained the registered sharp bound:

```text
maximum cell residual         3/17
maximum two-sided bias        6/17
two-sided bound               6/17
```

The combined v0.28 eligibility rule accepted only the mechanically identical,
semantically calibrated cell. It rejected four mechanical controls, the
unknown-scale cell, and the incomplete cell with explicit reasons.

Runtime was 0.121 seconds, peak resident memory was 20,537,344 bytes, and no
GPU was used.

## Integrity

```text
implementation commit
  b510b38a28fc30c6bd7b48f2c254122220f3b1ed

registration commit
  6669fcdc95d828bdf12f27d48dce77c7c8840023

registration SHA-256
  a925e338a0a4545daa83489afba259698c991b44293cb1459b409fd077c58d14

result SHA-256
  96491a7a087a9c56726392e28bffafba10f9184040ffaa505604205e3e02893a

run-receipt SHA-256
  b7b7af3fc3076d643a58f49d23c836d11a80acc1aa190c1e0fc2d9cce00c4871

independent-verification SHA-256
  a683723f7fe4a5b23dd66d299a61d6ad6215740c42b98f7a1203b722b08d67d8
```

## Claim boundary

This result validates a finite conservative-access ledger. It does not show
that a real consequence has stable cardinal utility, derive a scalar table
from ordinal choices, validate a demonstrator model, characterize every
semantics-preserving MDP equivalence, or resolve ASMP-9.
