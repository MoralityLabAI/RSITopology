# Completion audit v0.26

## Proved

- Exact costed alternating bisimulation preserves universal safety and the
  full worst-path vector budget region.
- The strategy transfer retains unrestricted quotient-history memory.
- Deterministic finite quotients inherit the v0.25 SCC/cycle formula.
- Decorated covers through 96 raw states transfer with zero failures in two
  implementations.
- Thue-Morse has exact half rate but no finite exact stationary quotient.
- Finite exact abstraction is sufficient and explicitly not necessary.
- Five definition mutations are rejected centrally and independently.

## Verification boundary

The predecessor inventory contains 26 packages and 294 tests. This package
adds 10 focused tests, so the expanded chain contains 304 tests. The explicit
27-package regression passed all 304 tests in 281.10 seconds (285.43 seconds
including the PowerShell wrapper) with Python bytecode and pytest caching
disabled.

## Not claimed

Approximate bisimulation, zero-error robustness under approximation,
nonadditive tree costs, continuous-belief quotient construction, and the
nondeterministic multidimensional mean-payoff region remain open.

V0.27 resolves the narrower approximate-cost case under exact safety, proves
the sharp strict-margin condition that can imply exact safety, and refutes
zero-error transfer from metric closeness alone. Nonadditive costs, arbitrary
approximate transition matching, and the other listed global gaps remain open.

V0.28 subsequently handles nonadditive realized-language log-cardinality by
adding a port-specific causal history-fiber entropy profile. Its exponential
clone proves that this extra profile cannot be inferred from finite quotient
state or successor-class data alone.

V0.31 subsequently closes the listed nondeterministic finite-quotient
mean-payoff gap. The exact region is an intersection over memoryless adversary
policies of reachable-SCC cycle-polytope unions. Continuous-belief quotient
construction remains open.
