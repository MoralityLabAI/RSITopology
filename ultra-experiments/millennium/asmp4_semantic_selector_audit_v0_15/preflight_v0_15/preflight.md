# Eval Preflight — asmp4-semantic-selector-audit-v0-15

**Claim:** A clause-complete conservative audit finds no canonical ASMP-4 clause that selects between the computed q-fiber sensor and the forced raw-mode-injective sensor; any ambiguous clause blocks the claim.
**Policy:** `base`
**Status:** **FAIL**
**Release blocking:** yes

## Findings

### HIGH — `dataset_not_held_out` · **BLOCKING**

The dataset is not explicitly declared held out.

**Required repair:** Use a held-out evaluation split or label the result exploratory and non-generalizing.

### HIGH — `identity_blinding_missing` · **BLOCKING**

The protocol does not explicitly blind candidate identity.

**Required repair:** Set pairwise.blind_identity: true and strip model-identifying metadata.

### HIGH — `order_randomization_missing` · **BLOCKING**

The protocol does not explicitly randomize display order.

**Required repair:** Set pairwise.randomize_order: true with a reproducible seed.

### HIGH — `position_swap_missing` · **BLOCKING**

The protocol does not explicitly run both A/B and B/A orderings.

**Required repair:** Set pairwise.swap_positions: true and retain the displayed order in raw logs.

### MEDIUM — `dataset_below_policy_minimum`

Dataset size 23 is below the policy minimum of 30 independent items.

**Required repair:** Increase independent dataset items or narrow the claim. Judge repetitions do not increase task sample size.

### LOW — `adapter_subjective_dimension_gap`

The 'generic' adapter recommends subjective dimensions that are not declared.

**Required repair:** Add the applicable dimensions or record a scoped omission in the manifest.
