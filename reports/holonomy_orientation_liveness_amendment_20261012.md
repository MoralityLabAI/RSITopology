# Orientation-reversal liveness at every rank, and a proposed amendment to the dense-local holonomy protocol

Date: 2026-10-12. Proposal, not a registration. Companion files:
`protocols/qwen08_dense_local_holonomy_v0_1_1_amendment.json` and
`scripts/holonomy_orientation_liveness.py`.

## 1. The inequality

Let `U_0, …, U_m = U_0` be a cycle of `r`-dimensional subspaces with the
polar (shortest-geodesic) transports used throughout this repository, and
let `H in O(r)` be the loop holonomy. Then `det H` is the holonomy of the
induced line bundle `Lambda^r U`. For adjacent subspaces with orthonormal
bases `U, V` and principal angles `alpha_1, …, alpha_r`,

```text
|det(U^T V)| = prod_i cos(alpha_i),
```

so the angle between the lines `Lambda^r U` and `Lambda^r V` is
`theta = arccos(prod_i cos alpha_i)`. Lift the cycle of lines to the unit
sphere of `Lambda^r R^n` by choosing successive unit representatives with
non-negative inner product; `det H = -1` means the lift ends at the antipode
of its start, whose spherical distance is `pi`, while the lift has length
`sum_e theta_e`. Hence

```text
det H = -1   implies   sum_e arccos( prod_i cos alpha_i^(e) ) >= pi.
```

At `r = 1` this is Theorem 1 of `reports/QWEN08_PRECISION_GEOMETRY_PAPER_V0_1.md`.

Under a lineage floor `tau` on worst-direction retention, every principal
angle has `cos alpha_i >= sqrt(tau)`, so each edge contributes at most
`theta_r(tau) = arccos(tau^(r/2))`, and a cycle of length `L` can reverse
orientation only if `L * theta_r(tau) >= pi`.

## 2. The table at the parent protocol's floor

`protocols/qwen08_dense_local_holonomy_v0_1.json` (registered, not run) uses
lineage floor 0.9, 2×4 cells with 8 nodes, 10 edges, three elementary
rectangles (4 edges) and cycle rank 3; its longest simple cycle has 8 edges.

| rank | max line angle per edge | minimal live cycle length | 4-edge rectangle | 8-edge cycle |
|---:|---:|---:|---|---|
| 1 | 18.43° | 10 | forced +1 | forced +1 |
| 2 | 25.84° | 7 | forced +1 | live |
| 3 | 31.37° | 6 | forced +1 | live |
| 4 | 35.90° | 6 | forced +1 | live |
| 5 | 39.79° | 5 | forced +1 | live |
| 6 | 43.20° | 5 | forced +1 | live |
| 7 | 46.24° | 4 | live | live |
| 8 | 49.00° | 4 | live | live |

At floor 0.95 the rectangles are dead at every rank up to 8 and the 8-edge
cycle is dead up to rank 3; at floor 0.5 everything is live from length 3 or
4. The script prints these.

## 3. Consequence for the parent protocol

The parent treats `det H = -1` as "categorical denial; suppress canonical
angles" at every rank, and its aggregate gate opens the causal outer stage
only for "orientation-preserving" loops. Under its own floor, orientation
preservation is forced on every elementary rectangle unless the common rank
is 7 or 8, and on every cycle at rank 1. A run that reports "all admitted
loops orientation-preserving" at common rank 6 or below would be reporting a
tautology; the Qwen0.8B precision paper already found exactly this at rank 1
and converted it into a methodological point. The amendment makes the
conversion part of the protocol rather than a post-hoc rescue:

1. compute each admitted cycle's angle budget `B` from measured principal
   angles;
2. report `det H` only for cycles with `B >= 180°`; mark the others
   `orientation_forced_positive`;
3. carry `B` and the live/forced flag next to every canonical-angle report;
4. allow aggregate orientation statements to count live cycles only, and if
   none exist, say `orientation_channel_dead_at_this_floor`.

No gate, floor, cap, or stop state changes. The graded canonical-angle
channel is untouched; its liveness is a separate question governed by the
parent's noise null.

## 4. A design remark

The inequality exposes a tension in rank-one and low-rank holonomy
diagnostics: the orientation channel becomes live only when lineage is
already poor (small `tau`) or cycles are long, so in the regime where
identity is well preserved it carries no information beyond lineage. For the
dense-local design this argues for reporting at the highest common rank that
passes rather than at rank one, and for including at least one long cycle
(the 8-edge cycle) in the loop registry, since at floor 0.9 it is the only
cycle live below rank 7.
