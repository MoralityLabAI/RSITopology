# ASMP-3 online-normal-form stopping boundary v2.11

## Recommendation

Stop extending the current black-box online-extractor harness after v2.11.

The harness has now computed the exact information partitions, probe frontier,
positive-noise safety tradeoff, and sharp path-error loss.  Larger values of
`N`, more rational denominators, or more copies of the same candidate/noise
patterns cannot change any remaining ASMP-3 blocker.

## Harness-backed reasons

1. **Decision-only observations:** the intersection of valid singleton witness
   sets is empty for every `N>=2`; the safe success is exactly zero.
2. **Unbound ideal search:** `k` ideal probes achieve exactly `k/N`; increasing
   the finite grid only repeats the combinatorial identity.
3. **Trace without `H`:** every positive decoy mass puts valid and invalid worlds
   in the same observation class, forcing Las Vegas success zero.
4. **Trust without recheck:** invalid-output probability is exactly the decoy
   mass; this is an identity, not a sampling estimate.
5. **Uncontrolled path error:** soundness zero is compatible with validated
   finder success zero.
6. **Controlled path error:** `max(0,1-s-delta)` is attained by an explicit joint
   law for all 270 registered rational rows.
7. **Positive lane:** all 12 v2.10 compositions satisfy the six-clause contract
   with positive exact margins and complete resource ledgers.

## What cannot be decided by this harness

- whether a future ASMP-3 definition should require the six-clause online
  contract;
- whether `WV-FIX` or `WV-ADM` is the intended left-hand class;
- whether task-specific non-black-box structure yields a different converse;
- universal interactive communication/query/honest-prover lower bounds;
- external expert acceptance or reproduction; and
- noise laws outside the registered adaptive path-control model.

These are normative, theorem-design, or external-evidence questions.  They are
not unresolved parameter values in the current program.

## Legitimate resume triggers

Resume only with at least one of:

- an authoritative successor definition freezing the operational interface;
- a concrete non-black-box protocol family that evades the v2.11 observation
  model;
- a new interface-uniform lower-bound theorem;
- a new correlated-noise hypothesis with a provable path-level consequence; or
- attributable independent expert reproduction.

Absent such a trigger, additional rows would create volume without increasing
the proved scope.
