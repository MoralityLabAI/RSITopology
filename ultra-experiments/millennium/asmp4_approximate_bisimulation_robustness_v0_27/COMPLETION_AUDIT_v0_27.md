# Completion audit v0.27

## Proved

- Exact-safety epsilon-cost alternating bisimulation transfers every safe
  causal strategy in both directions.
- Horizon-`T` vector budgets need at most `T epsilon` cumulative slack.
- Worst-path limsup rate regions have Hausdorff slack at most `epsilon`.
- One-state loops attain the cost bound, so its constant cannot be reduced.
- A strict `L delta` signed safety margin implies the exact Boolean clause.
- Equality is sharp and metric closeness alone permits a nonempty/empty
  zero-error region jump at arbitrarily small scales.
- Central and import-independent implementations reject seven mutations.

## Verification boundary

The predecessor inventory contains 27 packages and 304 tests. This package
adds 10 focused tests, so the expanded chain contains 314 tests. The explicit
28-package regression passed all 314 tests in 294.89 seconds (300.06 seconds
including the PowerShell wrapper) with Python bytecode and pytest caching
disabled.

## Not claimed

Approximate safety without a strict guard margin, nonadditive transcript-tree
costs, construction of a finite abstraction for arbitrary nonlinear or
continuous-belief plants, and solution of nondeterministic multidimensional
mean-payoff regions are not claimed.

V0.28 resolves the narrower whole-language log-cardinality case under
port-compatible causal factor maps. Arbitrary tree functionals without a
registered factor-distortion modulus remain outside both the v0.27 and v0.28
claims.
