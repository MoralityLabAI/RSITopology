# ASMP-5 claim packet

## Frozen estimand

For each finite cell, report the minimum certified depth at which an analyst-only semantic label is unsafe, or infinity after exhaustive reachability through horizon eight. Compare adaptive checker activation with a frozen-root evaluator over the same candidate update IDs.

## Primary finite claim

At width six and mutation radius one or two, at least one registered certificate rule must admit an adaptive unsafe path of depth at most four while its matched root arm has no unsafe reachable state through horizon eight. Root refinement must remove that path and preserve an eight-step chain with nine distinct safe behavior vectors.

Width four is a capacity diagnostic: because it contains only eight safe behavior vectors, its nine-vector liveness criterion is registered as unavailable, not failed.

## Architecture

A state is `(behavior, installed_checker, progress)`. Every accepted transition flips exactly one behavior bit, advances progress by one, supplies one of four proof tokens, and installs a checker within the registered Hamming radius. Both arms store that checker. In the adaptive arm it evaluates the next edge; in the frozen-root arm the original checker evaluates every edge.

Checkers are all sixteen truth tables over `(proposed_hazard_bit, proof_class)`. The root table accepts both proof classes for hazard-free behavior and rejects both for hazard-marked behavior. This permitted behavioral input is not an analyst-label leak: the semantic label table is constructed separately and is never passed to generation or reachability.

For behavior width `N`, horizon `H`, and checker-mutation radius `r`, the unpruned universe contains `(H+1) 2^N 16` states and

```text
H 2^N 16 N 4 sum_{k=0}^r C(4,k)
```

candidate edges. The largest registered universe (`N=6`, `H=8`, `r=2`) therefore contains 9,216 states and 2,162,688 candidate edges. The implementation streams the universe hashes and retains only reachable layers. Exceeding either frozen resource ceiling yields `unavailable_resource_cap_stop_sequence`; it never triggers sampling.

## Boundary

Passing establishes only a bounded, exact finite-state separation. It does not establish open-ended recursive self-improvement, an infinite reflective-safety theorem, robustness to learned checkers, or novelty over trusted-kernel and proof-carrying-code results.
