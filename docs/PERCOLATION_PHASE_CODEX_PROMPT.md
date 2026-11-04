# Codex prompt: percolation phase structure of the lineage bifiltration (v0.1)

Copy everything below the line into a Codex session rooted at this repository.

---

## Context you must load first

Read, in order:

1. `rsi_topology/bifiltration.py` — `build_lineage_holonomy_bifiltration` admits
   edges at a single frozen `lineage_floor` and reports components, `beta_1`,
   and admitted loops.
2. `rsi_topology/rank1_w1.py` — rank-one O(1) edge-transport signs, coboundary
   gauge action, and the first Stiefel--Whitney class `w1` as the loop
   character.
3. `rsi_topology/confinement_experiments/` and `experiments/06_spin_glass.py` —
   the registered work-unit/receipt experiment pattern this task must follow.
4. `reports/QWEN08_DENSE_LOCAL_HOLONOMY_V0_1.md` and
   `reports/QWEN08_RANK1_W1_REANALYSIS_V0_1.md` — the empirical phenomenology
   the harness must be able to reproduce descriptively.

## Mathematical object

The lineage bifiltration is an inhomogeneous bond-percolation filtration.
Sweeping `lineage_floor` tau from 1 down to 0 over the registered transport
graph produces a right-continuous step process whose jump set is exactly the
sorted distinct edge retentions. Three ordered critical floors are exact
(no estimation) once the receipts are fixed:

- `tau_conn`: the largest floor at which the registered node set is one
  connected component (equivalently, giant-component emergence on these
  finite graphs);
- `tau_cycle`: the largest floor at which `beta_1 > 0`, i.e. holonomy becomes
  structurally available;
- `tau_loop`: the largest floor at which at least one *registered* loop is
  admitted.

Always `tau_loop <= tau_cycle` when both are defined. There is no universal
ordering between `tau_cycle` and `tau_conn`: a high-retention cycle may form
inside one disconnected component before a low-retention bridge connects the
registered node universe.
The dense-local Qwen0.8B result already exhibits the anisotropy this exposes:
checkpoint edges survive to floor ~0.9958 while context edges control the
transition near ~0.89–0.91. Edge classes are therefore first-class: every
curve is reported globally and per edge class.

On top of the percolation layer sits the Z/2 gauge (spinor) sector. At rank
one the edge-sign cochain is a Z/2 gauge field; node frame flips act by
coboundaries; the gauge-invariant content of the sign assignment is the
evaluation of `w1` on the cycle space. Define, for a fixed floor tau:

- the **syndrome** `s(tau)` in GF(2)^{beta_1(tau)}: the vector of loop signs
  (0 for +1, 1 for -1) over a cycle basis of the admitted graph;
- `w1_trivial(tau)` iff `s(tau) = 0`, equivalently iff the negative-edge set
  is a GF(2) coboundary (a cut) of the admitted graph;
- the **frustrated-cycle cluster decomposition**: connected components of the
  graph whose vertices are frustrated basis cycles and whose adjacency is
  shared admitted edges; report cluster count, sizes, and largest-cluster
  fraction of `beta_1`;
- the **coboundary distance** `d(tau)`: minimum number of edge sign flips
  making every cycle positive. Compute it exactly by minimum-weight coset
  enumeration when `|admitted edges| - rank_GF2(cycle-edge incidence) <= 20`
  (always true at the current graph scale of ~10 edges); otherwise report the
  edge-disjoint-frustrated-cycle lower bound and a greedy upper bound, and
  label the pair as bounds, not a value.

The two-parameter object of interest is the phase diagram over
`(tau, q)`, where `q` is a sign-flip noise rate applied to edge transports:

- **disconnected phase**: no spanning component (no transportable identity);
- **coherent phase**: connected and `w1_trivial` (identity globally
  transportable; a global section of the line bundle exists);
- **frustrated phase**: connected but frustrated clusters span a nonzero
  fraction of the cycle space (identity exists but is path-dependent; sign
  errors are no longer removable by local reframing).

The frustrated phase is the percolation-side shadow of the confinement
regime already studied in `experiments/06_spin_glass.py`; do not merge the
two suites, but reuse their common infrastructure.

## Deliverables

### 1. `rsi_topology/percolation.py`

New module, same defensive style as `bifiltration.py` (frozen dataclasses,
`to_dict`, explicit validation, assertion cross-checks). Public API:

- `lineage_percolation_curve(*, edges, loops=(), registered_nodes=(),
  edge_classes=None) -> LineagePercolationCurve`
  Sweep every distinct retention value (plus floors 0.0 and 1.0), delegating
  each evaluation to the existing `build_lineage_holonomy_bifiltration` —
  do not reimplement admission logic. Emit per-floor records (floor,
  admitted edge count, component count, largest component fraction,
  `beta_1`, admitted registered loop count) plus the exact critical floors
  `tau_conn`, `tau_cycle`, `tau_loop`, globally and per edge class when
  `edge_classes` (a mapping edge_id -> class label, e.g. `checkpoint` /
  `context`) is supplied. Cross-check: the curve must be monotone in
  admitted edges as the floor decreases; assert it.
- `sign_syndrome(*, cycle_basis_edge_ids, edge_signs) ->
  SignSyndrome` with fields: GF(2) syndrome vector, GF(2) rank of the
  cycle-edge incidence matrix, `w1_trivial`, frustrated cycle ids.
  Gauge-invariance test hook: the syndrome must be invariant under any
  node-frame flip (coboundary added to `edge_signs`).
- `frustrated_clusters(*, syndrome, cycle_basis_edge_ids) ->
  FrustratedClusterReport`: decomposition, sizes, largest fraction.
- `coboundary_distance(*, cycle_basis_edge_ids, edge_signs) ->
  CoboundaryDistance`: exact by coset enumeration under the dimension guard
  above; bounds otherwise; the receipt must state which mode ran.
- `percolation_phase_point(*, edges, loops, registered_nodes, edge_signs,
  lineage_floor) -> PhasePoint`: combine the above at one floor and classify
  into `disconnected | coherent | frustrated`, with the raw quantities in the
  receipt so the label is re-derivable.

No new attestation level. All outputs are diagnostics on already-admitted
objects; when consumed by attestation code the cap remains exactly what the
existing bifiltration status implies.

### 2. Synthetic ensemble null

In `rsi_topology/percolation.py` or a sibling `percolation_null.py`:

- retention-permutation null: shuffle observed retentions over the fixed
  registered topology (within edge class, and also pooled — two named nulls,
  never silently mixed);
- sign-noise ensemble: flip each edge sign independently with probability
  `q`, seeds via `numpy.random.SeedSequence` spawned from (experiment id,
  cell id, root seed) exactly as `confinement_experiments/common.py` does.

Each null run emits the same curve/phase receipts as the empirical path so
observed-vs-null comparison is column-for-column.

### 3. `experiments/07_percolation_phase.py`

Follow the registered confinement-suite pattern exactly (`config.json`,
`environment.json`, `work_units/*.json`, `aggregate.csv`, `aggregate.json`,
`metrics.json`, `figure.png`, `REPORT.md`, `checksums.json`,
`run_receipt.json`; implementation-specific work-unit filenames; one BLAS
thread per process). The experiment maps the `(tau, q)` phase diagram on a
registered synthetic graph family shaped like the real object: L layers by
C context columns, rectangular loops as in `rank1_w1.LoopInterval`,
checkpoint and context edge classes with independently configurable
retention distributions. Metrics per cell: phase label frequencies, mean
largest-component fraction, mean largest frustrated-cluster fraction, mean
coboundary distance, and finite-size scans over C. Provide
`configs/pilot/07_percolation_phase.yaml` sized to complete on CPU in
minutes; the full configuration is a specification only and must not be
launched from tests, smoke, or packaging.

### 4. Tests (`tests/test_percolation.py`)

Exact small cases, no tolerance games:

- triangle with one negative edge: `beta_1 = 1`, syndrome rank 1, frustrated,
  coboundary distance 1;
- 4-cycle with two negative edges forming a cut: `w1_trivial` true,
  distance 0;
- theta graph (two independent cycles) with one shared negative edge:
  both cycles frustrated, one frustrated cluster of size 2, distance 1;
- gauge invariance: random node flips leave every syndrome, cluster, and
  distance receipt bit-identical;
- curve exactness: for a hand-built 5-edge graph, the step function equals
  the hand-computed table at every distinct retention, and
  the guaranteed `tau_loop <= tau_cycle` ordering holds where defined; add a
  disconnected-cycle counterexample demonstrating that `tau_cycle > tau_conn`
  is possible and must not be rejected;
- degenerate guards: empty edges, duplicate ids, retentions outside [0, 1].

`python -m pytest -q` must pass in full (149 existing tests plus new ones).

### 5. Protocol and docs

- `protocols/percolation_phase_v0_1.json`: frozen grid, seeds, graph family,
  null definitions, and the three phase-label decision rules, hashed in the
  style of the existing protocols;
- `docs/PERCOLATION_PHASE.md`: the mathematical object section above,
  the API, the run commands, and an explicit claim boundary: this suite is
  synthetic-calibration and retrospective-descriptive machinery; it
  authorizes no causal stage, no edit, no VPD reopening, and adds no
  attestation level.

## House rules (non-negotiable)

- No live model training, generation, or weight mutation.
- Retrospective analyses are labelled retrospective; nothing here converts
  the already-revealed Qwen0.8B elementary signs into confirmatory evidence.
- The Qwen3-1.7B VPD comparator is never pooled with natural-feature
  line-bundle results.
- Deterministic seeds, bounded CPU-only jobs, receipts for every run.
- Reuse `build_lineage_holonomy_bifiltration`, `rank1_w1` sign utilities,
  and `confinement_experiments` runner infrastructure instead of forking
  them.

## Follow-up experiments (register separately after the harness lands)

**Stage A — retrospective empirical curves (engineering_evidence).** Apply
`lineage_percolation_curve` to the frozen Qwen0.8B dense-local edge receipts
at layers 11, 15, 19, 23. Report per-class critical floors and locate the
frozen `lineage_floor` relative to `tau_cycle`. Falsifiable descriptive
prediction, stated before running: context edges determine `tau_conn` at all
four layers and checkpoint edges are never critical; layer 15's
`holonomy_unavailable` status corresponds to `tau_cycle` sitting below the
frozen floor, not to a missing cycle space at floor 0.

**Stage B — confirmatory sign percolation on fresh geometry.** Joint with
the already-proposed context-restricted capture around the four locally
rank-4 graph-reachability nodes (one full-precision layer control).
Preregister: (i) the fresh cycle basis satisfies `w1 = 0` with the existing
Clopper--Pearson margin style; (ii) the empirical `(tau, q)` location of the
fresh graphs falls in the coherent phase of the synthetic diagram at matched
size. This is the first genuinely out-of-sample `w1` test; frame it that
way in the protocol.

**Stage C — ALife extension (optional, may live in a separate repo).**
Population of agents, each carrying a local frame (a fiber); heredity and
interaction events create edge transports whose retention and sign-flip rate
are set by a mutation/noise parameter; selection acts on task performance,
not on topology. Measured question: do evolved populations self-organize
toward the coherent-phase boundary (`w1 = 0` maintained on a giant
component near `tau_conn`), i.e. is heritable identity under maximal
plasticity an attractor? The phases give crisp operational readouts:
disconnected = no heredity, coherent = species-like transportable identity,
frustrated = path-dependent identity (hybridization-incompatibility
analogue as a nonzero `w1` class). Reuse `experiments/07`'s receipts so the
evolutionary runs are directly comparable to the static phase diagram.
