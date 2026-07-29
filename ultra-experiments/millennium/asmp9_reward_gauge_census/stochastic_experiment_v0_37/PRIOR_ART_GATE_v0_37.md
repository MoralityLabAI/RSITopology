# Prior-art gate for ASMP-9 stochastic experiment v0.37

## Status

Open development audit. This file must be completed before any v0.37 protocol
is frozen.

## Results that already own the general language

- David Blackwell, **Equivalent Comparisons of Experiments**, *Annals of
  Mathematical Statistics* 24(2), 1953:
  <https://doi.org/10.1214/aoms/1177729032>.
  The comparison of experiments by attainable risk and by stochastic
  simulation is classical.
- Lucien Le Cam's deficiency theory supplies approximate comparison of
  statistical experiments. The standard book-length reference is *Asymptotic
  Methods in Statistical Decision Theory* (1986).
- Erik Torgersen, *Comparison of Statistical Experiments* (1991), develops
  sufficiency, randomization, deficiency, and experiment equivalence:
  <https://doi.org/10.1017/CBO9780511666353>.
- Claude Shannon, **The Zero Error Capacity of a Noisy Channel** (1956),
  supplies the confusability-graph side:
  <https://doi.org/10.1109/TIT.1956.1056798>.
- Skalse et al., **Invariance in Policy Optimisation and Partial
  Identifiability in Reward Learning**:
  <https://arxiv.org/abs/2203.07475>.
- Skalse and Abate, **Partial Identifiability and Misspecification in Inverse
  Reinforcement Learning**:
  <https://arxiv.org/abs/2411.15951>.

## Subsumption posture

The following are not candidate-new claims:

- Blackwell dominance as a decision-uniform comparison;
- simulation/garbling characterizations in the classical finite experiment;
- Le Cam deficiency as an approximate risk-comparison device;
- zero-error confusability graphs; or
- the fact that equal observational laws define equivalence classes.

The proposed contribution is narrower:

1. make the ASMP-9 access object explicit as a compound statistical
   experiment;
2. keep exact fibers, pairwise confusability, component decision quotients,
   and bounded-risk deficiency separate;
3. freeze shared-versus-reset nuisance coupling as part of the access model;
   and
4. build an exact rational instrument that exposes when a zero-error quotient
   is insufficient for bounded-risk safety decisions.

## Required searches before registration

- Blackwell comparison for sets or classes of experiments;
- robust and minimax deficiency for compound experiments;
- randomization criteria under nuisance parameters;
- deficiency under total-variation contamination neighborhoods;
- inverse-reinforcement-learning results stated directly in decision-risk or
  experiment-comparison language; and
- exact finite LP formulations and dual certificates for deficiency.

If the robust-deficiency lemma or the proposed S0 separation is already a
direct named corollary with the same compound semantics, v0.37 must be framed
as an instrument consolidation rather than a theorem contribution.
