# Result v0.30

## Resolved subproblem

The sequential minimax binary prefix-free cost omitted from v0.29 now has an
exact causal-factor distortion law:

`P_target(T) <= P_source(T) + C_phi(T)`,

where `C_phi(T)` is the worst-path sum of the local rounded successor-fiber
costs. Bidirectional `o(T)` profiles preserve the registered prefix-cost region
when the associated safe strategy transfers exist.

## Harness evidence

- The central implementation exhausts 332,928 binary causal morphisms through
  depth three with zero violations.
- It checks 512 regular clone/horizon rows, 16,384 mixed schedules, seven
  powers of the terminal-bijective disclosure block, and 8,192 sparse
  horizons.
- The import-independent verifier checks all 4,096 binary output maps on the
  full depth-two ternary tree, 30 explicit regular trees, 15,625 separately
  evaluated mixed schedules, and 16,384 sparse horizons.
- Eight false simplifications are explicitly rejected, including terminal
  fibers, unrounded products, one final ceiling, minima, boundedness, and
  `liminf`.

The corrected sharp threshold is `T >= 3`: for ternary repetition,
`ceil(T log2 3)` equals `2T` at horizons one and two and is strictly too small
thereafter.

## Disposition

The phase boundary agrees with v0.29 because

`log2 F(T) <= C(T) <= 2 log2 F(T)`,

but the positive finite-horizon correction is genuinely different. Terminal
or unrounded fiber entropy cannot replace per-prefix rounded local fibers.

The central wrapper, independent verifier, all 10 focused tests, and lint pass.
The explicit 31-package chain passes all 344 tests in 488.61 seconds with
Python bytecode and pytest caching disabled. Exact wrapper timings are recorded
in `COMPLETION_AUDIT_v0_30.md`.

## Not claimed

This result does not claim average-length or stochastic source coding,
nonbinary coding, construction of public quotients for arbitrary nonlinear
plants, or adversarial multidimensional mean-payoff synthesis. It is one
cost-transfer layer of ASMP-4, not a global solution of every remaining
construction problem.
