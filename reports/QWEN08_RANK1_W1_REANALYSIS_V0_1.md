# Qwen0.8B rank-one sign holonomy (`w1`) reanalysis

## Status

The CPU-only reanalysis completed under the registered Windows Job Object on
2026-07-16.  It is a **retrospective derived analysis**, not a new confirmatory
preregistration: the earlier dense-local run had already revealed that every
admitted elementary validation loop had positive determinant, so the signs of
contiguous composite loops were algebraically implied before this protocol was
frozen.

That limitation is load-bearing.  The run validates the discrete instrument,
its resampling stability, its arithmetic-precision stability, and the exact
loop-space bookkeeping.  It does not turn a known elementary result into fresh
out-of-sample evidence.

## Mathematical object

At rank one, each orthogonal edge transport lies in

`O(1) = {+1, -1}`.

Changing a node's local frame flips the signs on all incident edges, adding a
coboundary to the edge-sign cochain.  The product around a closed loop is
unchanged.  The resulting loop character is the first Stiefel--Whitney class

`w1 in H^1(G; Z/2)`.

For a real line bundle over a graph, this class is the complete isomorphism
invariant.  On an admitted graph, all cycle-basis products equal `+1` exactly
when `w1 = 0`, equivalently when the line bundle is orientable and
trivializable.

## Result

| Site | `beta1` | Construction signs | Validation signs | Classification |
|---|---:|---|---|---|
| `model.layers.11` | 3 | `[+1,+1,+1]` | `[+1,+1,+1]` | `w1 = 0` |
| `model.layers.19` | 2 | `[+1,+1]` | `[+1,+1]` | `w1 = 0` |
| `model.layers.23` | 3 | `[+1,+1,+1]` | `[+1,+1,+1]` | `w1 = 0` |

All admitted rank-one dense-local graphs are therefore orientable and
trivializable on their measured graph domains.  This is stronger and more
precise than saying that their continuous holonomy angle is zero: `SO(1)` is
trivial, and the nontrivial rank-one invariant is the `O(1)` sign class.

### Derived composite diagnostics

The protocol registered seven contiguous composite constraints:

- three at layer 11;
- one at layer 19; and
- three at layer 23.

Their combined constraint matrix has GF(2) rank 7.  Every construction-half
generator product matched its geometry-validation composite sign.  Across 128
independent within-class bootstraps, every composite had:

- 128/128 construction-generator stability;
- 128/128 validation-loop stability; and
- 128/128 construction-to-validation prediction agreement.

The exact two-sided Clopper--Pearson lower bound was 0.9716 in each case.  The
matched label-permutation prediction agreements ranged from 54/128 to 75/128;
their largest 95% upper bound was 0.6723.  Every registered diagnostic margin
therefore passed.

If the validation cohomology classes were uniform, the probability of
satisfying seven independent GF(2) constraints would be

`2^(-7) = 1/128 = 0.0078125`.

This value is reported descriptively, not as a confirmatory p-value, because
the validation elementary signs had already been revealed.

### Precision boundary

Every point loop sign agreed between float32 and float64 analysis arithmetic.
This does **not** establish runtime-precision stability: both paths analyze the
same arrays from one 4-bit model runtime.  A separately captured full-precision
model path remains necessary for that claim.

## Corrected comparator provenance

The 91.67% orientation-reversal figure came from a separate Qwen3-1.7B **VPD
weight-component identity construction**, not a natural-feature line bundle.
Its archived predictor table contains 192 evaluations:

- 176 negative determinant signs in split A;
- 176 negative determinant signs in split B;
- 192/192 split-sign agreement;
- 176 stable orientation-reversing and 16 stable orientation-preserving
  evaluations.

This supports retrospective determinant-sign stability for that construction.
It does not support a complete `w1` classification or a composite-loop
prediction without the comparator's bound edge cocycle and cycle basis.  The
two objects are not pooled.

## Resource and integrity receipt

- Frozen implementation commit: `713a406bab9ad09acec153971c6bf543f756abf4`
- Protocol SHA-256: `3bcbb8814f4d50094abc640b2fdb7363814277fa1446779327f6a288328803b2`
- Result SHA-256: `3f80dbe78c48396d106647ee8423122b6f8fd89350aa2cd8d2933eb2da232cad`
- Job status: `completed`, exit code 0
- Elapsed: 98.277 seconds
- Peak RAM: 180.012 MB under a 4,096 MB hard cap
- Peak I/O: 32.064 MB/s under a 250 MB/s cap
- Peak GPU: 0 MB
- Registered swap: 0 bytes
- Cleanup: passed
- Repository tests before execution: 149 passed

## Claim boundary and next test

This result establishes a stable, gauge-invariant `w1 = 0` description on the
already-admitted Qwen0.8B rank-one dense-local graphs.  It does not establish
semantic identity, causal edit value, VPD efficacy, capability preservation,
compactification, recursive improvement, or RSI, and it does not reopen the
closed causal, Qwen1.7B, or VPD stages.

A genuinely confirmatory sign-holonomy prediction now needs fresh held-out
geometry.  The highest-value capture is not more replicas on the same global
grid; it is the separately registered Stage B proposal: context-restricted
sampling around the four locally rank-4 graph-reachability nodes, with one
full-precision layer control.  Until that exists, the correct headline remains
the rank-one classification and the localized context bottleneck.
