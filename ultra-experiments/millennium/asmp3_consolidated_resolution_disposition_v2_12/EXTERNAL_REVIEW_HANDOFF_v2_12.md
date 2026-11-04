# ASMP-3 external-review handoff v2.12

## Requested review tracks

Two independent teams are still required:

1. complexity, interactive-game semantics, and resource lower bounds;
2. probability, semantic-noise models, and converse validity.

At least one team must independently implement a checker rather than wrapping
the repository verifier.

## Primary adjudication questions

1. Does v0.7 constitute a legal frozen-interface counterexample to the literal
   sufficiency direction while retaining efficient honesty and nonzero noise?
2. Does v2.5's unchanged protocol with singleton, padded, and empty nonbinding
   `Refute` relations refute literal necessity?
3. Is v2.10's online extractor valid against one-shot stateful strategies
   without replay, given public noisy-trace binding and candidate-only `H`?
4. Does v2.11 correctly prove black-box Las Vegas necessity of each six-clause
   online premise, especially the zero-success result under positive decoy mass?
5. Is the v2.12 disposition appropriately limited—literal iff refuted,
   repaired subclass minimal, unrestricted classification unproved?

## Minimum independent reproduction

An adequate checker should independently:

- reconstruct the v0.7 total-variation optimum;
- verify the v2.5 nonbinding-`Refute` dimension separation;
- enumerate or otherwise prove v2.10's zero-invalid online extraction property;
- derive the v2.11 observation partitions, `k/N` probe frontier, and sharp
  `max(0,1-s-delta)` construction; and
- confirm the five unresolved blockers without treating repository-generated
  simulated reviews as external receipts.

## Receipt requirements

Record attributable identity, expertise, affiliation, conflict status, exact
commit, commands, independent implementation provenance, findings, and signed
or otherwise auditable evidence.  Until two qualifying receipts exist, the
external completion gate remains false.
