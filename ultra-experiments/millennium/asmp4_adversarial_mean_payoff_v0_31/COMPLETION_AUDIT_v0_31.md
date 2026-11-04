# Completion audit v0.31

## Requirement ledger

| Requirement | Evidence | Status |
|---|---|---|
| Preserve the v0.25 deterministic formula | Empty-adversary specialization in theorem and fixtures | Pass |
| Close v0.26's finite nondeterministic seam | Memoryless-spoiler/SCC multicycle formula | Pass |
| Use the registered cost polarity | Exact `limsup` cost to mean-payoff-`inf` identity | Pass |
| Characterize the entire region | Finite intersection-of-unions polyhedral formula | Pass |
| Preserve nonconvex SCC choices | Controller irreversible-fork counterboundary | Pass |
| Audit strategy memory | Infinite-memory boundary and `1/(k+1)` finite-period slack | Pass |
| Emit winning and losing evidence | Exact cycle-hull witnesses and memoryless spoilers | Pass |
| Check broad finite families | 2,304 central and 1,296 independent decisions | Pass |
| Reject theorem mutations | Eight central and eight independent witnesses | Pass |
| Preserve predecessor coverage | 31 packages / 344 tests | Pass |
| Run expanded regression | 32 packages / 354 tests | Pass |

## Execution record

The central ten-gate wrapper passed in 2.13 seconds. The import-independent
verifier passed in 1.09 seconds. All 10 focused tests passed in 6.29 seconds,
and Ruff passed in 0.17 seconds.

The explicit 32-package regression passed all 354 tests in 336.76 seconds
(339.87 seconds including the PowerShell wrapper), with Python bytecode and
pytest caching disabled.

## Independence boundary

The independent verifier implements its own transitive reachability, SCC
partition, simple-cycle enumeration, rational segment feasibility, policy
enumeration, two-state census, boundary fixtures, mutations, document checks,
and predecessor inventory. It does not import the central implementation.

## Not claimed

This audit does not prove a new multi-mean-payoff theorem, construct an exact
finite quotient for a nonlinear plant, or establish finite-memory attainment
of every closed boundary budget.

The v0.32 successor audit preserves these boundaries and identifies the
missing global grammar plus abstraction/replacement theorem as the residual
dependency root.
