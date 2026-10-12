# ASMP-9 v0.16 prior-art gate

## Decision

Do not claim novelty for majorization, Robin-Hood transfers, balanced
reliability allocations, or optimal paired-comparison design.

Relevant anchors:

- El-Neweihi, Proschan, and Sethuraman (1986), optimal allocation in
  parallel-series and series-parallel reliability systems using majorization
  and Schur functions:
  <https://doi.org/10.2307/3214014>.
- Kiefer and Wolfowitz (1960), classical optimal experimental design and
  equivalence-theorem foundations:
  <https://projecteuclid.org/ebooks/berkeley-symposium-on-mathematical-statistics-and-probability/Proceedings-of-the-Fourth-Berkeley-Symposium-on-Mathematical-Statistics-and/chapter/Optimum-Experimental-Designs-V-with-Applications-to-Systematic-and-Rotatable/bsmsp/1200512174>.
- Röttger, Kahle, and Schwabe (2022), optimal discrete-choice and
  Bradley-Terry designs through graph Laplacians:
  <https://arxiv.org/abs/2208.08926>.
- Zou et al. (2026), TRACE, which uses the probability of obtaining both
  successful and failed rollouts as a practical RLVR allocation objective:
  <https://arxiv.org/abs/2606.11119>.

## Surviving contribution

The result sought here is a narrow access-ledger theorem for the exact
conditional quotient introduced in ASMP-9 v0.13:

1. nature adversarially chooses each edge probability inside a symmetric
   interval;
2. the useful event is global cycle-fiber informativeness, not local reward
   contrast on one prompt;
3. nuisance endpoint labels are minimized before the allocation is optimized;
   and
4. a pairwise decomposition proves exact integer maximin balancing.

The theorem may be a specialization of broader reliability-allocation
principles. Its role in the project is to close a stated ASMP-9 sample-access
obligation, not to claim a new general theory of majorization or RL rollout
allocation.
