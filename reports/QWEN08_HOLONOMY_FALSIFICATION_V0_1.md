# Qwen3.5-0.8B holonomy falsification result

## Outcome

The current local identity object failed honestly, while a pooled global
version of the same object was recovered.

At each model state, layer, behavior family, and context shard, the registered
object was the cross-fitted top-r eigenspace of between-class scatter over nine
frozen subconditions.  A rank passed only when

```text
q05(bootstrap worst-direction retention)
  - q95(label-permutation worst-direction retention) > 0.02.
```

With two prompts per subcondition, per half, per local context, none of 512
unique nodes supported any rank.  Consequently all three base-to-adapter grids
stopped before graph construction:

| State pair | Unsupported site x family grids | Graphs | Loops | Certificates |
|---|---:|---:|---:|---:|
| base vs naive | 16/16 | 0 | 0 | 0 |
| base vs shuffled VPD | 16/16 | 0 | 0 | 0 |
| base vs VPD | 16/16 | 0 | 0 | 0 |

This is `holonomy_unavailable_no_supported_identity_rank`, not zero measured
holonomy.  No loop angle exists because the lineage substrate did not pass.

The instrument was not dead: its planted matched-label calibration passed all
ranks in every pair analysis.  At rank 1 the median point retention was 0.808,
but the median bootstrap lower bound was only 0.203, below a random-label upper
bound of 0.783.  The best margin anywhere in the 512-node, rank-1-through-8
universe was -0.0064 against a required +0.02.  The failure is uncertainty in
local frame estimation, not a marginal threshold call.

## Support-recovery diagnostic

A separately frozen, target-blind diagnostic pooled context shards while
retaining the same labels, halves, rank sweep, bootstrap, and permutation null.
Pooled objects were prohibited from receiving lineage or holonomy
certification.

| Contexts pooled | Prompts/subcondition/half | Passing objects |
|---:|---:|---:|
| 2 | 4 | 65/512 (12.7%) |
| 4 | 8 | 373/512 (72.9%) |
| 8 | 16 | 60/64 (93.8%) |

In the full pool, the common supported cells numbered 14/16 for base vs naive
and 15/16 for each of the shuffled-VPD and VPD pairs.  Every pair covered all
four layers and all four behavior families, with common ranks from 1 through
8.  The four state-specific misses were confined to `affine_recurrence` at
L19/L23 and were near the gate boundary.

The warranted conclusion is therefore:

> Qwen3.5-0.8B contains a recoverable global between-class behavior-family
> superstructure on these prompts and sites, but two samples per class and
> local context do not identify reusable local coordinates.

Pooling contexts mixes increased sample count with broader context support, so
the curve does not prove that the same number of within-context replicas will
recover the local object.  It does justify one denser local falsification run.

## Next registered experiment

The next run should use Qwen3.5-0.8B base and the provenance-limited naive
adapter strictly as a checkpoint axis, with:

- four local context shards;
- sixteen prompt replicas per subcondition, half, and shard;
- the same four behavior families, nine subconditions, four residual-block
  sites, ranks 1-8, and 128-replicate label-permutation gate;
- exact construction/geometry-validation separation and zero prompt-byte
  overlap with the causal outer split;
- graph construction only after a common rank exists at every node of a cell;
- `beta_1 = |E_tau| - |V| + c(G_tau)` before loop admission;
- construction/validation determinant agreement and a prompt-resample noise
  null before any loop is called nontrivial.

For a two-state by four-context grid, a fully lineage-connected cell has three
elementary rectangles and cycle rank three.  If the denser local run still has
no common rank, the local between-class object is rejected at development
scale.  If it has common ranks but `beta_1 = 0`, holonomy remains unavailable.
If loops exist but do not exceed their noise null, the correct result is
lineage-only geometry.  Only noise-valid loops justify the already frozen
causal path-displacement outer test.  Qwen3-1.7B remains confirmatory and should
not run until this development gate passes.

## Provenance and limits

Four hard-capped, sequential model-state captures produced 256 validated NPZ
chunks.  All source-index hashes, prompt orders, array shapes, finiteness
checks, wrapper query-backs, and cleanup receipts passed.  The three pair
analyses and pooled diagnostic ran CPU-only with CUDA disabled and BLAS thread
limits.  Canonical hashes and decisions are recorded in
`artifacts/qwen08_holonomy_geometry_v0_1/result_receipt.json`.

The adapters came from an eight-row engineering smoke run.  Nothing here
supports a VPD-versus-shuffled efficacy claim, a causal edit claim, capability
preservation, compactification, recursive improvement, or RSI.
