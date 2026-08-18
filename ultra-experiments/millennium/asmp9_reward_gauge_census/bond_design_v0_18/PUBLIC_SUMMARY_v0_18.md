# ASMP-9 v0.18: cyclic-core bonds are the failure supports

## Result

Version v0.18 establishes, inside the frozen independent-binomial
conditional-access model inherited from v0.17:

> The inclusion-minimal boundary supports that destroy full
> conditional-fiber quotient rank are exactly the bonds of the graph obtained
> by deleting its original bridges, component by component.

Equivalently, the previously enumerated bad-support hypergraph is the bond
clutter of the cyclic core.

The registered verdict is:

```text
bond_characterization_established_in_frozen_model
```

All eight preregistered gates and all eight separately sealed replay checks
passed.

## Why the theorem holds

The v0.17 residual graph assigns each edge one of three statuses:

```text
Z: one reference arc
I: both arcs
F: one reverse arc.
```

Full quotient rank is available exactly when every original nonbridge edge
lies on a directed residual cycle. After original bridges are deleted, this
is equivalent to strong connectivity on every remaining connected component.

If a residual component is not strongly connected, a source or sink in its
condensation exposes a cut with no arc in one direction. Every edge crossing
that cut must be a `Z/F` boundary edge, because an `I` edge supplies both
arcs. Thus every bad support contains a cut and therefore contains a bond.

Conversely, orienting every edge of a bond in one direction destroys strong
connectivity. Since a proper subset of a bond contains no cut, it cannot be a
bad support. Inclusion-minimal bad supports and bonds are therefore the same
sets.

## Allocation consequence

For unit-sum nonnegative edge weights `w`, the v0.17 large-deviation exponent
becomes:

```text
tau_G(w)
  = min over cyclic-core cuts C of sum_(e in C) w_e.
```

Hence:

```text
tau_G*
  = max_(w >= 0, sum w = 1) min_C w(C).
```

This is the classical budgeted/design version of minimum cut. Fulkerson's
1959 capacity-budget problem and the later general budgeted/design frameworks
of Juttner and Chakrabarty-Mehta-Vazirani are the relevant ancestry. Version
v0.18 does not claim to introduce max-min cut design.

The zero-sum dual is equivalently a fractional packing of bonds:

```text
tau_G* = 1 / nu_b*(G),
```

where `nu_b*(G)` is the maximum total bond mass subject to unit load on each
edge.

The structural search no longer requires enumerating `3^|E|` residual status
vectors. A minimum-cut oracle separates the allocation constraints.
Polynomial solvability is classical; the ASMP-9 contribution is the reduction
from conditional reward-gauge access to that object.

## Cactus closed form

If every nonbridge edge lies on exactly one simple cycle and `M` is the
number of nonbridge edges, then:

```text
tau_G* = 2/M.
```

The unique optimum is uniform on the nonbridge edges and zero on bridges.
This follows because cactus bonds are exactly the two-edge subsets within one
cycle.

## Fresh registered checks

The first proposed fresh registry was mistakenly exercised by the pre-freeze
test suite. Those four cells were declared burned before the protocol was
committed and are listed in the development registry.

The replacement scientific cells were not executed until after registration:

| graph | bonds | direct SCC states | exact `tau_G*` |
|---|---:|---:|---:|
| square/hexagon cactus with bridge | 21 | 177,147 | `1/5` |
| `K_(2,5)` | 37 | 59,049 | `1/5` |
| `K_(3,4)` | 49 | 531,441 | `1/4` |
| cube | 63 | 531,441 | `1/4` |

Across 1,299,078 directly enumerated residual states:

- SCC-minimized bad supports and independently enumerated bonds agreed
  exactly;
- no bond contained an original bridge;
- every cyclic-core cut contained a bond;
- all four frozen rational primal/dual certificate pairs closed exactly; and
- the cactus formula returned uniform weight on ten cyclic edges and zero
  weight on its bridge.

The run took approximately `110.21` seconds, used `23,105,536` bytes peak
resident memory, and used no GPU.

A clean detached replay from the result commit passed the same eight replay
checks, produced a byte-identical Markdown report, and reproduced the complete
scientific JSON payload. Only the execution commit, emission timestamp,
elapsed time, and peak-memory telemetry differed.

## Evidence chain

- implementation freeze:
  `e063a7707b3203e21442c4a77330f72596260a57`;
- registration commit:
  `c72ff1db597c22a56f1a1e13488967fdd116d30e`;
- registration SHA-256:
  `696d7e46c385e3614e99f2da87cacf77bfb3a741c596ac5d4687ca59f8854d0a`;
- protocol SHA-256:
  `c330d2ccda7ed464bb21a077a70bdb79b57941eaf18a850409eb0a776fb9aee8`;
- result SHA-256:
  `78c4a6039dae8230b0f64f3773f9dd6256ac938753d976010bf969f8ae3f3754`.

## What this advances

Version v0.17 identified residual-cycle liveness and an abstract hypergraph
allocation game. Version v0.18 identifies that hypergraph exactly and exposes
its classical optimizer.

This closes the structural asymptotic graph-design question in the frozen
model. It does not close exact finite-budget allocation on arbitrary graphs,
adaptive querying, dependence, unknown response links, behavioral
misspecification, downstream utility, or general reward identification.

## Claim boundary

Exact identification, on the frozen independent-binomial conditional-access
object inherited from v0.17, of inclusion-minimal full-rank failure supports
with cyclic-core bonds; exact fresh finite SCC-versus-bond checks; classical
max-min cut primal/dual certificates; and an elementary cactus closed form.
Not a novelty claim for bonds, cut design, or fractional packing; not an
arbitrary finite-budget integer theorem, adaptive allocation, dependent or
unknown-link response theorem, downstream power theorem, behavioral
reward-identification theorem, general IRL theorem, or ASMP-9 resolution.
