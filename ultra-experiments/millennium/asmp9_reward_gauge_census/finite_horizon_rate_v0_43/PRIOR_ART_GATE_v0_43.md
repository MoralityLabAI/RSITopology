# ASMP-9 v0.43 prior-art gate

## Disposition

The mathematical ingredients in v0.43 are classical. The candidate
contribution is their decision-relative composition against the exact
finite-horizon ASMP-9 access object from v0.41-v0.42.1. No claim is made to a
new Pinsker inequality, simulation lemma, comparison-of-experiments theorem,
two-point method, or Bernoulli concentration inequality.

## Primary and load-bearing sources

1. **Blackwell comparison.** David Blackwell, “Comparison of Experiments,”
   *Proceedings of the Second Berkeley Symposium on Mathematical Statistics
   and Probability* (1951), pp. 93-102,
   <https://digicoll.lib.berkeley.edu/record/112749>.
   Blackwell comparison supplies the decision-problem ordering beneath the
   risk-polytope object.
2. **Deficiency and decision-relative comparison.** Erik Torgersen,
   *Comparison of Statistical Experiments* (Cambridge University Press,
   1991), especially the deficiency chapter,
   <https://doi.org/10.1017/CBO9780511666353.007>.
   The repository specializes deficiency to frozen finite loss types; it does
   not introduce the general concept.
3. **Finite-horizon simulation.** Michael Kearns and Satinder Singh,
   “Near-Optimal Reinforcement Learning in Polynomial Time,” *Machine
   Learning* 49 (2002), 209-232,
   <https://www.cis.upenn.edu/~mkearns/papers/KearnsSinghE3.pdf>.
   Their simulation lemma is the closest RL-side ancestor of propagating
   one-step model error through a horizon.
4. **Empirical-distribution concentration.** Tsachy Weissman, Erik
   Ordentlich, Gadiel Seroussi, Sergio Verdú, and Marcelo J. Weinberger,
   “Inequalities for the L1 Deviation of the Empirical Distribution,”
   HPL-2003-97R1 (2003),
   <https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/2003/HPL-2003-97R1.pdf>.
   This is the distribution-free TV ingredient used by v0.42.1, not by the
   sharper sentinel block estimator.
5. **Two-point minimax reasoning.** Jean Bretagnolle and Catherine Huber,
   “Estimation des densités: risque minimax,” *Zeitschrift für
   Wahrscheinlichkeitstheorie und Verwandte Gebiete* 47 (1979), 119-137,
   <https://doi.org/10.1007/BF00535278>.
   Le Cam/Bretagnolle-Huber two-point arguments and Pinsker conversion are
   classical; v0.43 only gives an exact rational witness for this access
   problem.

## Subsumption check

The following are already known in broader form:

- risk comparison by experiment deficiency;
- KL chain rules for adaptive transcripts;
- Pinsker conversion from KL to total variation;
- finite-horizon simulation bounds;
- two-point minimax lower bounds; and
- Hoeffding concentration for Bernoulli block indicators.

The surviving repository-specific question is narrower:

> Is the `O(h^2/g^2)` sample floor produced by the v0.42.1
> TV-then-union-bound certificate intrinsic to finite-horizon
> decision-relative access, or does the exact Bellman geometry admit a
> smaller sharp horizon exponent?

The v0.43 theorem answers this on one fully characterized sentinel family and
rules out the particular KL-regular lower-bound witness proposed in the v0.42
obligation matrix. It does not claim a minimax theorem over all finite adaptive
experiments.

## Frozen novelty sentence

> ASMP-9 v0.43 composes the KL chain rule, Pinsker, an exact binary
> deficiency formula, a two-point chi-square certificate, and a block
> estimator to show that the quadratic horizon factor in v0.42.1 is not
> intrinsic on the registered sentinel family: its sharp sample exponent is
> linear in horizon, up to confidence constants.

This is a consolidation and correction inside the ASMP-9 access ledger, not a
new general result in information theory.
