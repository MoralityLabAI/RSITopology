# The Missing Phase of Bundle Lineage

## Result

Principal-angle lineage is not sufficient to certify that a signed monitor or
edit coordinate has one globally consistent identity across prompt and training
changes.  A matched synthetic control gives both flat and curved systems a
minimum edge worst-direction retention of `0.990033`.  The flat system returns a transported
monitor exactly to itself.  The curved system accumulates `-62.173 degrees` of
rotation and returns only `0.466809` signed alignment, even though its mean
edge chordal lineage (`0.994692`) is slightly better than the flat control
(`0.992571`).  Block energy remains one in both cases.

Because this control has rank two, `62.173 degrees` is the loop's sole
canonical rotation-plane angle and therefore both its mean and maximum angle.
For rank six, the registered summary is the sorted three-angle conjugacy class,
not one signed scalar and not the entries of the holonomy matrix.

This is a synthetic identifiability construction in `Gr(2, 4)`.  It is not
evidence that transformer monitors exhibit the effect.

## The discarded factor

For orthonormal rank-`r` frames `U_a` and `U_b`, the overlap has a polar/SVD
factorization

\[
U_b^\top U_a = Q_{b\leftarrow a} S_{ba}.
\]

The singular values in `S` determine the principal angles.  The existing
`subspace_lineage` statistic intentionally keeps those values and discards the
left/right singular vectors.  The orthogonal polar factor `Q` is nevertheless
load-bearing for signed coordinates: it is the closest norm-preserving map
from coordinates in `U_a` to coordinates in `U_b`.

Given a context-by-checkpoint plaquette, compose the transports around its
boundary:

\[
H_\square =
Q_{00\leftarrow 01}
Q_{01\leftarrow 11}
Q_{11\leftarrow 10}
Q_{10\leftarrow 00}.
\]

Changing the basis independently at each vertex conjugates `H_square` at the
base vertex.  Its trace and eigenphases are therefore gauge invariant.  The
registered scalar is

\[
\kappa_\square = 1 - \frac{1}{r}\operatorname{tr}(H_\square).
\]

For a uniformly random unit monitor coordinate `v`,
`E[v^T H_square v] = tr(H_square) / r`.  Thus `kappa_square` is exactly the
average signed-monitor identity loss after one closed transport loop.

For a smooth projector field `P(p,t)`, the infinitesimal object is the
curvature of the tautological Grassmann connection,

\[
F_{pt}=P[\partial_pP,\partial_tP]P,
\qquad
H_\square\approx\exp(F_{pt}\,\Delta p\,\Delta t).
\]

The unit test confirms the expected area law: doubling both sides of a small
plaquette multiplies its phase by approximately four.

The exact infinitesimal target is not the finite-grid regression slope. At the
registered origin,

\[
F_{st}=\begin{bmatrix}0&-1.49\\1.49&0\end{bmatrix},
\]

so the analytic maximum canonical rotation rate is `85.370711` degrees per
unit area. The registered finite grid fits `83.837782`; its `1.796%` relative
shortfall is expected finite-loop variation and is recorded as grid metadata
rather than treated as the invariant constant.

This extends the program's discriminating-control tower. Occupancy is a
vertex-level invariant defeated by the matched-spectrum lineage control.
Lineage is an edge-level invariant defeated here while worst-direction
retention is matched. Holonomy is the first loop-closure invariant.

## Matched construction

Let `J_ij` denote the skew generator rotating coordinate plane `(i,j)` and let
`U_0 = span(e_0,e_1)`.  Sample

\[
U(s,t)=\exp(sA+tB)U_0
\]

around a ten-by-ten square with step `0.1`, using

\[
A=J_{02}+0.7J_{13}.
\]

The flat control uses the commuting generator

\[
B_{flat}=0.7J_{02}-J_{13},
\]

while the curved condition uses

\[
B_{curved}=0.7J_{03}-J_{12}.
\]

| condition | commutator norm | min edge worst-direction retention | mean edge chordal lineage | loop phase | det(H) | signed return | energy return |
|---|---:|---:|---:|---:|---:|---:|---:|
| flat | 0.0000 | 0.990033 | 0.992571 | 0.000 deg | +1.000 | 1.000000 | 1.000000 |
| curved | 2.8914 | 0.990033 | 0.994692 | -62.173 deg | +1.000 | 0.466809 | 1.000000 |

The control isolates non-integrability rather than local damage.  Both systems
have the same worst edge retention, and the curved system has the higher mean.

## Orientation is a prior discrete gate

Holonomy lies in `O(r)`, not automatically `SO(r)`. Every v0.3 receipt reports
`det(H)`, an orientation component, and a mandatory reversal flag. If
`det(H) < 0`, canonical-angle fields are suppressed and their status becomes
`superseded_by_orientation_reversal`. A reflection is a categorical identity
break, not another point on the rotation-angle scale. Both planted conditions
have determinant `+1`; a dedicated test verifies the `-1` branch.

## Registered estimation-noise null

Estimated subspaces can generate spurious loop rotation even when the true
connection is flat. Independent edge errors accumulate like a random walk:
signed phase variance should scale with perimeter, while planted curvature
scales in phase with enclosed area.

Protocol `monitor_holonomy_noise_null_v0_2` independently resamples every flat
connection node in the tangent space, using 128 frozen seeds over loops with
`8` through `48` perimeter edges. The noise amplitude was frozen at `0.0195`.
At the 40-edge reference loop, mean minimum edge worst-direction retention is
`0.990310` against
the main control's `0.990033`, an absolute difference of `0.000276`.

| scaling test | slope | intercept | R-squared |
|---|---:|---:|---:|
| curved maximum canonical angle vs area | 83.8378 | 0.01178 | 0.999975 |
| flat-noise signed-angle variance vs perimeter | 0.001078 | 0.00183 | 0.947972 |

All frozen gates pass. This does not make an observed real-model loop
"curvature" by threshold. A real audit must condition its empirical null on
rank, perimeter, edge-retention statistics, and estimator uncertainty, then report the
observed conjugacy angles together with an empirical exceedance probability.
High raw holonomy with a high noise-null quantile is an estimator problem, not
a blue-team priority signal.

## Consequences for the current program

### Blue-team monitors

A sequence of high pairwise transfer scores can miss accumulated phase.  A
monitor audit should include context-by-checkpoint Wilson loops.  High-curvature
plaquettes are natural stress-test and data-acquisition targets even when every
edge passes the ordinary lineage gate.

### Feature-reward training

The current bundle-energy score `||U^T x||^2 / ||x||^2` is gauge invariant.  It
survives rotations inside the retained subspace, which is a concrete reason to
prefer block-energy rewards over arbitrary single coordinates when semantic
specificity permits.  Signed or componentwise rewards are gauge covariant:
they need an explicit transport connection, and their trust should be reduced
where loop holonomy is large.

This suggests two distinct allocation policies:

- audit sampling may upweight high-curvature cells;
- trusted feature-reward allocation may downweight them or fall back to
  invariant block energy.

"Parallel-transport the reward" is not, by itself, a cure. In a curved region
the transported coordinate depends on its path. Any signed-coordinate policy
must freeze a convention before outcomes: choose a rooted spanning tree on the
context-by-checkpoint grid and transport every coordinate along its unique tree
path. Every off-tree edge then closes an audit loop against that path. The tree
makes the coordinate reproducible; the off-tree canonical angles measure the
ambiguity it cannot remove.

### Disparate weight edits

Signed bundle coordinates are precisely the direct-edit branch's useful
information.  High holonomy means there is no path-independent global signed
coordinate, even when rank and edge retention look healthy.  In that regime,
one global low-rank edit is wrong-shaped; the admissible object is a transported
family of local edits or a coordinated section.

## Next real-model use

No new model-bearing run is needed to define the diagnostic.  Once prompt- and
checkpoint-specific bases share a registered edit space, compute Procrustes
transports on a small grid, freeze a rooted spanning tree, and seal edge
singular values, canonical loop angles, and matched resampling nulls before
behavioral outcomes. The first empirical question is not whether curvature
causes failure, but whether noise-calibrated loop closure adds grouped held-out
predictive value beyond edge chordal lineage, worst-direction retention,
occupancy, rank, eigengap, and Jacobian visibility.

Canonical receipts:

- `artifacts/monitor_holonomy_control_v0_3.json`
- `artifacts/monitor_holonomy_noise_null_v0_2.json`

## Independent specification test

Fable's `files(7).zip` was imported byte-for-byte under archive SHA-256
`F297580DEDBF2E3161D972F599E513EA6EA30526C66BB3CFFEF41AD28AC7AB64`.
Its implementation uses only this report's prose construction and independently
reproduces the headline values to six decimals, including both determinants.
The imported script is now a permanent documentation test, so changing the
construction prose without updating its numerical contract becomes visible in
the test suite.
