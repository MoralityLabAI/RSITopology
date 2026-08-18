# ASMP-9 v0.11 registered execution attempt

## Status

`unavailable_wall_time_no_scientific_result`

## Bound run

The implementation was frozen at:

```text
110609c569a2ccc35388c857d01ca39e7d5a0f0a
```

and separately registered at:

```text
00b6f0a
```

All fourteen sealed hashes matched before execution. The runner was invoked
against the registered 262,144-tuple three-context census, 4,096 seeded cells,
and the frozen 360-second wall-time limit.

## Outcome

The external command timed out after 424 seconds. The Python worker was still
running with approximately 425 CPU seconds and 24.6 MB resident memory. It was
terminated. No artifact directory or scientific output was produced.

This is not a failed mathematical gate and not evidence for or against the
context-gluing theorem. It is an operationally unavailable registered attempt:
the literal implementation recomputed exact rational incidence ranks inside
every tuple and could not meet its own resource envelope.

## Repair constraint

Any repair must:

- preserve the exact tuple, seed, status, gate, and resource specifications;
- preserve exact rational rank checks;
- optimize only by precomputing the 64 possible four-item graph ranks and
  component counts before traversing graph triples;
- use new versioned source, protocol, registration, and output names; and
- retain this unavailable attempt unchanged.
