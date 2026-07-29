# ASMP-9 v0.28 prior-art gate

Status: development-only. Complete the source audit before registration.

## Owned ingredients

1. Ng, Harada, and Russell (ICML 1999) own potential-based reward shaping and
   policy invariance.
2. Cao, Cohen, and Szpruch (NeurIPS 2021, arXiv `2106.03498`) own major
   entropy-regularized IRL identifiability and multi-environment results.
3. Kim, Garg, Shiragur, and Ermon (ICML 2021, PMLR 139) own environment design
   for reward identification.
4. Skalse et al. (ICML 2022, arXiv `2203.07475`) own broad reward-learning
   invariance classifications.
5. Lin and Kulasekera (Biometrika 2007,
   <https://doi.org/10.1093/biomet/asm029>) own unknown-link single-index
   identifiability conditions.
6. Choice-indifference, willingness-to-pay, bisection, and stochastic root
   finding own the calibrated-threshold ingredients catalogued in the v0.26
   prior-art audit.
7. ASMP-9 v0.10 owns this repository's finite-MDP shaping-subspace
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

## Registration blockers

Before freezing:

1. verify the adaptive scaling obstruction formally;
2. include a matched unknown-numeraire control;
3. test full-rank, rank-deficient, and ill-conditioned quotient designs;
4. keep positive scale classified according to the declared decision target;
5. add a concrete finite-MDP occupancy construction rather than testing only
   arbitrary matrices; and
6. register no claim that a real consequence is a stable cardinal numeraire.

