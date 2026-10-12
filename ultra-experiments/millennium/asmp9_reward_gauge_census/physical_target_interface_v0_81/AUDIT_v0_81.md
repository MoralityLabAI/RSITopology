# Independent result audit v0.81

## Status

**Pass.** The registered full-pass decision reproduces from the raw rows
without importing `structured_target.py` or `execute_registered.py`.

## Checks

1. Recomputed the registration and all execution-receipt hashes.
2. Rehashed every prereveal source named by the registration.
3. Confirmed byte identity of primary/replay rows, results, and receipts.
4. Parsed exactly 60 unique rows in the fresh `v081|...` namespace.
5. Recomputed every route margin from the four rational reward coordinates.
6. Rechecked shaping invariance and exact ±2 non-gauge offsets.
7. Independently solved all four context likelihood score equations by
   80-step bisection.
8. Recomputed all 20 target errors and signs.
9. Recomputed the 24 shaping/base probability differences.
10. Recomputed the structured Hellinger union bound and accumulated TV term.
11. Confirmed the fixed sequence `W0 -> I0 -> D0 -> R0 -> L0 -> M0`.

## Numeric reconciliation

| Quantity | Independent value | Frozen value |
| --- | ---: | ---: |
| maximum R0 error | 0.06652036905583891 | 0.06652036905583891 |
| maximum L0 difference | 0.05078125 | 0.05078125 |
| Hellinger union bound | 7.42707333822635e-12 | 7.42707333822635e-12 |
| accumulated TV penalty | 0.04503465813551455 | 0.04503465813551455 |
| robustified M0 bound | 0.04503465814294162 | 0.04503465814294162 |

The independent audit receipt is
`artifacts_v0_81/independent_audit_v0_81.json`.

## Claim boundary

This audit verifies arithmetic, source binding, replay, and adjudication for
one controlled fixture. It does not independently validate the behavioral
model or expand the ASMP-9 claim.

