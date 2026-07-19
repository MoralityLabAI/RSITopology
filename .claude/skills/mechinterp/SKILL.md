---
name: mechinterp
description: Distilled methodology for identity-geometry mechinterp in this program — gauge-invariant holonomy, rank boundaries, percolation thresholds, evidence discipline, and harness cost rules. Load before designing, running, or reviewing any capture, geometry analysis, protocol, or interpretation of receipts.
---

# Mechinterp methodology (distilled from RSITopology receipts, 2026-07)

Every rule below was paid for by a real run. Citations point at the report
that taught it; read the report only when you need the full derivation.

## 1. The instrument lies in specific ways — know them

- **Lineage is not identity.** Principal-angle/retention statistics discard
  the polar factor `Q` of `U_b^T U_a`, and `Q` is what transports signed
  coordinates. A system can beat a flat control on *every* retention metric
  and still return a monitor rotated −62° after one loop. Never certify a
  signed use from retention numbers alone; demand loop holonomy.
  (`silico_reports/reports/monitor_holonomy_insight.md`)
- **A convenient basis is not an identity certificate.** Only gauge-invariant
  quantities count: singular values, holonomy conjugacy classes (`det(H)`,
  sorted canonical angles, trace), GF(2) syndrome classes. Anything that
  changes under a node reframing is bookkeeping, not evidence.
- **Report the invariant that exists at the measured rank.** At rank one,
  `SO(1)` is trivial — there is no rotation angle to estimate; the real
  invariant is the `O(1)` sign class, i.e. `w1` on the cycle space. An empty
  angle spectrum at rank 1 is a mathematical boundary, not evidence of
  flatness. (`reports/QWEN08_RANK1_W1_REANALYSIS_V0_1.md`)
- **`det(H) < 0` is a categorical failure.** Suppress canonical-angle
  interpretation entirely; orientation reversal caps certification and blocks
  signed use. No averaging across it.
- **Covariance/Gram objects are unstable; cross-fitted between-class scatter
  survives.** v0.3 made covariance output `reported_ungated` for a reason.
  Default to between-class scatter for new constructions.

## 2. Rank and sample support

- **Rank recovery is a detectability threshold, not a fixed property.**
  Two replicas per cell → total collapse; sixteen → a clean rank-1 line
  bundle, with four nodes locally rank 4. Before buying a capture, treat
  "replicas needed to support rank r" as a spiked-model (BBP-type)
  calculation, not a guess. (`reports/QWEN08_DENSE_LOCAL_HOLONOMY_V0_1.md`)
- **The common-grid rule is deliberately conservative:** a cell's rank is the
  minimum supported rank over all its nodes. Higher-rank local fibers that
  don't survive every context shard are real but demand context-conditioned
  patches (a Čech cover with overlaps), not a global fiber. Design triple
  overlaps into the capture — `w2`/spin-structure data on patch overlaps
  cannot be reconstructed retroactively from pairwise receipts.
- **Context is the weak axis; checkpoints are clean.** Checkpoint-edge
  retentions sit near 0.996–0.999; context edges near 0.89–0.93 and they set
  every critical threshold. Spend capture budget on context replication, not
  more checkpoints. (Confirmed twice: dense-local run, percolation Stage A.)

## 3. Thresholds and percolation

- **Any frozen floor is one point of a filtration — always compute the whole
  curve.** Exact critical floors on finite receipts: `tau_conn`
  (connectivity), `tau_cycle` (β₁ > 0), `tau_loop` (a registered loop
  survives). Theorem: `tau_loop <= tau_cycle` when both are defined.
  **No universal order between `tau_cycle` and `tau_conn`** — cycles can
  close inside a component before the node universe connects, and the Qwen0.8B
  receipts show `tau_cycle > tau_conn` at all four layers. Do not preregister
  the wrong ordering. (`reports/QWEN08_PERCOLATION_REANALYSIS_V0_1.md`)
- **`holonomy_unavailable` may be a threshold artifact.** L15 had β₁ = 0 at
  the frozen 0.9 floor but β₁ = 3 in the full graph, with `tau_cycle` only
  0.002 below the floor. Always report the fragility margin
  `|tau_frozen − tau_cycle|`; a small margin means the status flag is sitting
  on the critical surface and is not stable evidence.
- **Phase labels:** disconnected / coherent (connected, `w1` trivial) /
  frustrated (connected, frustrated cycles). The window between `tau_conn`
  and `tau_cycle` is cyclic-but-fragmented — keep β₁ and the syndrome in the
  receipt so the finer state is re-derivable. Sign-flip noise `q` makes this
  a (τ, q) diagram; the frustrated phase is the percolation shadow of the
  spin-glass/confinement suite (random-bond Ising / toric-code family —
  coboundary distance is code distance; exact coset enumeration at ≤ ~20 free
  dimensions, labeled bounds beyond, never a silent heuristic).

## 4. Evidence discipline (non-negotiable)

- **Retrospective stays retrospective.** If elementary results were revealed
  before the protocol froze, derived composites validate the *instrument*,
  never the hypothesis. Report would-be p-values descriptively and say so.
  Fresh held-out geometry is the only path to confirmatory status.
- **Never pool non-comparable objects.** Model, object type, rank, and
  protocol must all match. The Qwen3-1.7B VPD weight-component comparator is
  never pooled with natural-feature line-bundle results; a full `w1`
  comparison needs the comparator's bound edge cocycle and cycle basis.
- **Target blindness:** features, subspaces, patches, candidates, and hashes
  are sealed before any outcome is read. No threshold tuning on revealed
  outcomes. Geometry gates are necessary-but-not-sufficient; report occupancy
  margins so fragility is visible.
- **Attestation levels are closed:** `engineering_evidence` <
  `lineage_certified` < `holonomy_clean`. Never introduce a new level; new
  diagnostics attach to existing levels. Signed interventions require
  `holonomy_clean`; energy rewards require `lineage_certified`.
- **Two estimands, never mixed:** direction value within a site vs site
  selection across identity-matched sites. Never pooled across identity
  strata or with each other.
- **A mixed result must decouple:** keep the positive finding, reject the
  overreaching claim, leave downstream authorizations closed. The dense-local
  run is the template — rank-one object retained, continuous-holonomy claim
  rejected, no stage reopened.

## 5. Controls that must exist before a claim

- **Label-permutation null** matched on site, rank, prompt count, spectrum,
  and RNG stream — a mismatched null proves nothing.
- **Three adversarial tampers:** spectrum-preserving conjugation (lineage
  must catch it), band failover (certification must drop to
  `engineering_evidence`), curvature injection (signed authorization must
  fail while block energy stays flat).
- **Two named retention nulls** for graph statistics: within-edge-class and
  pooled permutation — never silently mixed.
- **Gauge preflight:** loop reframings must produce zero determinant-decision
  mismatches before any holonomy number is reported.
- **Precision claims need a separately captured full-precision path.**
  float32-vs-float64 agreement on arrays from one 4-bit runtime proves
  analysis stability only, not runtime-precision stability.

## 6. Run mechanics

- Frozen protocol JSON with SHA-256 before execution; result hashes after;
  deterministic `SeedSequence` spawned from (experiment id, cell id, root
  seed); bounded Windows Job Objects (RAM/CPU/IO caps, fail-closed);
  implementation-specific work-unit filenames so receipts can't be reused
  across code changes. Follow `rsi_topology/confinement_experiments/` — do
  not fork the runner.
- Repository tests must pass before execution; record the count in the
  report.

## 7. Harness cost discipline (LLM-driven runs)

- **Feed receipts, not raw data.** The compact receipt/hash design exists for
  integrity, but it is also the context interface: never paste activation
  arrays, full logs, or whole reports when the receipt or its hash suffices.
- **Stable prefix = cached prefix.** Keep frozen content (briefs, protocols,
  tool lists) byte-identical at the front of the prompt; volatile content
  (timestamps, run ids) goes last. Cache reads are ~0.1× input price; a
  broken cache silently pays full price every turn.
- **Tier the models.** Mechanical execution (captures, bootstraps, replay)
  does not need the most expensive model; reserve top-tier capacity for
  protocol design, insight generation, and adversarial review. Batch API is
  50% off for anything non-interactive.
- **Executor judgment is untrusted by design.** An LLM executor emits sealed
  measurements and `blocked_capability` reports; it does not alter gates or
  conclusion language. Its tacit knowledge enters the program only as
  pre-registered falsifiable predictions.

## Claim boundary (append to every report)

State explicitly what the result does **not** establish: semantic identity,
causal edit value, capability preservation, compactification, recursive
improvement, or RSI — unless a frozen protocol specifically tested it.
