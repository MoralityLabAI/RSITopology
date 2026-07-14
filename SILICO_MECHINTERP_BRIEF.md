# Silico execution brief: patchwise behavioral identity in Qwen3-1.7B

## Role

Act as a target-blind mechanistic-interpretability executor. Determine whether the failed global edit-atlas hypothesis has a narrower, measurable successor: behavior-family-local high-dimensional structures whose identity persists across prompts and model sites well enough to define causally useful edit coordinates.

Do not search for recursive self-improvement directly. Do not optimize model capability. The immediate job is to measure and certify candidate structures, produce matched causal-edit candidates, and stop honestly if the registered identity object does not exist.

This brief is interface-neutral. Map the requested measurements to Silico's native feature, circuit, intervention, and export operations. Do not invent unavailable measurements. If a required operation is unsupported, emit `blocked_capability.json` with the missing operation, affected gate, and nearest supported substitute; do not silently substitute it.

## Scientific question

The parent experiment rejected one global soft atlas across the registered Qwen sites and prompt groups. It did **not** reject high-dimensional behavioral structure in general.

Test this fresh hypothesis:

> Although no single global soft atlas is stable across the registered Qwen primitives, behavior-family-local identity patches may support stable, causally useful edit coordinates. Within certified local patches, target-blind selected edits should outperform matched-random directions; across patch boundaries, signed transport should fail or require separate coordinates.

The strongest permissible conclusion is about local, behavior-conditioned edit identity in this model. A positive result does not establish recursive improvement, compactification, RSI, safety, or capability preservation.

## Frozen target

- Model: `Qwen/Qwen3-1.7B`
- Revision: `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`
- Local model, if the workspace is mounted: `D:\Research_Engine\Qwen_Storyworld\cache\models\Qwen3-1.7B-70d244cc-verified`
- Primary site universe:
  - `model.layers.16.self_attn.v_proj`
  - `model.layers.17.self_attn.v_proj`
  - `model.layers.18.self_attn.v_proj`
  - `model.layers.19.self_attn.v_proj`
  - `model.layers.20.self_attn.v_proj`
  - `model.layers.21.self_attn.v_proj`
  - `model.layers.22.self_attn.v_proj`
  - `model.layers.23.self_attn.v_proj`
  - `model.layers.24.self_attn.v_proj`
  - `model.layers.25.self_attn.v_proj`
  - `model.layers.26.self_attn.v_proj`
  - `model.layers.27.self_attn.v_proj`
- Maximum candidate rank: 8 for compatibility with the existing lineage work. Report the full measured spectrum even when only ranks 1-8 are used for candidates.
- Behavior families:
  - `affine_recurrence`
  - `symbol_transport`
  - `grid_rotation`
  - `graph_reachability`
- Frozen data splits: `construction`, `selector`, `audit`, `outer`.

Use only `construction` prompts to construct features, bands, transports, patches, thresholds, and candidate-selection rules. Do not inspect answer keys or behavioral outcomes during construction.

## Required repository inputs

When the repository is mounted, hash and record these files before work begins:

- `protocols/proposal_recursive_patchwise_reentry_v2_1.json`
- `protocols/proposal_recursive_patchwise_holdout_v2_1.json`
- `protocols/identity_attestation_v1.json`
- `protocols/vpd_identity_stratification_v0_2.json`
- `schemas/identity_anchor_record_v1.schema.json`
- `schemas/lineage_certificate_v1.schema.json`
- `schemas/vpd_identity_candidate_v0_2.schema.json`

The public holdout manifest contains no answer key. The private answer key and the frozen scorer are not inputs to the construction phase.

## Non-negotiable controls

1. Preserve target blindness. Features, subspaces, patches, edit directions, matched controls, candidate IDs, and file hashes must be sealed before any audit or outer outcome is read.
2. Keep physical site, behavior family, prompt, split, rank, norm, and run replicate explicit. Never pool them silently.
3. Report gauge-invariant quantities for identity claims. A convenient basis is not an identity certificate.
4. No threshold tuning on revealed outcomes.
5. No signed activation or weight intervention may be called authorized below `holonomy_clean` certification.
6. Bundle-energy or subspace-energy rewards require at least `lineage_certified` status.
7. Lower-certification results may be retained only as `engineering_evidence`.
8. No new invariant level may be introduced. The allowed levels are `engineering_evidence`, `lineage_certified`, and `holonomy_clean`; holonomy is the top of the stack.
9. If the available model states do not support closed loops, do not manufacture loop closure from unrelated samples. Record `holonomy_unavailable`, cap certification at `lineage_certified`, and do not authorize signed edits.

## Phase 0: provenance and feasibility

Before measuring the model:

1. Record the exact model revision and hashes of all weight shards, tokenizer files, prompt manifest, Silico version/build, export configuration, numeric precision, device, and random seeds.
2. Confirm that every requested site resolves to one tensor with stable dimensions.
3. State the precise activation object used at each `v_proj` site: input, pre-projection output, post-projection output, token aggregation rule, and normalization.
4. State whether Silico can export:
   - prompt-indexed activations;
   - local Jacobian-vector or vector-Jacobian products;
   - orthonormal feature/subspace bases;
   - activation interventions;
   - low-rank weight-edit candidates;
   - deterministic raw arrays.
5. Identify the two axes available for lineage and loop construction. Prefer behavior context x genuine checkpoint/model state. If only one model state exists, use context-to-context lineage but mark holonomy unavailable unless Silico exposes another registered, semantically valid axis.

Stop before Phase 1 if the model revision, prompt split, or physical site universe cannot be pinned exactly.

## Phase 1: target-blind structure census

For every construction prompt and registered physical site:

1. Capture the registered activation object for the behavior-relevant token positions. Keep token-level arrays; aggregation is an additional view, not a replacement.
2. Measure local response geometry using both:
   - activation covariance/Gram structure; and
   - Jacobian-visible response directions where Silico supports them.
3. For each behavior family and site, estimate candidate subspaces for ranks 1-8 using deterministic SVD/eigendecomposition. Export the full spectrum and the orthonormal bases.
4. Estimate each subspace twice from disjoint construction-prompt halves. This is the minimum cross-fit needed to separate a repeatable family structure from a fitted basis.
5. Compute, without outcomes:
   - selected band and consensus rank;
   - mean chordal lineage: `trace(P_ref P_cur) / min(rank_ref, rank_cur)`;
   - reference recall: `trace(P_ref P_cur) / rank_ref`;
   - current precision: `trace(P_ref P_cur) / rank_cur`;
   - worst-direction retention: the minimum squared singular value of `U_ref^T U_cur`, with zero padding under rank loss;
   - log-volume retention: mean `log(sigma_i^2 + 1e-8)` over reference directions;
   - maximum principal angle, assigning 90 degrees to missing reference dimensions;
   - Jacobian visibility;
   - baseline activation RMS;
   - effective rank/participation ratio and eigengap as descriptive quantities.
6. Construct a family-label permutation null while preserving site, rank, prompt count, activation spectrum, and random-number stream.

### Gate P1a: local lineage signal

Within behavior families, cross-fit lineage retention must beat the family-label permutation null with a simultaneous one-sided 95% lower confidence bound strictly above `0.10`.

If this fails, report `P1_local_identity = fail` and stop before interventions.

## Phase 2: transports, loop closure, and patch certification

For every pair of adjacent registered nodes with equal rank, compute the orthogonal Procrustes transport from their cross-fitted bases. For each edge, record both mean chordal lineage and worst-direction retention.

For each registered elementary closed loop `gamma = (v0, ..., vn = v0)`, compose transports back to the hashed root fiber:

```text
M_gamma = T[v0 <- v(n-1)] ... T[v2 <- v1] T[v1 <- v0]
H_gamma = polar(M_gamma)
```

Report:

- `det(H_gamma)`;
- `det_h_flag = true` whenever `det(H_gamma) < 0`;
- sorted canonical rotation angles when `det(H_gamma) > 0`;
- maximum canonical angle;
- identity loss;
- loop orientation, root, edge order, basis hashes, and transport hashes.

Suppress canonical-angle interpretation when `det(H_gamma) < 0`; orientation reversal is a categorical failure.

Use a frozen rooted spanning tree for canonical transport. Off-tree edges are loop-closure audits. Do not choose a favorable path after examining loop results.

### Gate P1b: holonomy-clean local patches

An admitted local patch must satisfy all of the following:

- every edge has mean chordal lineage at least `0.95`;
- every edge has worst-direction retention at least `0.90`;
- every admitted elementary loop has `det(H) > 0`;
- every admitted elementary loop has maximum canonical angle at most `15 degrees`;
- all nodes use the same selected band and rank;
- all required measurements are present and finite.

Construct maximal connected patches under those rules. P1 passes only if at least three physical sites have an admissible patch in at least two behavior families.

If loops are unavailable, export lineage patches but cap them at `lineage_certified`; P1 holonomy authorization remains unavailable.

## Phase 3: candidate edit family and matched controls

Run this phase only after P1 passes. Candidate generation must remain target-blind.

For each admitted patch:

1. Define one canonical coordinate frame at the frozen root.
2. Generate rank-1 through rank-8 candidate directions from the cross-fitted family subspace.
3. Parallel-transport signed coordinates only along the frozen spanning-tree path.
4. Generate exact-rank, exact-norm matched-random directions at the same physical site.
5. Generate a separate cross-site contrast: attribution-selected site versus matched-random site while holding the direction policy fixed.
6. Never mix these two estimands:
   - `direction_value`: selected direction minus random direction at the same site;
   - `site_selection`: selected site minus matched-random site under the same direction policy.
7. Match or report caliper failure for Jacobian visibility and baseline activation RMS. The registered relative-distance ceiling is `0.20` for each.

Use construction prompts to define candidates and selector prompts only for the frozen selection step. Audit and outer prompts remain sealed.

Silico may execute construction/selector diagnostic interventions if its environment supports reversible activation patching. Direct weight writes must remain disabled unless the existing repository `certify(site)` result is `holonomy_clean` for `disparate_weight_edit`.

### Gate P2: causal edit value

The downstream repository scorer, not Silico's feature-selection interface, decides P2. The registered requirement is:

- within identity strata, selected edits beat within-site matched-random directions by more than `0.10` outer-utility standard deviations on selector-to-audit grouped holdout;
- rank and norm are matched exactly;
- the cross-site contrast is co-primary and separately reported;
- run replicate is the unit of independence.

Silico's job is to emit sealed candidates and measurements, not to alter this gate.

## Three adversarial matched controls

Package these as explicit tamper/control cases:

1. **Spectrum-preserving conjugation**: preserve the spectrum, selected band, rank, and occupancy while rotating the subspace away from its reference. The lineage measurement should detect the loss.
2. **Band failover**: preserve local-looking energy while moving the selected band or rank. Certification must fall to `engineering_evidence`.
3. **Curvature injection**: preserve high pairwise lineage while composing a nontrivial loop holonomy. Signed authorization must fail when the angle exceeds budget or `det(H) < 0`; block energy may remain stable.

If Silico cannot generate one of these controls natively, export the underlying basis/transport arrays needed by the repository's existing tamper generator.

## Required output bundle

Write one directory whose contents are sufficient for an independent replay:

```text
silico_patchwise_qwen17/
  run_manifest.json
  blocked_capability.json                 # only when applicable
  site_measurements.jsonl
  subspace_bases.npz
  subspace_index.jsonl
  edge_receipts.jsonl
  loop_receipts.jsonl
  patch_plan.json
  anchor_records.jsonl
  lineage_certificates.jsonl
  vpd_candidates.jsonl
  matched_controls.jsonl
  construction_split_summary.md
  sha256_manifest.json
```

### Minimum `run_manifest.json` content

- model ID, revision, shard hashes, tokenizer hash;
- Silico version/build and export settings;
- prompt-manifest and protocol hashes;
- exact site universe and activation-object definition;
- random seeds, precision, device, and timestamps;
- split-access log;
- supported and unsupported requested operations;
- P1a and P1b decisions with numeric margins;
- whether any intervention was executed and why it was authorized.

### Minimum candidate fields

Each row in `vpd_candidates.jsonl` must contain:

- `candidate_id`, `pair_id`, `arm`, `site_id`;
- `run_replicate`, `prompt_group`, `family`;
- `norm`, `rank`, `contrast_type`;
- `layer_index`, `component_type`, `direction_policy`;
- `jacobian_visibility`, `baseline_activation_rms`;
- `identity_stratum`;
- reference basis hash, current basis hash, transport-path hash;
- candidate tensor hash and matched-control tensor hash.

Do not include audit/outer outcomes in this file.

## Decision table

| Condition | Certification/output | Allowed use |
| --- | --- | --- |
| Provenance incomplete or measurement unsupported | invalid/unavailable | Stop; diagnostic report only |
| Repeatable local geometry absent | P1 fail | Stop before edits |
| Geometry present, lineage below threshold | engineering evidence | Descriptive analysis only |
| Lineage passes, loops unavailable | lineage certified | Gauge-invariant energy analysis only |
| Lineage passes, loop angle over budget | lineage certified | No signed use |
| Any `det(H) < 0` | lineage certified plus orientation flag | No signed use |
| Lineage and all loop gates pass | holonomy clean | Candidate signed use may be submitted to existing `certify(site)` policy |

Passing this table does not itself authorize a model write. The repository attestation API remains the authority for named consumers.

## Final report language

Use exactly one of these conclusion forms:

- **Pass:** “Target-blind, behavior-family-local identity patches were measured under the registered lineage and holonomy rules. Causally useful edit value remains to be established by the frozen matched-control scorer.”
- **Fail:** “No admissible local identity object was measured under the registered construction. No signed edit or recursive experiment is authorized.”
- **Unavailable/invalid:** “The requested identity object could not be evaluated because the registered instrument or provenance requirements were not satisfied.”

Never state that Silico discovered recursive self-improvement, a compactified capability, a safe edit, or a global behavioral atlas from this run.
