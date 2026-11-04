# Qwen0.8B dense-local percolation reanalysis

## Status

This is a retrospective exact reanalysis of already-revealed edge and loop
receipts.  The protocol was frozen before the curve computation, but the source
geometry was not fresh; the result remains `engineering_evidence` and does not
reopen any causal, Qwen1.7B, or VPD stage.

Both pre-stated descriptive predictions passed.

## Exact critical floors

| Layer | `tau_conn` | critical class | `tau_cycle` | `tau_loop` | `beta1` at 0.9 | `beta1` at 0 |
|---|---:|---|---:|---:|---:|---:|
| L11 | 0.903603 | context | 0.929846 | 0.929846 | 3 | 3 |
| L15 | 0.894128 | context | 0.897892 | 0.897892 | 0 | 3 |
| L19 | 0.901281 | context | 0.923886 | 0.923886 | 2 | 3 |
| L23 | 0.911987 | context | 0.918675 | 0.918675 | 3 | 3 |

Every connectivity-critical edge was a within-state adjacent-context edge.
No checkpoint edge was critical.  The checkpoint retention ranges were:

- L11: 0.998539–0.998707;
- L15: 0.997880–0.998221;
- L19: 0.996889–0.997747; and
- L23: 0.995850–0.996799.

The context ranges were much lower, spanning 0.893669–0.931290 over the four
layers.  This localizes the limiting axis to context transport rather than
checkpoint transport.

## Layer 15

Layer 15's earlier `holonomy_unavailable` status is precisely explained by the
frozen floor:

- at `tau=0.9`, `beta1=0`;
- `tau_cycle=0.8978924981`; and
- at floor zero, `beta1=3`.

The graph does contain a cycle space.  Its context edges simply fall below the
registered lineage floor before any cycle survives.  This is a threshold
effect, not missing full-graph topology.

## Threshold ordering

All four layers have `tau_cycle > tau_conn`.  Thus a cycle appears within one
component before the complete registered node universe becomes connected.
This real-receipt reanalysis independently validates the correction made while
implementing the synthetic harness: only `tau_loop <= tau_cycle` is a theorem;
there is no universal order between cycle emergence and global connectivity.

## Resource receipt

- Frozen implementation commit: `6bdf40a2d35308be8a3b1b86d4e331dcaec0a83e`
- Protocol SHA-256: `6c12dd2445e81bd7026ee75ec578bfff7e7d0272c6fea991daa1fcf6dcb9d6f1`
- Result SHA-256: `e58f8a488812043c88c6a08fdfd5551fc723844bbe60d09b5fb9311aa075e797`
- Elapsed: 9.435 seconds
- Peak RAM: 79.527 MB under a 1,024 MB cap
- Peak I/O: 17.13 MB/s under a 20 MB/s cap
- CPU: 8.016% under a 25% cap
- GPU: 0 MB
- Swap: 0 bytes
- Cleanup: passed

## Claim boundary

This result establishes exact threshold locations and edge-class criticality
for the frozen Qwen0.8B engineering graph.  It does not establish semantic
identity, a fresh `w1` result, causal edit value, VPD efficacy, capability
preservation, compactification, recursive improvement, or RSI.  Stage B—the
fresh context-restricted capture—remains the first confirmatory transformer
test.
