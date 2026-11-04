# ASMP-3 machine-grammar report v0.3

## Result

The missing machine layer is now implemented as a versioned successor
proposal. `ASMP-3-MACHINE-v0.3` freezes:

- canonical byte serialization;
- duplicate/alias/float/malformed rejection;
- a typed universal register IR;
- exact bit-cost gas and fault semantics;
- a total standard Turing-machine numbering and bounded simulator;
- all environment, noise, information, interface, payoff, and `Refute`
  signatures;
- distinct executable FIX and finite-catalog ADM quantifiers; and
- the exact asymptotic constant-gap membership predicate.

The v2.21 NONHALT family compiles into canonical instances in both modes. If
the proposal is adopted, uniform membership is therefore literally undecidable
for the successor; the earlier representation objection disappears.

## Machine evidence

The producer compiles seven machine indices into FIX and ADM, round-trips all
14 byte strings, and emits committed e=17 examples. It rejects pretty JSON,
trailing newlines, BOMs, duplicate keys, and floats. The reference evaluator
checks a gas-metered Minsky countdown plus halting, looping, and invalid
`U_TM_v1` machines. The independent verifier reconstructs compiler bytes and
runtime receipts without importing the producer.

## Scope judgment

This work closes a technical ambiguity but cannot confer normative authority
on itself. V0.3 is deliberately a successor rather than an in-place edit to
v0.1. The current safe status is:

```text
machine grammar = implemented and independently checkable
v2.21 reduction = valid in grammar-defined FIX and ADM sets
successor uniform membership = internally resolved as undecidable
authoritative adoption = pending
external reproductions = 0/2
```

## Verification

```text
producer gates = 11/11
clean-room checks = 11/11
focused tests = 26/26
full ASMP-3 regression = 512/512 across 43 test files
standalone ASMP-3 checkers = 39/39
external expert gate = 0/2; complete=false
```
