# ASMP-9 v0.21 public summary: the irreducible block already contains a #P-hard value problem

Version v0.20 reduced exact finite comparison allocation to independent
vertex-biconnected blocks but left the computation inside one
overlapping-cycle block unclassified.  Version v0.21 closes that gap at one
sharp boundary.

## Result

At response interior `epsilon=1/2` and total budget equal to the number of
edges, positive counts force exactly one comparison per edge.  The residual
object is then a uniformly random total orientation.  On a biconnected block,
ASMP quotient liveness is exactly total cyclicity:

```text
exact availability = T_G(0,2) / 2^|E|.
```

The numerator is the classical number of totally cyclic orientations.  By
the Las Vergnas interpretation and the Jaeger-Vertigan-Welsh Tutte
dichotomy, computing it is #P-complete under polynomial-time Turing
reductions.  Exact rational value computation is therefore #P-hard, including
when accessed through an oracle restricted to biconnected blocks.

The distinction matters: **value computation is hard here, but optimizer
search is not**.  The allocation at this boundary is unique.

## Registered verification

All 10 gates passed on four fresh biconnected graphs.  Deletion-contraction,
exhaustive orientation enumeration, and the inherited ASMP predicate agreed
exactly:

| Graph | Totally cyclic orientations | Availability |
|---|---:|---:|
| wheel on 7 vertices | 726 | `363/2048` |
| Petersen | 1,920 | `15/256` |
| pentagonal prism | 1,800 | `225/4096` |
| subdivided `K4` | 24 | `3/64` |

An independent verifier used the spanning-subgraph expansion rather than
importing the implementation and passed 11/11 checks.

The bridge control was load-bearing.  Adding a leaf bridge made
`T_G(0,2)=0`, as classical total cyclicity requires, while the ASMP
bridge-quotiented availability correctly remained `363/2048`.  The theorem
is about the local biconnected block, not an arbitrary graph with ignored
bridges.

## Attribution and boundary

The orientation interpretation, Tutte complexity dichotomy, and
biconnected-product mathematics are classical prior art.  The contribution is
the exact translation from the frozen ASMP access model and the explicit
localization of its value-computation barrier.

This does not solve the exact design problem above the count floor,
arbitrary-response weighting, approximation, adaptive access, behavioral
misspecification, general IRL, or ASMP-9.

Full result: [RESULT_v0_21.md](artifacts_v0_21/RESULT_v0_21.md)  
Protocol: [PROTOCOL_v0_21.md](PROTOCOL_v0_21.md)  
Prior-art gate: [PRIOR_ART_GATE_v0_21.md](PRIOR_ART_GATE_v0_21.md)

