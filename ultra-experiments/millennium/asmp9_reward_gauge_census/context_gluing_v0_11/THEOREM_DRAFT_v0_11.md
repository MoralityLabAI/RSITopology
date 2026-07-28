# Context-local utilities and the mixed-cycle gluing obstruction

## Status

Development theorem draft for ASMP-9 v0.11. The linear algebra is a direct
specialization of graph Hodge theory and the local-to-global obstruction is a
finite real-valued instance of classical gluing. Novelty is not claimed.

## Context-labelled comparison object

Let `X` be a finite item set. Each registered context or finite history `c`
has a comparison graph

```text
G_c = (X, E_c)
```

and an edge flow `y_c`. Parallel edge copies in different contexts remain
distinct. Their union is the context-labelled multigraph

```text
M = (X, disjoint_union_c E_c).
```

The flow is **context-locally scalar** when for every context there is a
utility `u_c` such that

```text
y_c(i,j) = u_c(j)-u_c(i).
```

It has a **shared scalar** when one context-independent `u` satisfies the same
equation on every labelled edge.

## Exact quotient theorem

Let `D_c` be the incidence matrix of `G_c`, `D_local` their block-diagonal
incidence map, and `D_M` the incidence matrix of the labelled multigraph. Then

```text
im D_M is a subspace of im D_local.
```

The dimension of locally scalar flows that do not reduce to one shared scalar
is

```text
q
  = rank(D_local)-rank(D_M)
  = sum_c (|X|-components(G_c))
      - (|X|-components(M))
  = beta_1(M)-sum_c beta_1(G_c).
```

The registered theorem uses one declared item universe in every context,
including isolated items as local gauge components. Context-specific item
universes are a later extension, not part of v0.11.

## Sharp access theorem

The cycle space of every `G_c` embeds on its own labelled edge coordinates in
the cycle space of `M`. The direct sum of the local cycle spaces therefore has
dimension `sum_c beta_1(G_c)`. A basis extension to the full cycle space of
`M` contributes exactly

```text
q = beta_1(M)-sum_c beta_1(G_c)
```

mixed-context cycles.

Conditional on local scalarity:

- all `q` independent mixed-cycle circulations vanish if and only if a shared
  scalar exists;
- `q=0` forces every locally scalar flow to glue by design, so it cannot count
  as a live empirical test of the alternative; and
- fewer than `q` independent linear checks cannot certify the hypothesis
  uniformly, because a nonzero quotient direction remains in their kernel.

Thus `q` is both the obstruction dimension and the sharp number of independent
compatibility checks in the registered exact-linear access model.

The total exact decision vocabulary is:

- `local_scalar_failed`;
- `shared_scalar_forced_by_design` when `q=0`;
- `shared_scalar_verified` when `q>0` and every mixed circulation vanishes;
  and
- `shared_scalar_refuted` when at least one mixed circulation is nonzero.

## Minimal counterexample

Two items and two contexts are minimal. Let each context compare the same
ordered pair. Assign edge differences `0` and `1`.

Each one-edge context is exactly scalar. No shared scalar can give two
different differences to the same item pair. The labelled multigraph has two
parallel edges:

```text
beta_1(M)=1,
sum_c beta_1(G_c)=0,
q=1.
```

This is a finite history-sensitive no-go when the two contexts are interpreted
as two histories. It does not imply that human or model preferences follow
this exact cardinal-difference grammar.

## Claim boundary

The theorem concerns exact real-valued comparison differences on a finite
registered context-labelled multigraph. It does not cover ordinal-only
choices, unknown response links, finite-sample estimation, endogenous context
selection, infinite histories, stochastic non-expected-utility
representations, or downstream regret under misspecification.
