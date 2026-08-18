# ASMP-4 stochastic-semantics stopping argument v0.8

## Decision

Stop treating randomized-code enumeration as evidence for one canonical
region until the probability/disturbance order is registered.  The same smooth
bounded-input plant and zero-message architecture is safe under one coherent
reading and infeasible under the other three.

## Why this is not a numerical gap

The continuous diagonal fixture has exact probabilities zero and one.  Its
finite grids have exact rational success `(1-1/N)^T`, and 484,524 enumerated
pairs reproduce that formula without error.  Sixty further exact cells expose
noncommuting alphabet and horizon limits.  Increasing grid size or Monte Carlo
budget cannot choose which limit or quantifier the source intended.

## Relationship to prior stopping evidence

V0.6 shows that sensor registration changes the exact region.  V0.7 adds a
nonrectangular relational region and proves support derandomization.  V0.8
shows that support-zero-error and per-disturbance-almost-sure safety themselves
separate on uncountable disturbances.  These are compatible nested results:
each closes a declared branch while exposing a missing canonical domain or
quantifier.

## Productive reopening conditions

Reopen the stochastic lane when the canonical problem declares:

- the safety event (`S_path`, `S_uniform`, or `S_support`);
- whether disturbances observe shared randomness or realized controls;
- a countable or uncountable disturbance domain with measurability conventions;
- and support, worst-seed, or expected transcript accounting.

An external proof audit finding an error in the countable-prefix argument or
diagonal fixture would also justify reopening.  Until then, more simulations
cannot repair the missing stochastic semantics.

The [v0.9 completion atlas](../asmp4_completion_atlas_v0_9/STOPPING_ARGUMENT_v0_9.md)
consolidates this lane with the independent sensor-domain fork and replaces a
lane-specific pause with a sealed, requirement-level stopping certificate.
