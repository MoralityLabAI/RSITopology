# ASMP-9 general comparison-graph allocation protocol v0.17

## Question

What replaces balanced edge allocation when the conditional reward quotient
has more than one independent cycle direction?

Version v0.16 proves exact balancing on one cycle. Version v0.17 tests the
derived general-graph replacement:

1. full conditional-fiber rank is residual-cycle liveness;
2. raw binomial counts compress exactly to `Z/I/F` edge statuses;
3. the continuous probability-box adversary reduces to endpoints;
4. minimal bad boundary supports determine the worst-failure
   large-deviation exponent; and
5. their primal/dual hypergraph game, not raw edge balance, determines the
   asymptotic allocation.

## Fresh graphs

All scientific graph/parameter cells are disjoint from the burned v0.17
development census.

### Five-node wheel

```text
four-cycle 0-1-2-3-0 plus hub 4 joined to all four rim vertices
|V|=5, |E|=8, beta_1=4
```

### Theta `(1,3,3)`

```text
three internally disjoint terminal paths of lengths 1,3,3
|V|=6, |E|=7, beta_1=2
```

### Four-cycle with a bridge tail

```text
cycle 0-1-2-3-0 plus bridge 0-4
|V|=5, |E|=5, beta_1=1
```

### Six-cycle control

```text
|V|=|E|=6, beta_1=1
```

## Registered gates

### G0 — registration binding

Every sealed file matches its registered SHA-256, the implementation commit
precedes the registration, the registration commit is the execution head,
and tracked files are clean.

### G1 — registry completeness

All six residual-rank cells, three availability cells, and three
bad-support/certificate cells are present exactly once. None of the fresh
graphs is isomorphic to a same-order graph in the burned development
registry. The finite counterexample has one complete labelled-allocation
census.

### G2 — residual-rank identity

For every fresh capacity cell and every realized count vector:

```text
fiber affine rank = beta_1(H_y),
```

where `H_y` is induced by residual strongly connected components.

### G3 — representative invariance

Every count representative of one conditional fiber returns the same
residual rank, even when its residual digraph differs.

### G4 — three-state exactness

For each availability cell, the `3^|E|` status polynomial equals direct raw
binomial enumeration grouped by conditional-fiber affine rank.

### G5 — endpoint reduction

For every registered graph, edge, and assignment of other edge statuses,
replacing that edge's `Z` or `F` status by `I` never destroys liveness.
The resulting exact coordinate law has nonnegative coefficients:

```text
A(p)=c-(c-a)(1-p)^n-(c-b)p^n.
```

This directly verifies the sign condition used by the coordinatewise
concavity proof.

### G6 — bad-support completeness

Exact ternary enumeration recovers:

- all 15 two-edge supports on the six-cycle;
- the 15 registered supports on theta `(1,3,3)`; and
- the six cycle-edge pairs on the four-cycle-with-tail, with the bridge
  absent from every minimal support.

Every reported support has a bad orientation, and every proper subset is
live under every orientation.

### G7 — primal/dual exponent certificates

Exact rational certificates must agree:

```text
cycle6:
  primal weights=(1/6,...,1/6)
  dual=uniform over 15 pairs
  tau=1/3

theta133:
  primal weights=(0,1/6,...,1/6)
  dual=half-uniform over the three pairs in each length-three path
  tau=1/3

cycle4_tail:
  primal weights=(1/4,1/4,1/4,1/4,0)
  dual=uniform over six cycle-edge pairs
  tau=1/2.
```

### G8 — finite nonuniform counterexample

At theta `(1,3,3)`, `N=14`, and `epsilon=2/7`, enumerate every positive
labelled allocation and every endpoint label. The exact optimum must beat
uniform `(2,2,2,2,2,2,2)`, and no allocation whose counts differ by at most
one may be optimal.

This is a prospective theorem stress test. Failure remains a valid result.

### G9 — resource and scope

```text
CPU only
GPU prohibited
wall time <= 180 seconds
peak resident memory <= 1 GiB
```

The exact claim boundary must be copied without alteration.

## Stop and interpretation rules

- Any failed gate gives `registered_exact_result_failed`.
- No threshold, graph, or expected support may be changed after
  registration.
- The burned development census is not pooled with the fresh verification.
- A pass verifies the finite instances and analytic proof identities. It
  does not turn them into behavioral evidence.

## Claim boundary

A pass is fresh exact verification of residual-cycle fiber rank, ternary
status compression, coordinatewise endpoint reduction, minimal-bad-support
exponent certificates, and one finite nonuniform-allocation counterexample
for independent Bernoulli comparison graphs.

It is not an every-budget optimum theorem, adaptive allocation, dependent or
unknown-link behavior, downstream test-power theorem, general inverse
reinforcement-learning identification, or ASMP-9 resolution.
