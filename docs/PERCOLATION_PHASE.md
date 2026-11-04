# Lineage and rank-one gauge percolation

## Scope

This package maps finite synthetic transport graphs over a lineage threshold
`tau` and independent rank-one sign-flip rate `q`.  It is model-only
calibration and retrospective-descriptive machinery.  It adds no attestation
level and authorizes no causal stage, edit, VPD reopening, model generation, or
weight mutation.

## Mathematical object

`build_lineage_holonomy_bifiltration` evaluates one point of an inhomogeneous
bond-percolation filtration.  `lineage_percolation_curve` sweeps every distinct
edge retention plus 0 and 1, delegating every admission decision back to that
existing function.  The resulting finite step curve reports components,
largest-component fraction, cycle rank, and registered-loop survival.

The exact critical floors are:

- `tau_conn`: largest floor where the complete registered node set is
  connected;
- `tau_cycle`: largest floor where `beta_1 > 0`;
- `tau_loop`: largest floor where a registered loop is admitted.

Registered-loop admission implies a cycle, so `tau_loop <= tau_cycle`.  There
is no general ordering between `tau_cycle` and `tau_conn`: a cycle can close in
one component before the full node universe becomes connected.  Tests include
that counterexample explicitly.

At rank one, edge transports lie in `O(1)={+1,-1}`.  Node-frame flips change
the edge-sign cochain by a coboundary while preserving every loop product.  A
deterministic fundamental cycle basis therefore yields the gauge-invariant
syndrome representing `w1 in H^1(G;Z/2)`.

The phase label at one `(tau,q)` point is:

- `disconnected`: more than one connected component;
- `coherent`: connected with `w1=0`;
- `frustrated`: connected with `w1 != 0`.

Frustrated basis cycles are clustered by shared admitted edges.  Coboundary
distance is the minimum number of edge-sign corrections required to make all
cycles positive.  The implementation enumerates the affine GF(2) kernel coset
when its dimension is at most 20.  Larger graphs receive an explicit lower and
upper bound, never a fabricated exact value.

## API

The public API in `rsi_topology/percolation.py` provides:

- `lineage_percolation_curve`
- `sign_syndrome`
- `frustrated_clusters`
- `coboundary_distance`
- `fundamental_cycle_basis`
- `gauge_transform_edge_signs`
- `percolation_phase_point`
- `retention_permutation_nulls`
- `sign_noise_ensemble`

All returned dataclasses expose `to_dict()` receipts.  Pooled and within-edge-
class retention permutations are named separately and never silently mixed.

## Running

Focused mathematical tests:

```powershell
python -m pytest tests/test_percolation.py -q
```

Smoke configuration:

```powershell
python experiments/07_percolation_phase.py `
  --config configs/smoke/07_percolation_phase.yaml `
  --output-root D:/Research_Engine/runs/confinement_percolation `
  --workers 1
```

Pilot configuration:

```powershell
python experiments/07_percolation_phase.py `
  --config configs/pilot/07_percolation_phase.yaml `
  --output-root D:/Research_Engine/runs/confinement_percolation `
  --workers 1
```

The full configuration is a specification only and must not be launched
without a separate bounded-run authorization.  Executed smoke and pilot runs
must use the registered Windows Job Object limits: 2 GB RAM, 50% CPU, 50 MB/s
I/O, zero swap, one BLAS thread, and no GPU.

## Follow-ups

Stage A applies the curve retrospectively to frozen Qwen0.8B receipts under a
separate protocol.  Stage B is the first confirmatory sign-percolation test and
requires fresh context-restricted geometry.  Stage C is an optional ALife
experiment and requires its own model-only knowledge contract: task performance
is the selection metric, while phase location and `w1` are held-out evidence
metrics so the topology result cannot be selected into existence.
