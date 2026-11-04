# ASMP-9 v0.26.1 execution note

## Status

```text
unavailable_runner_error_before_adjudication
```

The registered v0.26.1 runner stopped before creating its output directory or
emitting a gate record.

The Windows peak-memory helper called `GetProcessMemoryInfo` without declaring
the function's handle argument types. On a 64-bit process, `ctypes` attempted
to narrow the handle and raised:

```text
ctypes.ArgumentError: argument 1: OverflowError: int too long to convert
```

No repair verdict exists for v0.26.1. The immutable v0.26 source artifacts were
read but not altered.

A successor may change only the resource-measurement implementation, retain
the v0.26.1 adjudication logic and immutable v0.26 source hashes, and register
before execution.
