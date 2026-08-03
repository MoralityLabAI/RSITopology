# Result v0.25

Periodic block completeness is exact for finite public additive scheduler
state, but only componentwise. Each reachable cyclic strongly connected
component contributes the upward convex hull of its simple-cycle mean cost
vectors. Its weighted entropy is a minimum-cycle-mean function, and periodic
closed walks are dense in the component polytope.

A strongly connected two-state fixture has Pareto cycle means `(1,3)` and
`(3,1)` with dominated connector cycle `(5,5)`. Explicit periodic walks
approach `(2,2)` with exact error `3/(k+1)`, proving connector overhead
vanishes.

An irreversible fork gives the sharp negative boundary. Its true region is a
disjunction of the two component quadrants. The point `(2,2)` is not
achievable, yet one global support family convexifies across the fork and
accepts it. Component-indexed support families and their disjunction are
therefore load-bearing outside one recurrent SCC.

The central harness covers every nonempty two-state edge subset. The
import-independent verifier uses mutual reachability rather than Tarjan's
algorithm, covers all 511 nonempty three-state edge subsets, and checks over a
thousand closed walks against independently enumerated simple-cycle supports.

This is a theorem for finite public additive scheduler abstractions. It does
not establish such an abstraction for every nonlinear ASMP-4 registration.

The complete 26-package chain passes all 294 tests in 269.12 seconds.

The v0.26 successor proves that an exact costed alternating-bisimulation
quotient preserves the full vector budget region and therefore transfers this
finite deterministic formula to any registered public-history game admitting
such a quotient.

The v0.31 successor supplies the finite adversarial formula: intersect the
component-indexed cycle-polytope unions over all memoryless adversary policies.
The empty-adversary special case is exactly the theorem above.
