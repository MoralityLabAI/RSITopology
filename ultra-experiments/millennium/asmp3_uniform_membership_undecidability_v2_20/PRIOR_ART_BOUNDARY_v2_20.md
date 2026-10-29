# ASMP-3 v2.20 prior-art and novelty boundary

## Classical ingredients

No novelty claim is made for any of the following facts:

- the halting problem is undecidable;
- `NONHALT` is not recursively enumerable;
- a computable many-one reduction transfers undecidability and
  non-enumerability;
- binary hypothesis-testing advantage is bounded by total variation;
- randomized post-processing cannot increase total variation; and
- finite zero-sum games admit minimax and linear-programming formulations.

These are standard computability and finite decision-theory tools. The v0.8
convex-hull TV theorem and v1.3 sequence-form bridge likewise package classical
machinery for the ASMP-3 setting rather than claiming new minimax theory.

## Package-specific contribution

The research contribution claimed here is the placement of a NONHALT reduction
inside a source-audited ASMP-3 strict-FIX game while simultaneously preserving
the problem's operational firewalls:

- fixed simultaneous vector messages;
- one genuinely local coordinate query;
- a nonzero complete noise law;
- an efficient honest strategy;
- verifier, transcript, and query costs `polylog(T)`; and
- exact per-depth values on both branches.

The finite/uniform boundary is also made executable: bounded machine
simulation selects an exact finite certificate, while the eventual uniform-gap
property remains undecidable.

## Literature and review boundary

This package is an internal theorem and verification artifact, not a literature
survey or a claim of peer-reviewed originality. A release-grade external claim
would still need:

1. a formal comparison with established undecidability results for interactive
   proof and game-value index sets;
2. independent proof review of the protocol quantifiers and paired-world
   coupling; and
3. an authoritative judgment that the chosen generator representation is the
   parent problem's associated frozen uniform decision family.
