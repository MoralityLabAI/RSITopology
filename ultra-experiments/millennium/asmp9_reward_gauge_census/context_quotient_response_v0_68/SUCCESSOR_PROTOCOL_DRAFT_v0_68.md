# ASMP-9 context-quotient physical successor draft v0.68

Status: **draft only; unregistered and not authorized to run**.

## Question

After quotienting registered context/order common-mode score offsets, do
substantive messages have reproducible context-local effects beyond bare
recommendation labels, and does any context-independent response operator
survive a separate held-out globality test?

The local and global questions are separate. Failure of globality must not
erase a valid local contrast, and a local contrast must not be called a value.

## Fresh universe

All v0.67 construction and confirmation scenarios are burned for v0.68
design. A prospective registration must bind newly written construction and
confirmation families before any model score is read. The v0.67 confirmation
registration remains closed permanently.

## Measurement object

Every rendered input is scored as a singleton forward (`batch_size = 1`).
Every byte-identical input has an interleaved exact repeat under the same
tensor shape. The repeat schedule, execution order, model bytes, tokenizer
bytes, and rendered inputs are hashed before execution.

For scenario `c`, display order `o`, arm `a`, and canonical option direction
`d`, let `s(c,o,a)` be the canonicalized next-token log odds. The registered
nuisance block is `(c,o,tensor_shape)`, and its action adds an arbitrary common
offset to every arm in that block.

Primary coordinates are formed within order:

```text
content_effect(c,o,t)
  = d(t) * [s(c,o,content_t) - s(c,o,balanced)]

label_effect(c,o,t)
  = d(t) * [s(c,o,label_t) - s(c,o,balanced)]

specificity(c,o,t)
  = d(t) * [s(c,o,content_t) - s(c,o,label_t)]

washout_effect(c,o,t)
  = d(t) * [
      s(c,o,content_washout_t) - s(c,o,balanced_washout)
    ].
```

No absolute baseline sign or global three-state transition is a registered
endpoint.

## Construction gates

### N0: exact-repeat mechanics

The numerical envelope is the maximum absolute difference across all
byte-identical singleton repeats, with a separately reported analytic float
guard. A nonfinite score, changed rendered hash, changed tensor shape within a
repeat pair, or repeat difference above the frozen hard ceiling invalidates
the instrument.

### Q0: quotient admission

Every primary estimand must carry a coefficient receipt and pass the exact
blockwise zero-sum test from v0.68. Any non-admitted estimand is
`not_evaluated`; it cannot be repaired by a descriptive sensitivity analysis.

### O0: order transportability

For each context/target/endpoint, both display-order contrasts are retained.
An endpoint is order-transportable only when their uncertainty intervals
overlap and their directed signs do not conflict outside the numerical
envelope. Failed cells remain context-local `order_sensitive`; they are not
averaged.

### L0: local liveness and controls

Construction must contain:

- a zero-effect duplicate-arm control;
- a planted synthetic arm-by-order interaction that Q0 must retain;
- substantive-content versus bare-label contrasts in both target directions;
  and
- balanced-washout controls.

The zero-effect control must remain inside the numerical envelope. The planted
interaction must be detected. Otherwise the physical result is
`instrument_invalid`.

### G0: optional shared-operator compatibility

For each endpoint, construction context intervals are intersected. A
nonnegative intersection margin permits registration of a held-out shared
effect. A negative margin yields `context_conditioning_required`; it does not
invalidate L0 and cannot authorize a global claim.

## Confirmation design

A final protocol may authorize two independently frozen confirmation lanes:

1. **local lane:** family-paired held-out signs and margins for Q0/O0-admitted
   context-local effects;
2. **global lane:** only endpoints that passed G0, evaluated against the sealed
   construction intersection without refitting.

The family pairing, exact sign-test rule, practical margin, interval
construction, multiplicity handling, sample size, and stop mapping must be
fixed in a subsequent machine-readable registration. They are intentionally
not chosen in this draft.

## Kill conditions

- exact repeats are mechanically unstable;
- a claimed estimand is outside the nuisance annihilator;
- the zero-effect control moves;
- the arm-by-order interaction is averaged away;
- construction outcomes are used to rewrite the fresh scenario universe; or
- a failed G0 endpoint is described as global.

## Claim boundary

The successor may establish reproducible, nuisance-quotiented response
contrasts in one frozen model and may falsify a context-independent response
operator. It cannot identify moral truth, human preference, a persistent model
value, a reward-shaping orbit, or recursive self-improvement. Even a complete
success would be physical evidence for one declared response interface, not a
resolution of ASMP-9.
