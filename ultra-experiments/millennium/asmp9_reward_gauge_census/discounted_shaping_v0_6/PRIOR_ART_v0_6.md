# Discounted-shaping quotient: prior-art boundary

## Disposition

The rank theorem is a direct specialization of gain-graph incidence-matrix
theory. The telescoping identity is standard potential-based reward shaping.
Neither is claimed novel.

## Primary anchors

- Ng, Harada, and Russell (1999) establish policy invariance for discounted
  potential shaping `gamma Phi(s')-Phi(s)`.
- Jenner, van Hoof, and Gleave, *Calculus on MDPs: Potential Shaping as a
  Gradient* (2022), formulate potential shaping with discrete differential
  operators and strengthen uniqueness statements for universally
  policy-invariant additive transformations.
- Skalse et al. (2022) characterize reward invariances induced by multiple
  reward-learning data sources.
- Kim et al., *Reward Identification in Inverse Reinforcement Learning*
  (ICML 2021), give necessary and sufficient identifiability conditions for
  deterministic MaxEnt IRL settings.
- Zaslavsky, *Biased graphs. I. Bias, balance, and gains* (1989), develops the
  gain/balance framework underlying the incidence rank
  `|V|-number_of_balanced_components`.
- Rybnikov and Zaslavsky (2002) give further criteria for balance in Abelian
  gain graphs.

Primary links:

- <https://www.cs.utexas.edu/~shivaram/readings/b2hd-NgHR1999.html>
- <https://arxiv.org/abs/2208.09570>
- <https://arxiv.org/abs/2203.07475>
- <https://proceedings.mlr.press/v139/kim21c.html>
- <https://doi.org/10.1016/0095-8956(89)90063-4>
- <https://arxiv.org/abs/math/0210052>

## Residual contribution

The ASMP-9 contribution is access bookkeeping:

1. replace the ordinary cycle quotient with the correct discounted gain-graph
   quotient;
2. make the balanced-component rank loss explicit;
3. identify boundary-signature matching as the exact condition for
   shaping-invariant finite-trajectory comparisons; and
4. prevent the earlier exact-loop census from being transferred to discounted
   preference access.

The theorem is useful because it removes an invalid access grammar, not because
gain graphs or shaping telescoping are new.

## Deliberate omissions

- no policy or demonstration likelihood;
- no transition-redistribution invariance;
- no entropy-regularized policy equivalence;
- no stochastic or unknown discount factor;
- no finite-sample response model; and
- no inconsistent demonstrator.
