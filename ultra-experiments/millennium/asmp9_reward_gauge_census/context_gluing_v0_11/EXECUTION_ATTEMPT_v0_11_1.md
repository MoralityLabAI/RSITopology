# ASMP-9 v0.11.1 registered repair attempt

## Status

`unavailable_wall_time_no_scientific_result`

## Bound run

The implementation-only repair was frozen at:

```text
fbdf5d9197b57509ddf3815de336c4a918e831c2
```

and separately registered at:

```text
cedecf2
```

All twenty sealed hashes matched before execution. Every scientific cell,
seed, status, gate, and resource limit was identical to v0.11. The tuple
census used precomputed exact ranks and components.

## Outcome

The external command timed out after 404 seconds. The worker remained active
with approximately 409 CPU seconds and 23.1 MB resident memory and was
terminated. No artifact directory or scientific output was produced.

This is a second operationally unavailable attempt, not a mathematical gate
result. The failed optimization localizes the remaining cost to the seeded
mixed-cycle basis and witness checks: tuple-level rank precomputation alone
was insufficient to meet the unchanged cap.

## Further-repair constraint

A second repair may profile cells because the original scientific protocol
and gates were already frozen before either attempt. It must:

- preserve all 262,144 tuples and all 4,096 seeded cells;
- preserve all statuses, gates, and the 360-second/2-GiB envelope;
- replace repeated exact column-image and basis calculations only with
  algebraically equivalent rank/component formulas;
- validate equivalence exhaustively on burned registries and on a
  preregistered deterministic subset of the seeded generator; and
- retain both unavailable attempts unchanged.
