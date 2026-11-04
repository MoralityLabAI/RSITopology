# ASMP-9 v0.20 prior-art gate

Status: development-only.

## Classical ingredients

The following must be treated as prior art, not novelty:

1. Biconnected edge blocks, articulation vertices, and their linear-time
   depth-first-search decomposition. The primary algorithmic reference is
   Robert Tarjan, ["Depth-First Search and Linear Graph
   Algorithms"](https://doi.org/10.1137/0201010), *SIAM Journal on
   Computing* 1(2), 1972.
2. Reliability multiplication over blocks/one-point unions under independent
   component states. This is standard network-reliability and
   reliability-polynomial structure. As one explicit modern statement, Brown,
   Mol, and Oellermann,
   ["An infinite family of 2-connected graphs that have reliability
   factorisations"](https://doi.org/10.1016/j.dam.2016.11.006),
   *Discrete Applied Mathematics* 218 (2017), state that reliability
   polynomials multiply over blocks.
3. Exact network-reliability evaluation and design as a generally hard
   problem. Relevant entry points include Michael O. Ball, "Complexity of
   network reliability computations,"
   [DOI `10.1002/net.3230100206`](https://doi.org/10.1002/net.3230100206),
   *Networks* 10(2), 1980, and the later network-reliability complexity
   surveys. This citation establishes the surrounding hardness landscape; it
   is not asserted to prove the exact optimization complexity of the frozen
   ASMP-9 local block objective.
4. Separable integer resource-allocation dynamic programming.

## Residual ASMP-9 contribution

The candidate contribution is only the exact translation:

```text
conditional comparison counts
  -> ternary residual directions
  -> full reward-gauge quotient liveness
  -> block-local strong connectivity
  -> product of block-local access probabilities
  -> exact between-block integer allocation.
```

The result would identify the irreducible finite-design objects as the
vertex-biconnected cyclic blocks. It would not claim a new block theorem,
reliability factorization, or general local reliability algorithm.

## Hostile-referee question

Does global residual strong connectivity genuinely imply strong connectivity
inside every undirected block, or can a directed path leave one articulation
point and re-enter the block through another?

The block-cut forest supplies the answer: an outside path connecting two
distinct articulation vertices of one block would create an undirected cycle
spanning multiple blocks, contradicting maximal biconnectivity. The registered
protocol must nevertheless test this implication directly on fresh
multiblock graphs rather than cite the decomposition alone.

## Prior-art disposition

The prior-art gate passes only for the narrow translation claim. It fails for
any wording that calls the block decomposition, block product, Tarjan
algorithm, reliability factorization, or separable Bellman allocation new.
The exact finite-design problem *inside* a general biconnected residual block
remains unclassified here; the Ball citation cannot be used as a substitute
for a reduction proving hardness of this specific objective.
