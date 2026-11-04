# Discounted shaping is a gain-graph quotient

## Status

Unregistered theorem draft. The gain-graph rank formula is classical; this
document specializes it to the ASMP-9 access question.

## Twisted shaping operator

Let `G=(V,E)` be a finite directed multigraph and fix `0<gamma<1`. Define:

```text
(D_gamma Phi)(u->v) = gamma Phi(v) - Phi(u).
```

Rewards differing by an element of `im D_gamma` are related by discounted
potential shaping.

For an edge followed in its registered direction assign multiplicative gain
`gamma^-1`; against its direction assign gain `gamma`. A weakly connected
component is **balanced** when every closed walk has gain one.

For constant `gamma` this is equivalent to the existence of an integer height:

```text
h(v)=h(u)+1
```

on every directed edge `u->v`. Trees are balanced. A directed cycle and two
same-endpoint paths of different lengths are unbalanced.

## Rank and quotient theorem

Let `b_gamma(G)` be the number of balanced weak components, counting isolated
vertices. Then:

```text
rank(D_gamma) = |V| - b_gamma(G),

dim(R^E / im D_gamma)
  = |E| - |V| + b_gamma(G).
```

At `gamma=1`, every component is balanced and the formula reduces to the
ordinary incidence/cycle-space law:

```text
rank(D_1)=|V|-c(G),
dim quotient=|E|-|V|+c(G).
```

At `gamma=0` the gain-graph formula is not used:

```text
rank(D_0)=number of vertices appearing as an edge source.
```

### Proof

`D_gamma Phi=0` imposes `Phi(v)=gamma^-1 Phi(u)` on every edge `u->v`.
Choose a root in one weak component. All potentials are determined by the root
value. They are consistent around every closed walk exactly when the component
is balanced. A balanced component therefore contributes one kernel dimension.
An unbalanced closed walk forces:

```text
Phi(root)=gamma^k Phi(root)
```

for nonzero integer `k`, hence `Phi(root)=0`; the entire component then
vanishes. Thus `nullity(D_gamma)=b_gamma(G)`, and rank-nullity proves both
formulas.

## Trajectory-access theorem

For a trajectory:

```text
tau=(s_0 -> s_1 -> ... -> s_T),
```

let its discounted edge occupancy be:

```text
q_tau(e)=sum_{t:e_t=e} gamma^t.
```

Then for every potential:

```text
q_tau^T D_gamma Phi
  = gamma^T Phi(s_T) - Phi(s_0).
```

Therefore a comparison of trajectories `tau,tau'` is invariant to every
discounted potential shaping exactly when their boundary signatures agree:

```text
-e_(s_0) + gamma^T e_(s_T)
=
-e_(s'_0) + gamma^(T') e_(s'_(T')).
```

Same-start, same-end, same-horizon comparisons are a sufficient special case.
For infinite discounted trajectories with bounded potentials, the terminal
term vanishes and same-start comparisons are invariant in the limit.

## Access consequence

Ordinary loop closure is not the correct discounted query grammar. On a
directed cycle at `0<gamma<1`, `D_gamma` is full rank and the quotient is zero.
A loop return can therefore carry no shaping-invariant edge-reward
information.

Nontrivial finite-horizon access comes from differences of discounted
occupancies with matching boundary signatures—for example, equal-length routes
between the same endpoints. The minimum number of exact independent linear
queries is the quotient dimension above, provided the registered trajectory
grammar spans its left nullspace.

## Claim boundary

This is an exact linear-algebra theorem for edge rewards and discounted
potential shaping. It does not characterize all reward invariances induced by
policies, entropy regularization, transition redistribution, or inconsistent
demonstrators. It is not a novelty claim or a complete ASMP-9 resolution.
