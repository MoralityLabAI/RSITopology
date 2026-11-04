# Correlated gauge access v0.39

This additive ASMP-9 successor separates two propositions that v0.38 held
together:

1. reward representatives differ only by a licensed decision-preserving
   gauge transformation; and
2. the mechanism choosing a representative is statistically ancillary for
   the target.

The first does not imply the second.

The module proves the exact half-range leakage radius, tests stochastic
intervention as an information-erasing control, and compares equal-radius
gauge channels as substitutes for a missing target query. It imports the
sealed v0.38 exact primal-dual solver without modifying any v0.38 artifact.

Current state: `registered_confirmation_passed`.

The canonical outcome is [RESULT_v0_39.md](RESULT_v0_39.md). All ten gates
passed on 25 disjoint rows, and the independent verifier reproduced every
mathematical row while revalidating all fifteen sealed inputs.
