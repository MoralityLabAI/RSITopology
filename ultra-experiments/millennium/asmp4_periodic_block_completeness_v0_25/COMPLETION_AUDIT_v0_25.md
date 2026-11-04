# Completion audit v0.25

## Proved

- Reachable cyclic SCCs classify all eventual finite-scheduler behaviors.
- Each component region is its upward simple-cycle mean polytope.
- Weighted component entropy is a minimum-cycle-mean function.
- Periodic closed walks approximate every component-polytope point.
- A bounded reset connector or one strongly connected recurrent core suffices
  for v0.24 periodic block completeness.
- An irreversible fork requires a component-indexed disjunction and refutes
  cross-component convexification.
- Central and import-independent graph algorithms reject five mutations.

The prior-art boundary credits Karp's minimum-cycle-mean characterization and
Ziemian's finite-type rotation-polytope/periodic-density theorem. No novelty is
claimed for those graph or symbolic-dynamics ingredients.

## Verification boundary

The predecessor inventory contains 25 packages and 284 tests. This package
adds 10 focused tests, so the expanded chain contains 294 tests. The explicit
26-package regression passed all 294 tests in 269.12 seconds with Python
bytecode and pytest caching disabled.

## Not claimed

No finite public additive scheduler abstraction is proved for every nonlinear
plant. Infinite belief spaces, nonadditive tree costs, hidden state, and unsafe
or absent reset connectors remain outside the theorem.

V0.26 closes the exact transfer step when a costed alternating-bisimulation
quotient is supplied. It also proves with a Thue-Morse boundary that existence
of a finite exact quotient is sufficient rather than necessary.

V0.31 closes the remaining additive finite alternating-game calculation using
the classical memoryless-spoiler and multicycle characterization. It does not
alter the open nonlinear quotient-existence boundary.
