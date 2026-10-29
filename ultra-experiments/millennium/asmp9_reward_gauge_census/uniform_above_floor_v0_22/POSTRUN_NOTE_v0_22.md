# ASMP-9 v0.22 post-run note

## Registered verdict

```text
uniform_above_floor_translation_not_established_v0_22
```

The record is retained as a failed registered attempt.  Nine gates passed and
`G8_complexity_attribution` failed.

## Failure mechanism

The scientific checks did not fail.  The frozen G8 evaluator required the
lowercase substring:

```text
uniform allocation is optimal
```

inside the second forbidden sentence.  The registered sentence begins with
capitalized `Uniform`, so the case-sensitive implementation returned false.
The protocol's three allowed and four forbidden claims were otherwise present
unchanged.

The evaluator is sealed and will not be edited or rerun under v0.22.  A
versioned successor must:

1. replace the string-matching proxy with an exact structured-list equality
   check;
2. use graph cells whose outcomes were unread at the successor registration;
3. preserve the v0.22 numerical record as burned development evidence; and
4. make no change to the mathematical identity, thresholds, or claim
   boundary.

## Evidence retained

- All nine direct ternary-status censuses equaled the registered
  Backman/Tutte specialization.
- All nine fixed-count points lay on `H_-1`.
- The direct `2^20` wheel microtrial equaled both exact routes at
  `13727/16384`.
- Endpoint-label invariance passed.
- Every common-denominator numerator was integral.
- The run used 37,584,896 peak resident bytes and 96.665045 seconds on CPU.
- The independent verifier reproduced every numerical cell and the microtrial
  control.  Its composite verdict remained false because it correctly
  inherited the registered G8 failure.

These checks are diagnostic evidence only.  They do not override the failed
registered verdict.
