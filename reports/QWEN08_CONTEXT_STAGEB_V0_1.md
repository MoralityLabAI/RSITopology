# Qwen0.8B context-restricted sign-percolation Stage B

## Decision

The fresh four-bit main gate passed at layer 23, while the registered
cross-precision comparison was unavailable:

> `main_result_only_precision_stability_not_established`

This is the first out-of-sample `w1` result in the program in the narrow sense
registered by the protocol: the sites, behavior family, and old context
neighborhoods were selected from the revealed dense-local result, but all
2,304 prompt bytes and every measured activation were fresh.  It is not an
out-of-sample test of the site-selection procedure.

## Main four-bit result

Layer 23 recovered a common rank-one graph across base and the naive
engineering checkpoint.  At the frozen lineage floor `tau=0.9`, all ten
edges were admitted, the eight nodes were connected, and `beta_1=3`.  The
exact gauge-percolation classifier returned the coherent phase:

- the three fundamental-cycle syndrome entries were `(0, 0, 0)`;
- the exact GF(2) coboundary distance was zero;
- every registered elementary generator had `det(H)=+1`;
- construction and validation determinant decisions agreed on every loop;
- zero of 256 bootstrap resamples reversed orientation for each loop; and
- each one-sided 95% Clopper--Pearson upper bound was `0.0116339`, below the
  frozen `0.05` ceiling.

The exact critical floors were:

| Site | Common rank | `tau_conn` | `tau_cycle` | `tau_loop` | Phase at 0.9 |
|---|---:|---:|---:|---:|---|
| `model.layers.23` | 1 | 0.912870 | 0.959685 | 0.959685 | coherent |

As in the retrospective result, the cycle threshold exceeds the global
connectivity threshold: cycles appear in a high-retention disconnected
component before the last context bridge joins the node universe.

Layer 19 did not form a common four-bit graph.  The base runtime supported
rank one across all four fresh contexts (one node supported rank four), but
the naive runtime had one rank-zero context.  The cross-runtime common rank
therefore collapsed to zero under the frozen min-over-grid rule.  This is not
pooled with the successful layer-23 result or repaired post hoc.

## Unquantized float16 control

The layer-19 float16 control recovered a common rank-one graph.  It was also
connected and coherent at `tau=0.9`, with `beta_1=3`, three positive generator
signs, and zero bootstrap reversals.  Its critical floors were
`tau_conn=0.942612` and `tau_cycle=tau_loop=0.971052`.

The registered precision gate nevertheless returned `unavailable`, not
`pass`: layer 19 had no common four-bit graph, so there were no loop IDs
admitted in both runtimes to compare.  The defensible finding is therefore
precision sensitivity of support recovery at layer 19, plus an independently
coherent main graph at layer 23.  No precision-stable claim is made.

Float16 here means unquantized float16 model weights with activations stored
as float32.  It is not a float32 model run.

## Capture and resource receipts

All four model-bearing runs used the validated Windows Job Object wrapper,
one process per state, a 6,144 MB commit cap, 50% CPU cap, monitored I/O,
registered zero deliberate swap, one shard-half checkpoint unit, and
PID-scoped cleanup.

| Capture | Chunks | Elapsed | Peak RAM | Peak I/O | Cleanup |
|---|---:|---:|---:|---:|---|
| four-bit base, L19/L23 | 16 | 1,114.1 s | 5,546.6 MB | 27.2 MB/s | passed |
| four-bit naive, L19/L23 | 16 | 758.6 s | 5,611.9 MB | 97.1 MB/s | passed |
| float16 base, L19 | 8 | 437.7 s | 5,396.0 MB | 512.2 MB/s | passed |
| float16 naive, L19 | 8 | 425.0 s | 5,510.3 MB | 651.5 MB/s | passed |

The target-blind CPU analysis used a 4,096 MB / 50% CPU / 250 MB/s / zero-GPU
authorization.  The initial run completed in 79.9 seconds with 181.1 MB peak
RAM.  A second authorized replay completed in 78.2 seconds and reproduced the
result byte-for-byte.  The result SHA-256 before and after replay was
`01d3a29f0916a1df044a1b48fd540c8d11cba1bc3f2ee47c35571b54c8ab22ba`.

## Interpretation

The experiment supports a limited but real mathematical statement:

> On a fresh context-restricted Qwen0.8B graph at layer 23, the admitted
> rank-one determinant line bundle is connected, orientable, and
> trivializable over its measured cycle basis.  Its exact `w1` syndrome is
> zero out of sample under the registered sign-stability margin.

It does not recover a higher-rank non-Abelian bundle.  It does not show that
continuous holonomy predicts a causal edit, and it does not authorize VPD or
recursive-improvement work.  The precision result also blocks the stronger
claim that the selected identity geometry is stable between four-bit and
unquantized float16 runtimes at the same physical layer.

The most informative follow-up is no longer another global rank sweep.  It is
a precision-by-context support analysis: why the naive L19 shard-02 node is
rank zero in four-bit but rank one in float16, and whether that difference is
a smooth retention shift or a hard threshold crossing.  That should be a
separate protocol; this result must not be reopened by changing its rank or
floor.

## Claim boundary

This fresh development-model capture may establish context-restricted
lineage, an out-of-sample first Stiefel--Whitney sign result, and a `q=0`
percolation phase on the frozen base-to-naive grid.  It cannot establish
semantic identity, causal edit value, VPD efficacy, capability preservation,
compactification, recursive improvement, or RSI.

