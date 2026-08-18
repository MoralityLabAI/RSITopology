# Completion audit v0.30

## Requirement ledger

| Requirement | Authoritative evidence | Status |
|---|---|---|
| Freeze the problem, v0.3 cost model, and v0.29 predecessor | Three SHA-256 seals in both implementations | Pass |
| Prove the finite-horizon rounded transfer | Backward Kraft induction in `THEOREM.md` | Pass |
| Check broad finite causal trees | 332,928-map binary central census | Pass |
| Cross-check without importing central code | 4,096-map ternary census and independent recurrence | Pass |
| Make sequential rounding sharp | 512 central clone rows and 30 explicit independent trees | Pass |
| Locate the exact ternary threshold | Equality at `T=2`, strict failure of one ceiling for every `T >= 3` | Pass |
| Reject terminal-fiber control | Disclosure powers with terminal fiber one and exact one-third bit gap | Pass |
| Audit maximum, sparse, and `limsup` boundaries | Central and independent boundary families | Pass |
| Reject plausible theorem mutations | Eight central and eight independent mutation witnesses | Pass |
| Preserve predecessor coverage | 30 predecessor packages / 334 predecessor tests | Pass |
| Run expanded regression | 31 packages / 344 tests | Pass |

## Focused execution record

The central ten-gate wrapper passed in 59.80 seconds. The import-independent
verifier passed in 4.08 seconds. All 10 focused tests passed in 57.83 seconds,
and Ruff passed in 0.26 seconds.

The explicit 31-package regression passed all 344 tests in 488.61 seconds
(494.33 seconds including the PowerShell wrapper), with Python bytecode and
pytest caching disabled.

## Independence audit

`verify_prefix_kraft_fiber.py` contains its own tree normalization, successor
enumeration, Kraft recurrence, causal-map evaluator, ternary map census,
explicit tree generator, mixed recurrence, sparse boundary, mutation suite,
document sentinels, and predecessor inventory. Its AST import audit rejects an
import of `prefix_kraft_fiber`.

## Not claimed

The package does not construct a nonlinear public quotient, prove that every
safe plant admits the required bidirectional factors, solve stochastic coding,
or synthesize multidimensional adversarial mean-payoff regions. Those remain
outside this completion claim.
