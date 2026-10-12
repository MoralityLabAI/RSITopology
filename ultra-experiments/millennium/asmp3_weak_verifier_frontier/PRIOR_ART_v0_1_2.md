# ASMP-3 exchangeable-moment addendum: prior-art boundary

## Classification

The v0.1.2 calculation is a specialization of the classical discrete binomial
moment problem. It is not a new sharp probability inequality.

Boros and Prékopa, *Closed Form Two-Sided Bounds for Probabilities that At
Least r and Exactly r Out of n Events Occur* (1989),
[DOI:10.1287/moor.14.2.317](https://doi.org/10.1287/moor.14.2.317), formulate
primal and dual linear programs using binomial moments and give closed-form
bounds for event-count tails. Their paper builds on Prékopa's LP treatment of
Boole–Bonferroni inequalities and the earlier probability-bound lineage that
includes Dawson–Sankoff and Kwerel.

The observation that pairwise independence does not imply mutual independence
is also classical; examples are commonly associated with Bernstein and earlier
work by Bohlmann. No novelty is claimed for that fact.

## What is specific here

The additive contribution is limited to:

1. specializing the two-binomial-moment LP to the already frozen weak-verifier
   tuple `n=9`, marginal error `1/5`, majority threshold `5`, and admissible
   error `1/20`;
2. emitting exact rational primal and dual witnesses that a repository checker
   can verify without a numerical solver;
3. separating three safety-relevant conclusions: no universally certified
   pass, an underdetermined region, and a universally certified failure region;
   and
4. locating the beta-binomial threshold from v0.1.1 inside that model-free
   exchangeable classification.

The mathematical bounds should be cited to the discrete moment-problem
literature. The safety interpretation and executable specialization may be
presented as this project's contribution.

