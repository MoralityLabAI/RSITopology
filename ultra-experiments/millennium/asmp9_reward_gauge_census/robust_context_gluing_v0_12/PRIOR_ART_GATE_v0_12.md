# ASMP-9 v0.12 prior-art gate

## Decision

Do **not** freeze a generic “access lattice” theorem as the v0.12 result.

For any family of observation maps, adding an observation intersects
observational equivalence relations. In a finite linear model, this becomes
kernel intersection and row-space addition. Those statements are elementary
partition/subspace-lattice facts. More importantly, the reward-learning
application is already substantially organized by invariances:

- Skalse et al., [*Invariance in Policy Optimisation and Partial
  Identifiability in Reward Learning*](https://arxiv.org/abs/2203.07475),
  explicitly unify reward-learning data sources and downstream tasks through
  their invariances.
- Cao, Cohen, and Szpruch,
  [*Identifiability in inverse reinforcement
  learning*](https://arxiv.org/abs/2106.03498), give necessary and sufficient
  identifiability conditions in important entropy-regularized finite-MDP
  settings.
- Blackwell's [comparison of
  experiments](https://projecteuclid.org/euclid.bsmsp/1200500222) is the
  classical ordering of statistical access by decision-theoretic
  informativeness.

An implementation that merely stacks the already solved ASMP-9 access maps
would be a useful index, not a new mathematical result.

## Surviving target

Version v0.11 is exact and noiseless. The next load-bearing question is:

> How far is an observed context-labelled flow from the context-local scalar
> model and from the shared-scalar model, and which admissible mixed-cycle
> queries minimize worst-case error amplification?

This target sits inside classical nested linear-model geometry and optimal
experimental design. HodgeRank already separates gradient and cyclic
components for noisy ranking data:

- Jiang, Lim, Yao, and Ye, [*Statistical ranking and combinatorial Hodge
  theory*](https://web.stanford.edu/~yyye/hodgeRank2011.pdf).

Minimum cycle bases and E-optimal design are also established subjects. No
novelty is claimed for orthogonal projection, Pythagorean decomposition,
singular-value conditioning, or minimum cycle bases.

The candidate ASMP-9 contribution is narrower:

1. split error into **within-context non-scalarity** and **cross-context
   non-gluing** for the exact v0.11 access grammar;
2. prove the exact feasibility radius under a declared norm;
3. separate query count (`q`) from robust conditioning (`sigma_min`);
4. give matching lower and upper bounds for arbitrary normalized linear
   mixed-cycle queries; and
5. census whether shortest simple-cycle bases are also robustly optimal, or
   provide exact finite counterexamples.

This is an instrument theorem and access-design result, not new Hodge theory
or a general solution to inverse reinforcement learning.
