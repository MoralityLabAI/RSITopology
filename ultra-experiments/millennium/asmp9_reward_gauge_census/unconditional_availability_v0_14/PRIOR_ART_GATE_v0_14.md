# ASMP-9 v0.14 prior-art gate

## Decision

Treat nuisance elimination by conditioning, loss of information at extreme
sufficient statistics, and conditional-test power calculations as classical.
Do not claim new conditional-likelihood, Rasch, Bradley-Terry, or minimax
testing theory.

Primary anchors:

- Andersen, *Asymptotic Properties of Conditional Maximum-likelihood
  Estimators* (1970), conditioning on minimal sufficient statistics to remove
  incidental parameters:
  <https://doi.org/10.1111/j.2517-6161.1970.tb00842.x>.
- Andersen, *A Goodness of Fit Test for the Rasch Model* (1973), conditional
  likelihood-ratio model testing:
  <https://doi.org/10.1007/BF02291180>.
- Pfanzagl, *On the Consistency of Conditional Maximum Likelihood
  Estimators* (1993), including necessary conditions tied to nuisance
  sequences in the Rasch specialization:
  <https://doi.org/10.1007/BF00774782>.
- Diaconis and Sturmfels, *Algebraic Algorithms for Sampling from
  Conditional Distributions* (1998), exact conditional inference and Markov
  bases:
  <https://doi.org/10.1214/aos/1030563990>.
- Sturmfels and Welker, *Commutative Algebra of Statistical Ranking* (2012),
  Bradley-Terry toric models and graph circuits:
  <https://arxiv.org/abs/1101.1597>.
- Makur and Singh, *Minimax Hypothesis Testing for the Bradley-Terry-Luce
  Model* (2024), a materially broader goodness-of-fit theory:
  <https://arxiv.org/abs/2410.08360>.

## Surviving ASMP-9 role

The contribution is an exact access-ledger specialization:

1. extend the v0.13 zero-balance test to every cycle count fiber;
2. give the closed-form probability that the realized fiber is informative;
3. factor unconditional excess power through informative-fiber probability;
   and
4. exhibit a scalar-gradient nuisance family that drives that probability to
   zero without changing cycle circulation.

This is useful because it identifies the extra assumption a future positive
access theorem must expose. It is not presented as new probability theory.
