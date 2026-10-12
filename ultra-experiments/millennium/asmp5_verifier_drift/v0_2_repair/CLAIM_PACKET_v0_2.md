# ASMP-5 verifier-drift repair claim packet v0.2

## Purpose

Version 0.1 stopped at its frozen wall-time cap and produced no scientific
result. Version 0.2 preserves the same 36-cell finite universe and primary
hypothesis while replacing duplicate-token expansion and streamed universe
hashing with an exact quotient and closed-form universe receipts.

## Frozen claim

At width six and checker-mutation radius one or two, at least one of
`self_endorsement` or `pairwise_agreement` admits an adaptive certified unsafe
path of depth at most four while the matched frozen-root arm has no unsafe
reachable state through depth eight. `root_refinement` must remove the unsafe
path and retain an eight-step chain through nine distinct safe behavior
vectors.

Every arm stores the same proposed successor checker and sees the same
candidate edge IDs. Only the identity of the active checker differs.

## Exact optimization lemma

Proof tokens are neither stored in state nor consumed. The certificate
predicate reads a token only through its registered proof class. Replacing all
tokens of one class by the least token of that class therefore preserves every
reachable state and minimum unsafe depth. A test against the unquotiented v0.1
implementation on disjoint fixtures is mandatory before registration.

## Claim boundary

A pass is one exact finite counterexample to unrestricted successor-checker
self-endorsement and one bounded positive control for a frozen-root refinement.
It is not an infinite tiling theorem, a result about learned evaluators, or
evidence of recursive self-improvement.
