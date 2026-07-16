# RSI Topology: Spectral-Bundle Discovery

This repository turns the JSpace harmonic/global-section diagnostic into a
bounded discovery program for high-dimensional structures. The current object
is not graph topology by itself and not a guessed coordinate tuple. It is a
stable spectral bundle: a high-occupancy eigenspace of the mean projector for
a frozen band of prompt-specific, reliability-weighted sheaf Laplacians.

Two downstream hypotheses are kept separate:

1. **RL allocation:** energy in the frozen bundle improves held-out prediction
   and supports a candidate-sampling tilt whose KL divergence from the base
   policy is capped.
2. **Coordinated edits:** signed coordinates in the bundle improve held-out
   prediction beyond nuisance variables and Jacobian visibility, and beat a
   matched-rank Haar subspace. Discovery emits a normalized proposal and hash;
   it does not apply the edit.

## Identity-attestation consumers

The spectral-bundle, lineage, and holonomy stack is exposed as a three-level
identity contract for `hrmmmm_control_harness`, `vpd_edit_program`, and
`blue_beam`. It adds no invariant level. The frozen runtime rule is:

- signed rewards, signed interventions, and disparate weight edits require
  `holonomy_clean`;
- bundle-energy rewards require `lineage_certified`;
- all other uses are labelled `engineering_evidence`.

`AnchorRegistry.certify(site)` returns the attained and required level,
authorization, exact threshold margins, failure reasons, and the sealed anchor
hash. See [docs/IDENTITY_ATTESTATION_INTEGRATION.md](docs/IDENTITY_ATTESTATION_INTEGRATION.md)
for the HRMmmm, Blue Beam, and VPD commands.

VPD protocol v0.2 preregisters two non-interchangeable estimands: direction
value within one site and site-selection value across identity-matched sites.
Neither may be pooled across identity strata or with the other contrast.

## Gödel globe receipt viewer

[`godel-globe/index.html`](godel-globe/index.html) is a zero-build, direct-file
Three.js viewer for edge lineage, loop holonomy, determinant flags, identity
loss, and node certification receipts. It includes a 20-node synthetic fixture,
defensive JSONL loading, measured loop-closure transport animation, receipt
filters, and copyable provenance details. See
[`godel-globe/README.md`](godel-globe/README.md) for usage and validation.

The v0.1 real-model protocol now uses the current harness rather than rebuilding
it: family-resolved v0.3 between-class objects, mandatory control calibration,
the lineage-first `beta_1` gate, precision × context loops, existing patch
sectioning, and the existing certificate API. Its deterministic 1,152-prompt
manifest and target-blind capture/replay commands are documented in
[`docs/GODEL_GLOBES_V0_1.md`](docs/GODEL_GLOBES_V0_1.md). The preserved Silico
float32/bfloat16 result is treated as calibration only.

## Holonomy-bounded edit sectioning

`section_edits()` converts context-by-checkpoint identity receipts into maximal
flat patches, one transported coordinate per patch, and explicit lineage and
holonomy margins. `persistence_curve()` reports edit count across budgets with
component birth/death receipts, while `rank_audit_placements()` prioritizes
unmeasured loops by expected patch-boundary uncertainty reduction. Patch
authorization delegates to the existing `certify()` API; holonomy remains the
top level. See [docs/EDIT_SECTIONING.md](docs/EDIT_SECTIONING.md).

The registered v0.3 crossover separates pooling variance from boundary bias.
Its recoupled control preserves the patch advantage, while every analytically
derived decoupled regime makes the patch plan lose as predicted; see
[docs/EDIT_SECTIONING_V03_RESULTS.md](docs/EDIT_SECTIONING_V03_RESULTS.md).

## Signed-control risk gate

`predict_control_gate()` combines cumulative worst-direction lineage loss,
loop holonomy displacement, orientation, uncertainty, and audit coverage into
a proved upper bound on signed-coordinate error. The registered CPU red team
achieves zero false authorizations at 13.2% selective coverage and maps the
control-loss boundary across path length, retention, and holonomy angle. The
bound does not predict general self-improvement risk; see
[docs/CONTROL_RISK_THEOREM.md](docs/CONTROL_RISK_THEOREM.md) and
[docs/CONTROL_RISK_REDTEAM_RESULTS.md](docs/CONTROL_RISK_REDTEAM_RESULTS.md).

Run the CPU synthetic controls:

```powershell
python scripts/run_synthetic_discovery.py
python -m pytest -q
```

The real-model input contract is a family of prompt-specific normalized
weighted Laplacian operators acting on one registered edit space, candidate
vectors generated without outcomes, baseline nuisance/Jacobian covariates,
independent prompt/run groups, and outcomes joined only after geometry is
sealed. The existing JSpace protocol supplies the operator/reveal half.

No live model training or weight mutation is authorized by this repository.
The June Research_Engine edit receipts lack the actual edit matrices and
source provenance required to reconstruct the geometry; they may inform power
planning but cannot validate the edit gate retrospectively.

Preserved parent engineering protocol:
`protocols/spectral_bundle_discovery_v0_2_2.json`; the current additive
amendment is `protocols/spectral_bundle_discovery_v0_3.json`. The v0.1 protocol
and its absolute-uplift failure remain preserved. Large or
model-bearing runs are currently blocked by
`reports/resource_enforcement_audit.md`; only unit-scale controls are allowed
until CPU and I/O cgroups are delegated or an approved container path exists.

## Confinement-width CPU validation

Six additive CPU experiments now test the classical data-rate/invariance-
entropy mechanism used by the Confinement Width manuscript: split read/write
rate limits, spectral scaling with `h2(A_u)`, finite-horizon margin, evaluator-
transversal modes, sufficiency-audit scaling, and spherical 3-spin sampler
robustness. Universal volume obstructions are never pooled with constructive
controller results or Monte Carlo evidence. See
[`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) and
[`docs/CONFINEMENT_VALIDATION_SUITE.md`](docs/CONFINEMENT_VALIDATION_SUITE.md).
The bounded 2026-07-16 outcomes, including the stopped spin-glass pilot, are in
[`reports/CONFINEMENT_VALIDATION_PILOT.md`](reports/CONFINEMENT_VALIDATION_PILOT.md).

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_confinement_smoke.ps1
```

The full configurations are specifications only; they are not run by tests or
smoke scripts.
v0.2.1 leaves every v0.2 primary threshold unchanged, adds environment-stamped
receipts, sparse geometry noise, occupancy-margin warnings, and a descriptive
KL-normalized information coefficient. External Fable replays remain
diagnostic-only.
v0.2.2 likewise changes no gate; it binds every geometry summary to its band
and makes selection failover explicit.

Protocol v0.3 is an additive amendment and leaves v0.2.2 unchanged. It changes
the primary lineage object to the frozen top-r eigenspace of cross-fitted
between-class scatter over family-defining class means. The prior
covariance/Gram consensus remains executable but is `reported_ungated`; no
v0.3 gate may consume it. Certification is capped at
`engineering_evidence` unless a matched random-label control clears its
permutation null by a strict margin above `0.02`.

The amendment follows the EM-pair calibration: 216 same-site state-cross
edges transported cleanly (median worst-direction retention `0.95`), while
396 adjacent-layer edges had median retention approximately `0.003`; none of
99 attempted loops survived the `0.5` persistence floor, and all 108 anchors
remained `engineering_evidence`. v0.3 therefore filters the transport graph at
the frozen lineage floor before considering holonomy. It reports
`holonomy_unavailable` when
`beta_1(G_tau) = |E_tau| - |V| + c(G_tau)` is zero; this cycle-rank condition
replaces any arbitrary “enough loops” check. See
[`protocols/spectral_bundle_discovery_v0_3.json`](protocols/spectral_bundle_discovery_v0_3.json).

The sparse fixture's `geometry_noise=0` point is a legacy-RNG compatibility
baseline. Positive-noise sweeps consume an additional skew draw and must use
their smallest positive level, not zero, as the paired reference.

The WSL delegation remediation is prepared but not applied; see
`reports/wsl_cgroup_delegation_runbook.md`. It requires explicit authorization,
a manual WSL restart, and successful memory/CPU/I/O/cleanup probes before it
can unblock model-bearing work.

An analysis of the sealed external occupancy receipts found a geometry-pass
transition where mean minimum occupancy fell only `0.0384`, but standardized
policy utility fell `73.4%` and all three edit gates flipped to fail. This
was subsequently identified as low-to-middle band failover hidden by a summary
that omitted `selected_band`. Protocol v0.2.2 adds categorical selection
stability and band-attributed margins without changing gates.

The proposal-only lineage amendment then exercises the harder case: a common
conjugation holds the selected low band, rank, complete occupancy spectrum,
candidate vectors, and outcomes fixed while rotating identity. In the unit
control, occupancy differs by at most `8.9e-16`, mean chordal lineage falls to
`0.00123`, and both downstream gates flip from pass to fail. This validates the
instrument by construction, not on a real model. See
`reports/files4_mechanism_review.md` and
`protocols/spectral_bundle_lineage_followup_v0_1_1.json`.

The imported one-seed angle sweep confirms the continuous shape: occupancy is
constant to `9e-16`, lineage is monotone, and policy uplift versus lineage has
`R^2=0.9941` through `50 degrees`. Its source omitted `65`, `75`, and `85`
degrees and overstates cos-squared precision, so it remains diagnostic. The
prepared standing calibration fills the complete grid over three seeds but is
hard-cap locked pending cgroup delegation. See
`reports/files6_dose_response_review.md` and
`protocols/lineage_angle_calibration_v0_1.json`.

Lineage retains the singular values of each subspace overlap but discards its
orthogonal polar factor. A new CPU-only control composes those polar transports
around a context-by-checkpoint loop. Flat and curved fixtures have the same
minimum edge worst-direction retention (`0.990033`), yet the curved loop accumulates `62.17`
degrees of signed-coordinate rotation while block energy remains invariant.
This validates monitor holonomy as a distinct synthetic diagnostic, not as a
transformer result. See `reports/monitor_holonomy_insight.md` and run:

```powershell
python scripts/run_monitor_holonomy_control.py --output artifacts/my_holonomy_receipt.json
```

The registered follow-up distinguishes connection curvature from subspace-
estimation noise. In the planted control, canonical rotation scales with loop
area (`R^2=0.999975`); under independently resampled subspaces on a flat
connection, signed-angle variance scales with perimeter (`R^2=0.947972`) at
matched worst-direction retention. The analytic origin-curvature target is
`85.370711` degrees per unit area; the finite-grid slope is metadata. Higher-rank
receipts report the complete sorted set of canonical SO(r) rotation-plane angles.
Every receipt first reports `det(H)`; orientation reversal suppresses the angle
summary. Signed transports must use a preregistered
rooted spanning tree; off-tree edges are loop-closure audits, since curvature
makes unrestricted parallel transport path-dependent. Run:

```powershell
python scripts/run_monitor_holonomy_noise_null.py --output artifacts/my_holonomy_noise_receipt.json
```

Prepare (but do not execute) the next one-prompt benchmark by copying
`protocols/one_prompt_run_registration_template.json`, filling every required
hash/cap, then freezing it with:

```powershell
python scripts/register_one_prompt_benchmark.py completed.json --out-dir artifacts/one_prompt_registered
```

The registration prohibits outcomes and weight mutation. Its successful gates
authorize only a later multi-prompt prereveal engineering run.
