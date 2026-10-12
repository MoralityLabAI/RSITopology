# ASMP-9 v0.17 development note

## Status

Burned development evidence. This note may shape a prospective protocol but
is not itself a registered result.

## Main finding

The v0.16 balanced-allocation theorem does not extend to overlapping cycles.

On the five-edge theta graph with path lengths `(1,2,2)`, total trial budget
`N=10`, and `epsilon=1/4`:

```text
uniform (2,2,2,2,2):
  218403/524288

exact optimum:
  228591/524288

gap:
  2547/131072
```

The four optimal labelled allocations give the single-edge path one trial,
give one of the four remaining edges three trials, and give the other three
two trials. No balanced allocation is optimal.

The same optimizer orbit beats uniform at all four burned interiors:

```text
epsilon in {1/8,1/4,3/8,1/2}.
```

## Replacement object

For a realized fiber, the full quotient is available exactly when every
original non-bridge edge lies on a directed cycle in the three-state residual
network.

For large total budgets, let a *minimal bad boundary support* be an
inclusion-minimal edge set that can destroy this property when its edges take
zero/full statuses and all other edges are interior. If `w_e` is the
asymptotic trial fraction, the worst-case failure exponent is controlled by:

```text
tau_G(w)=min_B sum_(e in B) w_e.
```

The optimal exponent is the finite hypergraph game:

```text
max_(w in simplex) tau_G(w).
```

For a simple `k`-cycle this recovers uniform allocation and exponent `2/k`.
For the `(1,2,2)` theta graph, the six bad supports give the unique optimum:

```text
(0,1/4,1/4,1/4,1/4)
```

with exponent `1/2`, versus uniform exponent `2/5`.

## Exact development checks

- 629 direct conditional fibers and all 1,165 count representatives across a
  cycle, theta graph, and bowtie: zero residual-rank mismatches.
- 11 connected bridgeless labelled graphs on three or four vertices:
  6 have uniform allocation asymptotically suboptimal.
- Those six graphs are precisely the labelled copies of `K4` minus one edge,
  the `(1,2,2)` theta graph.
- The theta finite allocation census covered every positive labelled
  allocation for totals 5 through 12.
- The exact artifact completed in 35.93 CPU seconds.

## Interpretation

The correct generalization is not “balance trials over edges.” It is “balance
large-deviation protection over the minimal ways residual quotient liveness
can fail.” Redundant chords can receive asymptotically zero allocation even
though they are non-bridges and participate in multiple quotient cycles.

This is a structural advance toward ASMP-9's general access-allocation
obligation. It remains conditional on a known graph, independent Bernoulli
responses, a known symmetric probability interior, and the full-fiber-rank
liveness endpoint.
