# ASMP-9 v0.19.1 post-run note

## Frozen verdict

```text
finite_budget_cactus_dp_not_established_v0_19_1
```

The registered run completed in `431.8724859000067` seconds against the
unchanged `180`-second wall-time cap. Gate `G9_resource_and_scope` therefore
failed. The cap is not relaxed and the verdict is not reinterpreted.

Peak resident memory was `23,367,680` bytes and no GPU was used.

## Scientific payload

The other nine gates passed:

- the registration, sealed-file hashes, and fresh-cell registry matched;
- the cached integer residual engine reproduced the burned v0.19
  factorization hash and bridge equalities;
- every fresh direct cactus probability equaled the product of its cycle
  factors;
- bridge-count changes remained irrelevant and optimized bridges stayed at
  their mandatory floor;
- Bellman recursion matched independent exhaustive cycle-total enumeration;
- the full positive edge-allocation census matched Bellman and induced only
  within-cycle-balanced optima;
- both frozen counterexamples reproduced exactly; and
- all three outcome-neutral comparator cells were classified.

The independent verifier passed all `11/11` checks, including the total
gate-vector-to-verdict mapping. This corrects the v0.19 verifier's inability to
represent a valid negative resource outcome.

All v0.19.1 scientific cells are now burned. They may be used for regression
and performance diagnosis, not as fresh confirmation in a successor.

## Interpretation

Caching graph liveness by ternary residual state is arithmetically exact, but
the registered workload still exceeded the resource cap. Version 0.19.1 is
therefore evidence about the implementation bottleneck and a fully replayed
negative registered outcome, not an established finite-budget cactus theorem.

Any successor must first profile the burned workload and identify the
dominating stage. It must not select a smaller scientific cell merely because
that cell is more likely to pass. A proof-level contraction, a demonstrably
equivalent faster exact evaluator, or a prospectively justified resource model
is required before new cells are registered.

## Claim boundary

No result here establishes arbitrary-graph finite-budget allocation, adaptive
allocation, dependent-response robustness, behavioral reward identification,
general inverse reinforcement learning, or ASMP-9 at full scope.
