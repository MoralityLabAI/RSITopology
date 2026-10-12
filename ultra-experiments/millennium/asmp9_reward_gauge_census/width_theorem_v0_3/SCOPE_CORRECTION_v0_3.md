# ASMP-9 width theorem v0.3: mandatory scope correction

## Status

The registered v0.3 verdict
`sharp_query_width_theorem_implementation_verified` is **not claim-valid as
written**. Its theorem domain included:

```text
0 <= delta < 1.
```

The sharp width formula was proved and implemented for the strict-ambiguity
regime:

```text
0 < delta < 1.
```

Including `delta=0` is a load-bearing scope error. Version 0.3 is retained
unchanged for auditability and assigned the scientific status:

```text
superseded_scope_error_delta_zero.
```

It may not be cited as verification of the theorem on the registered closed
interval.

## Why zero is different

For `0 < delta < 1`, an integer score of zero has possible responses
`{-1,0,+1}`. Two candidates are robustly separated exactly when a query gives
strict opposite nonzero integer scores.

At `delta=0`, the response to a zero score is exactly `{0}`. A tie versus a
nonzero score is therefore separating information. Strict opposite signs are
sufficient but no longer necessary.

The v0.3 lower-witness search checked only strict opposite signs. It correctly
certifies the lower bound for every positive `delta<1`, but it does not certify
the `delta=0` endpoint.

This distinction is visible in the preceding v0.2 census: exact signs can
separate the bound-two registry at coefficient width one, whereas the
half-unit ambiguity arm needs width three.

## What survives

The constructive upper bound, extremal pair, algebra, implementation, and
disjoint-grid replays remain valid for:

```text
0 < delta < 1.
```

The correction narrows the theorem; it does not change the formula inside that
open interval.

## Repair rule

Version 0.3.1 must:

1. state `0 < delta < 1` in both prose and machine-readable protocol;
2. add a control showing that the v0.3 lower witness can separate through a
   tie at `delta=0`;
3. use fresh full-pair cells and new random seeds; and
4. report the zero-noise access threshold as a separate open theorem target,
   not as a corollary of the positive-ambiguity result.

