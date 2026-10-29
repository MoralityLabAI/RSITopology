# Lineage and rank-one gauge-percolation pilot

## Result

The frozen synthetic calibration completed successfully on 2026-07-16/17.
The 24-cell smoke run and 384-cell pilot both passed every registered gate:

- registered-loop admission never occurred above the cycle threshold;
- every connected `q=0` graph was coherent (`w1=0`);
- all maximum-`q` cells executed sign flips; and
- the observed, pooled-retention-permutation, and within-class-permutation
  arms remained separately named.

The pilot is **model-only descriptive phase mapping**.  It is neither evidence
about a transformer nor evidence about an evolving population.

## The corrected threshold theorem

Only this implication is universal:

`tau_loop <= tau_cycle`.

There is no universal order between `tau_cycle` and `tau_conn`.  The tests
include an exact four-node counterexample, and the pilot reproduced the same
phenomenon without being constructed around that individual graph.  At
`C=6`, the observed mean thresholds were:

- `tau_conn = 0.88415`;
- `tau_cycle = 0.91063`; and
- `tau_loop = 0.91063`.

A high-retention cycle therefore existed inside a disconnected component
before lower-retention context edges connected the complete node universe.
Treating `tau_cycle <= tau_conn` as an invariant would have rejected a valid
phase.

## Observed phase map

At four context columns and `tau=0.85`, all four observed graph replicas were
connected.  The phase frequencies across sign noise were:

| `q` | disconnected | coherent | frustrated | mean coboundary distance |
|---:|---:|---:|---:|---:|
| 0.00 | 0% | 100% | 0% | 0.00 |
| 0.05 | 0% | 75% | 25% | 0.25 |
| 0.15 | 0% | 0% | 100% | 1.25 |
| 0.50 | 0% | 25% | 75% | 1.00 |

At `tau=0.89`, the corresponding frustrated frequencies were 0%, 25%, 75%,
and 75%.  At `tau=0.91`, three of four graphs were disconnected; at
`tau=0.95`, all were disconnected.  Once disconnected, the primary phase is
reported as disconnected even if individual components contain local cycles.

At six context columns, the finite-size transition moved downward.  All
replicas were connected at `tau=0.85`, only one of four was connected at
`tau=0.89`, and none was connected at `tau>=0.91`.  On the connected
`tau=0.85` cells, frustration again rose from 0% at `q=0` to 100% at
`q=0.15` and `q=0.5`.

The nonmonotonicity between `q=0.15` and `q=0.5` at `C=4` is legitimate
finite-graph Z/2 behavior, not a defect: an additional sign flip can cancel a
cycle parity.  The extreme `q=1` smoke arm also leaves every even rectangular
loop positive because flipping all edges is a coboundary.  Sign-flip count is
therefore only an exposure metric; `w1` is the evidence metric.

## Edge-class nulls

The within-class null preserves the anisotropic retention distributions while
moving values among edges of the same class.  The pooled null erases that
allocation.  At `tau=0.95`, pooling the high checkpoint retentions into the
context class increased the mean largest-component fraction:

- `C=4`: observed 0.250 versus pooled 0.5625;
- `C=6`: observed 0.1667 versus pooled 0.4167.

This is a calibration of the intended anisotropic mechanism, not independent
evidence that real transformer graphs share it: the synthetic checkpoint and
context distributions were deliberately separated.

## Knowledge card

### Observed

- The implementation exactly separates disconnected, coherent, and frustrated
  phases on rectangular synthetic graphs.
- Exact small-graph syndrome, gauge-invariance, cluster, and coboundary-distance
  tests pass.
- The pilot contains all three phases and exposes a finite-size connectivity
  shift.
- Every work unit retains graph, seed, phase, curve, distance, and null-arm
  receipts.
- A second pilot replay produced the identical run-receipt SHA-256.

### Inferred

Within this synthetic family, connectivity is controlled by the lower-
retention context edges, while a nonzero rank-one gauge class divides connected
graphs into globally coherent and path-dependent regimes.  Connectivity and
cycle emergence are independent thresholds, not ordered stages.

### Not supported

- No claim about Qwen, VPD, causal edits, recursive improvement, or RSI.
- No ALife claim that selection drives populations toward the coherent-phase
  boundary.
- No claim that the planted retention distributions are measured transformer
  distributions.
- No new attestation level or authorization.

### Robustness and confounds

- Exact tests cover a triangle, square cut, theta graph, gauge reframing, an
  explicit threshold counterexample, and invalid inputs.
- The pilot has only four independent graph replicas per finite size.
- Frustrated-cluster decomposition depends on the selected cycle basis, even
  though `w1`, phase, and exact coboundary distance are gauge invariant.
- The full `C=16,32` configurations use bounds when exact coset enumeration
  exceeds its registered dimension guard; they were not run.
- A replay overwrote the wrapper's per-attempt summary but not the append-only
  event log or the write-once scientific run artifacts.  The scientific
  run-receipt remained byte-identical.

## Reproducibility

- Frozen implementation commit: `28ad382f06f3cb076924fd4992cb37f3aff11508`
- Protocol SHA-256: `56a28cf14da64662141d6c3fb1000e7ddbbc3ea8ada80141b0264d0fdf0386a6`
- Smoke work units: 24
- Pilot work units: 384
- Pilot run-receipt SHA-256: `1eaa88d9d60b8d7595804c36f7dbf64e8339244966d779c15a8adead8b2efee2`
- Byte-identical replay: passed
- Pilot first execution: approximately 45 seconds from append-only wrapper
  events
- Replay peak RAM: 178.262 MB under 2,048 MB
- Replay peak I/O: 16.076 MB/s under 50 MB/s
- GPU: 0 MB
- Cleanup: passed
- Full repository before execution: 160 tests passed

## Next experiment

The highest-information next step is Stage A under its own retrospective
protocol: apply the exact curve to the four frozen Qwen0.8B dense-local graph
receipts and test the already-stated descriptive prediction that context edges
set `tau_conn` while checkpoint edges remain noncritical.  Stage B remains the
first confirmatory transformer test and requires fresh context-restricted
geometry.  The optional ALife extension must remain separate and use task
performance for selection while reserving phase location and `w1` as evidence
metrics.
