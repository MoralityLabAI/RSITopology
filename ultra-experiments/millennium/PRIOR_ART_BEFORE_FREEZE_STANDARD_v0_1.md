# ASMP prior-art-before-freeze standard v0.1

## Status

Prospective registration rule, effective 2026-07-20. It does not invalidate or
retroactively alter sealed experiments. It applies to every new theorem seed,
experiment seed, or versioned successor that could support a mathematical or
novelty-bearing claim—not only to new top-level ASMP entries.

## Required sequence

Before a claim protocol or runner is frozen, its directory must contain a
versioned prior-art artifact that records:

1. the exact proposed novelty sentence;
2. frozen search strings, date, and sources searched;
3. the strongest positive, negative, and adjacent results found, preferring
   primary sources;
4. a claim-by-claim disposition from
   `{classical, subsumed, partial_extension, candidate_new, ill_posed}`;
5. the surviving non-overlap or application-specific contribution;
6. a hostile-referee attempt to trivialize the claim or locate a stronger
   result; and
7. a conservative external-description sentence.

The registration must bind the prior-art artifact's SHA-256 and must not claim
more novelty than its disposition allows. `candidate_new` means only “no direct
antecedent found in the frozen search,” never “novelty established.”

## Failure behavior

If the prior-art artifact is absent or unbound, the run may proceed only as an
explicitly labelled engineering pilot with no claim-eligible reveal. A later
prior-art audit cannot retroactively make an already-revealed pilot
preregistered.

If the audit finds the theorem classical or subsumed, the artifact may still
be frozen as an instrument, consolidation, replication, counterexample
generator, or application-specific normalization. The protocol and result
must state that status prominently.

## Motivation

ASMP-1 and ASMP-10 independently produced correct executable instruments whose
core rank theorems were classical. Both remained useful after attribution, but
both incurred avoidable post-result novelty audits. This rule moves that cheap
classification step before the expensive freeze-and-run sequence.

