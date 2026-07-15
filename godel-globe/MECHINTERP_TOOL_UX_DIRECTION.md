# Mechinterp tool UX direction: from feature inspection to identity-aware control

## Product thesis

Most mechanistic-interpretability interfaces are organized around discovery: find a neuron, latent, direction, head, circuit, or attribution path that appears related to a behavior. That is useful, but it leaves a second question implicit:

> Does this internal object continue to denote the same thing across prompts, contexts, checkpoints, and model variants strongly enough to support a comparison or intervention?

The RSITopology work suggests that this should be a distinct product layer. Feature visibility is not feature identity. A direction can remain locally salient while its coordinate meaning rotates, changes band, loses rank, or becomes path-dependent. Pairwise handoff tests can all look good while a closed chain returns a signed coordinate in a different orientation.

A mature mechinterp tool should therefore do more than display internal features. It should help users establish what kind of identity claim the available evidence supports, show where that claim breaks, and gate downstream uses accordingly.

The Gödel globe is one view into that layer. It is not a picture of a transformer's literal geometry. It is an audit map for measured relationships among registered internal objects.

## What the globe gets right

### 1. It makes local evidence and global consistency visibly different

Nodes, edges, and loops answer different questions:

- A node says that an internal object was measured at a registered site.
- An edge says how well a subspace or feature block transfers between two sites.
- A loop asks whether those locally good transfers compose to a globally consistent identity.

This distinction is difficult to communicate with a table of principal angles. On the globe, a user can see strong local lineage along every edge and still select a loop whose frame returns rotated. The animation makes the failure mode concrete without pretending to reveal where curvature is distributed: the frame traverses the measured path, then the receipt's closure rotation is applied.

### 2. It treats orientation reversal categorically

`det(H) < 0` is not rendered as a very large ordinary angle. It is a different kind of failure. Suppressing the angle spectrum, snapping the loop into a hard red dashed path, and disabling the rotation animation prevents a continuous chart from hiding a discrete identity break.

This is a good general UX rule for interpretability tools: categorical validity failures should not be buried inside continuous confidence scores.

### 3. It exposes instrument limits rather than converting them into structure

The calibration floor distinguishes a measured small angle from a resolvable one. A below-floor loop stays present but loses visual emphasis and is described as flat within the instrument floor. Missing edges, invalid loops, absent angles, and unsupported holonomy are likewise different states from a clean measurement.

The interface should preserve at least four epistemic states throughout the product:

- established within the registered instrument;
- failed against a registered boundary;
- unavailable because the necessary measurement was not made;
- invalid because provenance or construction requirements were violated.

Collapsing the last three into “low confidence” would make the tool easier to scan and much easier to misuse.

### 4. It connects provenance to interaction

Hashes, edge order, root fiber, rank, determinant, angle spectrum, identity loss, and certification margins are available from the selected object. The visual surface is therefore not detached from the receipt layer.

That matters because a mechinterp visualization should be an entry point into a reproducible claim, not the claim itself. Every interesting mark should lead back to the exact tensor, basis, prompt universe, transform, and protocol that produced it.

## The globe's proper role

The globe is best used for orientation, triage, and audit placement:

- locate high-curvature or orientation-reversing regions;
- see whether failures cluster by family, layer, or model state;
- compare inner and outer model-state shells;
- identify loops that deserve closer inspection;
- explain why pairwise monitor-transfer tests can miss a global inconsistency;
- communicate the distinction between gauge-invariant block energy and signed-coordinate identity.

It should not become the primary numerical analysis environment. Three-dimensional layouts introduce occlusion, perspective distortion, and a temptation to read presentational distance as model distance. Exact comparison belongs in coordinated tables, plots, and receipt views.

The strongest design is therefore a linked system:

1. the globe for spatial triage;
2. a receipt inspector for exact evidence;
3. a patch or matrix view for comparison across families and layers;
4. an experiment-authoring view for matched interventions and controls.

Selecting an object in any view should select the same registered object everywhere else.

## A better default workflow for mechinterp tools

### 1. Ingest

Load activations, features, Jacobian measurements, candidate subspaces, model states, prompts, and provenance. Validate shapes, identifiers, hashes, and the registered site universe before displaying scientific conclusions.

Unknown extra fields can be retained or ignored. Missing required fields cannot be silently imputed.

### 2. Construct target-blind objects

Feature discovery, band selection, subspace fitting, transport estimation, and patch construction should occur without behavioral outcomes that will later evaluate the object. The interface should show which split was available to each operation.

This could be represented as a compact access ledger rather than a generic “train/test” badge:

- construction data available;
- selector data sealed or available;
- audit data sealed;
- outer outcomes sealed.

### 3. Stress identity before interpreting semantics

Before asking what a feature means, test whether it is stable enough to carry meaning across the intended scope. The relevant controls should be first-class actions:

- spectrum-preserving conjugation;
- band failover;
- matched-lineage curvature injection;
- prompt-family permutation;
- estimation-noise and calibration-floor checks.

A semantic label should be scoped to the identity patch on which it was established, not attached permanently to one coordinate index.

### 4. Certify a use, not an object in the abstract

Certification should always name the requested consumer and operation. The same evidence can be sufficient for one use and insufficient for another:

- descriptive engineering evidence can support exploration;
- lineage certification can support gauge-invariant block-energy summaries;
- signed rewards, signed activation interventions, and disparate weight edits require holonomy-clean identity under the current policy.

The central UI action should therefore be closer to:

```text
certify(site, requested_use)
```

than to a universal “feature confidence” score.

The result should include the attained level, required level, authorization decision, exact margins, and specific failure reasons. A blocked action should answer “what failed, by how much, and what new measurement could resolve it?”

### 5. Propose matched interventions

Once an identity object passes its construction gate, the tool can generate an intervention and its controls together. A VPD-oriented interface should keep two estimands separate:

- selected direction versus a matched-random direction at the same site;
- selected site versus a matched-random site under a fixed direction policy.

Rank, norm, Jacobian visibility, baseline activation RMS, family, prompt group, and identity stratum should be visible before sealing. Unsupported matches should appear as unsupported, not disappear from the analysis.

### 6. Seal, execute, and reveal

The interface should make prereveal state tangible. Candidate tensors, assignments, filters, thresholds, protocol, source universe, and evaluator should receive hashes before outcomes are joined. After sealing, changes should require a versioned extension rather than an editable notebook cell.

This is not bureaucracy added after the research. It is part of the measurement UX: it tells a reviewer which choices were made without access to the result.

## How to represent high-dimensional structure

A mechinterp tool should resist the urge to draw 512-dimensional objects as if the drawing recovered their shape. The useful visual targets are invariants, relations, and failure boundaries:

- spectrum and effective-rank profiles;
- principal-angle and worst-direction-retention distributions;
- gauge-invariant subspace overlap;
- transport paths and loop closure;
- determinant/orientation state;
- identity patches and their persistence over budgets;
- causal effect relative to matched controls;
- uncertainty and instrument floors.

The globe follows this rule when it uses spatial embedding only as a navigational scaffold. Latitude represents layer order, shell radius represents model state, and loop animation represents a receipt value. It does not claim that chord length, globe curvature, or swirl density is transformer geometry.

That separation between data-bearing channels and decorative channels should be made systematic. A useful “view legend” could classify every encoding as:

- measured;
- derived under a registered rule;
- categorical metadata;
- presentational only.

## Product surfaces that should come next

### Identity patch view

The next high-value surface is a two-dimensional family × layer matrix showing maximal flat patches, lineage and holonomy margins, unmeasured boundaries, and the edit-count-versus-budget persistence curve. This is more actionable for VPD than the globe because it answers where one coordinate may be reused and where a separate edit is required.

### Audit planner

Unmeasured loops should be ranked by expected reduction in patch-boundary uncertainty. The user should see why a proposed measurement is valuable: which components it might merge or split, its current classification interval, and the downstream authorizations affected.

The planner should distinguish “high estimated curvature” from “high estimator noise.” Otherwise the tool will spend audits chasing the weaknesses of its own measurement process.

### Intervention composer

The composer should begin with a certified patch, not an arbitrary tensor address. It should show:

- canonical root and frozen transport path;
- requested signed or energy-based operation;
- rank and norm budget;
- matched control construction;
- affected prompts and sites;
- authorization result;
- expected failure modes;
- a preview that never writes weights until explicitly executed.

When curvature makes signed transport path-dependent, the interface must not hide that ambiguity by choosing a convenient route. The registered spanning-tree path is the canonical operational convention; off-tree edges are audits.

### Before/after receipt diff

Model comparison should be receipt-aware. Instead of only showing activation deltas, show changes in:

- selected band and rank;
- lineage margins;
- loop determinant and angle spectrum;
- patch membership;
- authorization level;
- downstream matched-control effect.

This would make a model update legible as a change in the identity contract, not merely a change in average benchmark behavior.

## Three user modes

### Researcher

The researcher needs rapid exploration, raw tensor access, alternative estimators, and negative results. Exploratory objects should be visually distinct from registered objects, and promoting an object into a registered experiment should freeze its choices.

### Control engineer

The control engineer needs simple authorization queries, bounded failure reasons, patch plans, and audit priorities. They should not need to interpret a principal-angle spectrum to decide whether a signed monitor signal can be reused.

### Reviewer or auditor

The auditor needs replayable receipts, exact universes, hash chains, split access, missingness, null controls, and a total decision mapping. The interface should allow a result to be reconstructed without trusting the visual layout or the model that proposed the interpretation.

A strong product can expose the same underlying object at three levels of detail rather than building three disconnected applications.

## Failure modes to avoid

### Smoothness theater

A smooth embedding or interpolation can imply that a stable mechanism exists between observed points. The interface must distinguish measured edges from visual interpolation and unmeasured regions from low-curvature regions.

### Saliency as identity

Repeatedly high activation, attribution, or Jacobian visibility is evidence of local relevance, not necessarily stable coordinate identity. The tool should never promote saliency directly into edit authorization.

### Universal feature names

Human-readable feature labels are useful indexes, but they should be attached to a model state, site, family, patch, estimator, and evidence scope. Labels outside that scope are hypotheses.

### One confidence number

Provenance validity, measurement reliability, lineage, holonomy, causal utility, and safety are different axes. Compressing them into one score makes it impossible to tell what evidence is missing.

### Silent negative-result rescue

If a global atlas fails, the product may offer a versioned local-patch hypothesis, but it should not silently relax the global threshold, remove difficult prompts, or reinterpret an unavailable component as a pass.

### Visual authority without receipts

Beautiful circuit diagrams can acquire more epistemic authority than their generating measurements deserve. Every visual conclusion should be inspectable as a receipt and reproducible from exported data.

## Practical roadmap

### Stage 1: receipt viewer

The current globe establishes the basic interaction grammar:

- defensive local JSONL ingestion;
- node, edge, and loop navigation;
- certification halos;
- measured closure animation;
- determinant and instrument-floor handling;
- provenance inspection;
- zero-build local operation.

This stage is useful for communication and manual triage. It is not yet an experiment-control surface.

### Stage 2: linked identity workbench

Add the patch matrix, persistence curve, null comparison, audit planner, and synchronized selection. Import Silico or another mechinterp tool's raw feature/circuit exports, then emit RSITopology-compatible anchor, edge, loop, and certificate receipts.

The important integration boundary is an artifact contract, not a bespoke screenshot or hidden backend call.

### Stage 3: registered intervention workflow

Add candidate/control generation, use-specific certification, sealing, exact outcome joins, and before/after receipt diffs. Keep model mutation in a separate explicit execution step with a durable receipt.

### Stage 4: training and monitor lifecycle

Track identity through checkpoints, fine-tuning runs, monitor updates, and reward-model revisions. Surface re-anchoring as a first-class event and require loop-closure audits when a signed coordinate crosses a registered boundary.

## Product evaluation

The tool should be judged by control and research outcomes, not only by whether users enjoy the visualization. Useful measures include:

- time to identify a deliberately planted identity break;
- false-authorization rate under spectrum-preserving, band-failover, and curvature attacks;
- fraction of blocked actions with a correct, actionable failure explanation;
- audit measurements saved per resolved patch boundary;
- reproducibility of a conclusion from exported receipts;
- agreement between researchers on what is measured, unavailable, and merely suggested;
- causal uplift over matched controls within preregistered identity strata;
- rate at which semantic feature labels survive held-out contexts without re-anchoring.

For the globe specifically, a comprehension test matters more than visual preference: after using it, can a technically literate user explain why high pairwise lineage does not guarantee a globally stable signed coordinate?

## Positioning

The concise product claim is:

> Mechanistic interpretability tools help users find internal features. An identity-aware control layer determines where those features continue to refer to the same object strongly enough to compare, transport, reward, or edit.

This complements tools such as Silico rather than competing with their feature-discovery interface. Silico can supply candidate features, circuits, activations, and interventions. The RSITopology layer supplies a target-blind identity contract, matched adversarial controls, use-specific certification, and durable receipts.

For VPD, this turns “edit this attributed direction” into “edit within this certified patch, along this registered coordinate, against these matched controls.” For HRMmmm, it turns “trust this monitor feature” into “authorize this use only while its identity certificate remains within margin.” For a reviewer, it turns an appealing mechanistic story into a replayable claim with explicit boundaries.

## Bottom line

The most promising direction is not a more elaborate neuron browser. It is a mechinterp workbench that treats identity stability as an object users can measure, falsify, certify, and monitor over time.

The Gödel globe is a strong front door because it makes loop inconsistency intuitive. The durable product value lies behind it: scoped feature names, target-blind construction, matched controls, patchwise coordinates, explicit instrument failure, and authorization rules that connect interpretability evidence to actual control decisions.
