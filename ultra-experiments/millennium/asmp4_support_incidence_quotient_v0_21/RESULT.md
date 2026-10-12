# Result v0.21

The active support-incidence signature
`sigma(y)={(s,z,s_next):(y,s_next) in E(s,z)}` defines a canonical finite
quotient for exact support preservation. It is invariant under raw renaming
and duplicate colors, preserves support-zero-error feasibility, and is
idempotent. The quotient observer gives exact semantic read region
`[1+log2(rho(A_sem)),infinity) x [2,infinity)`.

Across all 53,108 v0.17 memoryless relations, 724 are feasible and 260 of those
contain duplicate active signatures. The raw active histogram `20,210,494`
becomes the semantic histogram `64,396,264` for two, three, and four classes.
Independent row-support and column-signature enumerations agree on the full
joint histogram.

The 104 feasible deterministic labeled relations contain no active duplicate
signatures, so the v0.16 partition theorem is unchanged.

This is a rigorous quotient-first response to v0.20, but it is deliberately
not minimal for control. It preserves the full finite event-support object and
does not claim that the original ASMP-4 text mandates this quotient or that it
solves the global nonlinear theorem.

The complete 22-package chain passes all 254 tests in 293.88 seconds.

The v0.22 successor shows that exact support incidence is not control-minimal:
a causal belief-aware encoder can emit only current `q`. The frozen v0.21
exact-support claim remains unchanged.
