# ASMP-9 v0.15 prior-art gate

## Decision

Treat conditional inference, exact versus unconditional power loss, minimax
paired-comparison estimation, and optimal Bradley-Terry design as established
areas. Do not claim a new general optimal-design or conditional-testing
theory.

Primary anchors:

- Andersen (1970), conditioning on sufficient statistics to eliminate
  nuisance parameters:
  <https://doi.org/10.1111/j.2517-6161.1970.tb00842.x>.
- Tang, Ng, Guo, Chan, and Chan (2006), exact conditional versus exact
  unconditional testing when binary response probabilities are extreme:
  <https://doi.org/10.1080/10629360600569519>.
- Shah et al. (2016), sharp minimax estimation bounds for pairwise-comparison
  models with explicit comparison-graph dependence:
  <https://arxiv.org/abs/1505.01462>.
- Kahle, Röttger, and Schwabe (2020), parameter-dependent optimal
  experimental designs for the Bradley-Terry model:
  <https://arxiv.org/abs/1901.02375>.
- Kiefer and Wolfowitz (1960), the classical equivalence-theorem foundation
  for optimal experimental design:
  <https://projecteuclid.org/ebooks/berkeley-symposium-on-mathematical-statistics-and-probability/Proceedings-of-the-Fourth-Berkeley-Symposium-on-Mathematical-Statistics-and/chapter/Optimum-Experimental-Designs-V-with-Applications-to-Systematic-and-Rotatable/bsmsp/1200512174>.

## Surviving ASMP-9 role

The contribution sought here is narrower:

1. identify the exact probability-interior nuisance that minimizes the
   availability of the v0.13 conditional quotient;
2. replace v0.14's conservative positive bound with a sharp identity;
3. turn that identity into an exact equal-count trial threshold; and
4. keep the stronger total-budget balancing claim separate until proved.

Even if the closed form is a special case of known inequalities, its role is
an access-ledger consolidation rather than a novelty claim.
