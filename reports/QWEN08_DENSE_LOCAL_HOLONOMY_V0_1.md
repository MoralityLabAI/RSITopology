# Qwen0.8B Dense-Local Holonomy Result v0.1

## Decision

The denser local capture partially recovered a cross-checkpoint lineage object,
but it did **not** establish noise-nontrivial holonomy and does **not** open the
causal outer stage.

Only `graph_reachability` produced a common supported rank at every node of a
site-by-family grid.  The common rank was one at all four registered layers.
The other twelve site-by-family grids had no common supported identity rank.

At rank one, an orientation-preserving loop has holonomy in `SO(1) = {1}`.
Consequently, the eight admitted orientation-preserving loops have no
continuous canonical rotation angle to estimate: every receipt has
`det(H) = +1`, identity loss zero, and an empty canonical-angle spectrum.  This
is a mathematical rank-one boundary, not evidence that higher-rank transformer
geometry is flat.

The rank-one object nevertheless has a nontrivial discrete topological test.
For a real line bundle the full structure group is `O(1) = {+1, -1}`, and the
sign accumulated around a loop evaluates the first Stiefel--Whitney class
`w_1` on that cycle.  The admitted elementary loops form cycle bases for the
lineage graphs at layers 11, 19, and 23.  Every generator has positive sign.
Therefore `w_1 = 0` on each measured cycle space, and the certified
graph-reachability line bundle is orientable and trivializable over each of
those admitted graphs.  This statement is scoped to the measured graphs; it
does not imply a globally trivial bundle over unmeasured contexts or model
states.

The registered stop state is therefore:

> `lineage_only_no_noise_valid_holonomy`

The aggregate gate also fails independently because support appears in only one
behavior family, below the registered minimum of two.

## Frozen inputs

- Scientific protocol SHA-256:
  `964d979372dac37b65746c9018d1629b9bb3223a045c26eb82d3967c189d1518`
- Dense prompt manifest SHA-256:
  `b7d2e98e90158b1a5f67981f5ec40261c672c64739263927dc5322861cacbd39`
- Analysis registration SHA-256:
  `c7db76598c8b31f507fd4a1e6786f1b74362ed3cdcbdafef7e679b6a011c3690`
- Base capture-index SHA-256:
  `7b887ab7c40f8731f3cbb40243161f46c4925b029b0ef3ea7cfca89c7af789da`
- Naive capture-index SHA-256:
  `d2777ef88aa2113108fd9f6af9fd1fab23b22815116e418c1d6a26540d3fdf5e`

The manifest contains 4,608 distinct prompt bytes.  Its separation receipt
reports zero byte-identical overlap with both the original geometry manifest
and the sealed causal-outer manifest.  Opaque label-agnostic nonces distinguish
replicas from task generators with small finite prompt support; the nonce rule
is recorded in the manifest.

## Capture and resource receipts

Both states were captured sequentially in four-bit inference mode, with no
generation, gradients, or weight mutation.  Each state produced 32 chunks;
each chunk has 576 rows by 1,024 activation dimensions.

| State | Model elapsed | Peak CUDA allocation | Job peak RAM | Job peak I/O | Cleanup |
|---|---:|---:|---:|---:|---|
| base | 1,207.85 s | 1,454.90 MB | 5,527.09 MB | 69.73 MB/s | passed |
| naive QLoRA | 1,671.00 s | 1,409.73 MB | 5,526.72 MB | 398.28 MB/s | passed |

The Windows Job Object enforced 6,144 MB RAM and 50% CPU.  I/O was monitored
fail-closed at 750 MB/s, the timeout was 3,600 seconds per state, and the
registered swap allowance was zero.  The wrapper cannot disable the Windows
pagefile per process; “zero swap” means no deliberate swap allocation and is
not a proof that Windows performed no paging.

The target-blind CPU analysis ran under a separate 4,096 MB / 50% CPU /
250 MB/s / 14,400 second authorization.  It completed in 494.75 seconds with
189.16 MB peak job RAM and cleanup passed.

## Rank recovery

Across 128 state-by-site-by-family-by-context nodes:

| Family | Supported-node profile | Median rank-1 point retention | Median rank-1 bootstrap lower 95 | Median permutation upper 95 | Median null margin |
|---|---|---:|---:|---:|---:|
| affine recurrence | 31 rank 0; 1 rank 2 | 0.3273 | 0.0025 | 0.3457 | -0.3396 |
| symbol transport | 32 rank 0 | 0.3449 | 0.0037 | 0.4246 | -0.4126 |
| grid rotation | 32 rank 0 | 0.7521 | 0.1900 | 0.4285 | -0.2380 |
| graph reachability | 28 rank 1; 4 rank 4 | 0.9250 | 0.6716 | 0.4653 | +0.2104 |

The graph uses the minimum supported rank over all eight state-by-context nodes
in a site-by-family cell.  Thus all four graph-reachability grids select rank
one even though four individual nodes support rank four.

## Lineage graph and bifiltration

| Layer | Common rank | Admitted edges / 10 | `beta_1` | Admitted loops / 3 | Result |
|---|---:|---:|---:|---:|---|
| 11 | 1 | 10 | 3 | 3 | structurally available, rank-one trivial |
| 15 | 1 | 4 | 0 | 0 | `holonomy_unavailable` |
| 19 | 1 | 9 | 2 | 2 | structurally available, rank-one trivial |
| 23 | 1 | 10 | 3 | 3 | structurally available, rank-one trivial |

Checkpoint edges are extremely clean (minimum retention 0.9958 across the four
layers).  Context edges are the limiting axis: their layerwise minimum
retentions are 0.9012, 0.8937, 0.8974, and 0.9056.  This reproduces the earlier
localization: context variation, not the engineering checkpoint edge, controls
lineage connectivity.

The sample-support intervention did what it was supposed to do.  Moving from
two to sixteen replicas recovered a repeatable line bundle where the earlier
local object collapsed completely.  Four individual graph-reachability nodes
even supported rank four.  The common-grid rule reduced every cell to rank one
because the higher ranks did not survive *all* context shards.  Thus another
replica increase is not the evidenced next move.  A future, separately
registered construction should test context-conditioned patches and their
overlaps, rather than assuming one global higher-rank fiber.

## Certification and controls

- Instrument calibration passed all registered ranks.
- Gauge preflight passed 384 loop reframings with zero determinant-decision
  mismatches and zero canonical-angle error.
- 14 node certificates attained `lineage_certified`.
- 18 remained `engineering_evidence`.
- 0 attained `holonomy_clean`.
- Corotation was not established: only one family supplied equal-rank grid
  edges, so the registered cross-family comparison had zero eligible pairs.
- Every sectioning grid returned no admissible multi-patch edit section.

A separately provenance-bound natural-feature run previously reported 91.67%
orientation-reversing loops.  It is not pooled into this dense-run inference,
but it supplies a useful contrast for future synthesis: the object that passes
the present lineage gate is an orientable line bundle on its measured cycle
spaces, whereas the uncertified natural-feature object was dominated by sign
reversals.  The comparison must retain separate receipts because the objects,
models, and admission rules differ.

## Interpretation

The earlier two-replica local collapse was partly a sample-support problem:
with 16 replicas per subcondition per half and context, one behavior family now
forms a repeatable local line bundle across all four layers.  But the denser run
does not recover the higher-rank local fibers required for continuous
non-Abelian holonomy or high-dimensional transported edit coordinates.

This narrows the real-model result to:

> A rank-one graph-reachability lineage object exists on the frozen
> Qwen3.5-0.8B base-to-naive grid.  Its checkpoint edges are clean and three of
> four layer grids contain cycles.  Its measured first Stiefel--Whitney class
> vanishes, so it is orientable and trivializable on those admitted graphs; but
> its orientation-preserving holonomy is algebraically trivial and cannot
> support the proposed continuous signed-edit risk signal.

Equally importantly, the decision machinery behaved correctly under a mixed
result: it retained the rank-one finding, rejected the continuous-holonomy
claim, and left every downstream authorization closed.  That separation is
what makes the positive and negative parts independently reusable.

The result does not justify a Qwen1.7B confirmation, causal activation edits,
VPD weight-edit authorization, compactification, recursive improvement, or RSI
claims under the frozen protocol.

## Canonical result artifacts

- Analysis result SHA-256:
  `6a153e34dfc1092d7ca21719d56376678cf7d11906a688077d8bba1f97d1a6c7`
- Pair capture-index SHA-256:
  `18d3d8d5fcb85cfdcfdcbb6f5383181ca8c3a3e38439ebcbe01866735c14f873`
- Release manifest SHA-256:
  `ec0e4614405019ab5a38465485d7a2881d32c82b236e3561c2e69a99c5d44b3f`
- Release manifest payload SHA-256:
  `b226ab65662f0be4d5809ea7b7d52eebfabec888f5418ae2125d593576f45d3b`

The full activation and analysis bundle remains under
`D:\Research_Engine\runs\qwen08_dense_local_*`.  The repository carries this
report, the compact receipt, frozen protocols, prompt manifest, and replay code;
it does not duplicate the large activation arrays.
