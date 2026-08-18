# ASMP-9 v0.28 prior-art gate

Status: source audit complete for the registered finite access specialization.
Registration is permitted only with novelty disclaimed and every control below
sealed prospectively.

## Owned ingredients

1. Ng, Harada, and Russell (ICML 1999) own potential-based reward shaping and
   policy invariance.
2. Cao, Cohen, and Szpruch, *Identifiability in inverse reinforcement
   learning* (NeurIPS 2021,
   <https://papers.nips.cc/paper/2021/hash/671f0311e2754fcdd37f70a8550379bc-Abstract.html>),
   own major entropy-regularized IRL identifiability and
   multi-environment/multi-discount results.
3. Kim, Garg, Shiragur, and Ermon, *Reward Identification in Inverse
   Reinforcement Learning* (ICML 2021, PMLR 139,
   <https://proceedings.mlr.press/v139/kim21c.html>), own necessary and
   sufficient finite deterministic MaxEnt-MDP identification conditions.
4. Kleine Buening, Villin, and Dimitrakakis, *Environment Design for Inverse
   Reinforcement Learning* (ICML 2024, PMLR 235,
   <https://proceedings.mlr.press/v235/kleine-buening24a.html>), own adaptive
   environment design for reward identification.
5. Skalse et al., *Invariance in Policy Optimisation and Partial
   Identifiability in Reward Learning* (ICML 2023, PMLR 202,
   <https://proceedings.mlr.press/v202/skalse23a.html>), own broad
   reward-learning invariance classifications.
6. Lin and Kulasekera (Biometrika 2007,
   <https://doi.org/10.1093/biomet/asm029>) own unknown-link single-index
   identifiability conditions.
7. Choice-indifference, willingness-to-pay, bisection, and stochastic root
   finding own the calibrated-threshold ingredients catalogued in the v0.26
   prior-art audit.
8. ASMP-9 v0.10 owns this repository's finite-MDP shaping-subspace
   intersection specialization; v0.26-v0.27 own the offset and midpoint
   boundaries.

## Surviving contribution

The only proposed contribution is the access ledger:

```text
homogeneous occupancy interventions + unknown link
  -> positive scale remains invisible;

unknown-value side feature
  -> still homogeneous, still invisible;

externally calibrated numeraire
  -> each occupancy functional becomes localizable;

ker(X)=declared gauge
  -> exact quotient identification.
```

This is a consolidation and bridge between existing results, not a claim to
new inverse-problem, IRL, utility, or experimental-design mathematics.

## Required registered controls

Before freezing:

1. verify the adaptive scaling obstruction formally;
2. include a matched unknown-numeraire control;
3. test full-rank, rank-deficient, and ill-conditioned quotient designs;
4. keep positive scale classified according to the declared decision target;
5. add a concrete finite-MDP occupancy construction rather than testing only
   arbitrary matrices; and
6. register no claim that a real consequence is a stable cardinal numeraire.
