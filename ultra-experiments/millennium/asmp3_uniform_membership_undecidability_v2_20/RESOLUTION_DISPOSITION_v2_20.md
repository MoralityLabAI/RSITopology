# ASMP-3 resolution disposition v2.20

## Decision

V2.20 replaces the unsuccessful semantic-impossibility route with a genuine
mathematical obstruction:

```text
arbitrary computable strict-FIX generators
  -> uniform constant-gap membership is undecidable
  -> positive membership is not recursively enumerable
```

This resolves the registered `WV-FIX-UCOMP` decision problem. It does not yet
license the unqualified sentence “ASMP-3 is resolved,” because v0.1 never says
which task-family descriptions form its associated uniform decision family.

## What changed after the v2.19 reassessment

The attached critique of v2.18 was correct on the decisive point: admitting
both `FIX` and `ADM` had not been semantically justified, so the conditional
no-singleton-selector lemma was not an impossibility result. V2.20 does not use
that premise. It adopts the conservative strict-freeze reading and proves a
standard many-one reduction with an exact game value on both sides.

The remaining block is therefore narrower and explicit. It is no longer “we
do not know how to classify the games.” It is:

> Does the parent problem quantify over arbitrary computable generators, or
> over a narrower effectively presented family with additional structure?

## Stop rule for this lane

Further enumeration of bounded games cannot settle that representation
question. The current lane should stop after release verification unless one
of the following becomes available:

1. an authoritative amendment freezing the parent representation;
2. a proof that the canonical language necessarily contains the registered
   generator class;
3. a reduction from the registered class into a different authoritative
   parent encoding; or
4. external review accepting or rejecting the registered class as the
   associated frozen uniform decision family.

If arbitrary computable uniform generators are accepted, v2.20 is a candidate
negative resolution under the source's explicit undecidability rule. If a
narrower representation is chosen, this package remains a sharp boundary
theorem and the restricted decision problem must be studied separately.

## Prohibited overclaims

Do not state that:

- every formulation of weak verification is undecidable;
- no mathematical characterization exists;
- the five positive-resolution requirements have all been met globally;
- the `ADM` class is covered; or
- external acceptance has been obtained.
