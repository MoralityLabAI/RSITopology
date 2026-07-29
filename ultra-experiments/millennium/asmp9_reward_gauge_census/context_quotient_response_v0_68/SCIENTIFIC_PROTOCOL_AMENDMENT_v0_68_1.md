# ASMP-9 context-quotient protocol amendment v0.68.1

Status: **frozen prereveal amendment; execution unregistered and unauthorized**.

This amendment is additive. It does not edit or erase
`SCIENTIFIC_PROTOCOL_v0_68.md` or `protocol_v0_68.json`.

## Reason for amendment

Version v0.68 called the upper-tail rank of the observed scenario mean among
all `2^12` scenario-level sign inversions an "exact randomization p-value."
That interpretation is not justified by the frozen design:

- the twelve scenarios are a fixed finite registry, not an iid sample from a
  declared population;
- content and label arms are both evaluated rather than randomly assigned to
  experimental units; and
- no symmetric scenario-error law was registered.

The `2^12` enumeration is exact as an algebraic sign-orbit sensitivity
calculation. It is not a design-based or model-based p-value. No model outcome
has been read, so the correction is made before execution registration.

## Replacement local gate

The v0.68 `N0`, `Q0`, `S0`, score universe, endpoint epsilon, scenario
definition, construction/confirmation split, and global `G0` gate are
unchanged.

`L0` is replaced by a finite-registry criterion:

1. at least 10 of 12 scenarios have directed content-minus-label specificity
   strictly above endpoint epsilon for both targets and both display orders;
2. the median scenario worst-direction specificity is strictly above endpoint
   epsilon; and
3. the mean of the twelve scenario-mean specificities is strictly above
   endpoint epsilon.

The third condition prevents two sufficiently adverse scenarios from being
hidden by the coverage count. The `2^12` sign-orbit upper-tail fraction is
still reported as descriptive sensitivity, but it has no probability
interpretation and no gate consumes it.

## Claim change

The local verdict is renamed conceptually to:

```text
local_response_family_established_on_frozen_registry
```

It means the deterministic, nuisance-quotiented response contrasts clear the
registered practical margins on this finite registry. It is not a population
inference statement. Confirmation is a second disjoint finite registry, not a
confidence sample.

## Integrity rule

Every execution registration must hash both the immutable v0.68 protocol and
the v0.68.1 machine-readable amendment. It must bind the amended analyzer and
prereveal validator. A registration that binds only v0.68 is not authorized
after this amendment.
