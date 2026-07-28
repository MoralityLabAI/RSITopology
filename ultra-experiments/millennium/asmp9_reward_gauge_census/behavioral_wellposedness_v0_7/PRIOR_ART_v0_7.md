# ASMP-9 behavioral well-posedness: prior-art boundary

## Primary anchors

1. Jiang, Lim, Yao, and Ye, *Statistical ranking and combinatorial Hodge
   theory*, Mathematical Programming 127 (2011), 203-244,
   DOI `10.1007/s10107-010-0419-x`.

   Pairwise rankings as graph edge flows, their least-squares projection onto
   gradient flows, and the local/global cyclic decomposition are HodgeRank.
   The cycle-consistency theorem and residual used here are a direct finite
   specialization.

2. Bradley and Terry, *Rank analysis of incomplete block designs: I. The method
   of paired comparisons*, Biometrika 39 (1952), 324-345.

   The scalar log-odds model is classical. This experiment does not claim a new
   paired-comparison model or estimator.

3. Skalse, Farrugia-Roberts, Russell, Abate, and Gleave, *Invariance in Policy
   Optimisation and Partial Identifiability in Reward Learning*, ICML 2022,
   arXiv `2203.07475`.

   Their work characterizes infinite-data invariances of expert
   demonstrations, trajectory comparisons, and other reward-learning data
   sources. ASMP-9 must not present generic partial identifiability as new.

4. Cao, Cohen, and Szpruch, *Identifiability in inverse reinforcement
   learning*, NeurIPS 2021.

   They characterize rewards consistent with entropy-regularized optimal
   policies and give positive identification results from multiple discounts
   or sufficiently different transition laws. The one-state threshold model
   here is a deliberately smaller access-complexity calibration, not a
   competing general IRL theorem.

5. Skalse and Abate, *Partial Identifiability and Misspecification in Inverse
   Reinforcement Learning*, arXiv `2411.15951`.

   Their framework already provides broad necessary and sufficient
   misspecification results. The present cycle certificate is a transparent
   graph-specialized no-go, not a general misspecification theory.

## Exact contribution boundary

The durable ASMP-9 contribution is the access ledger:

```text
reconstruct a scalar under coherence promise: |V|-c queries;
certify coherence only:                       all non-bridge edges;
reconstruct and certify the full law:         |E| queries;
post-forest model-checking surcharge:         beta_1 queries.
```

The deterministic-policy arm separately records the exact adaptive and
nonadaptive approximation radii in a minimal environment-intervention model.
Both are classical rank/search facts packaged as a prospective instrument.

No novelty claim is made for HodgeRank, Bradley-Terry identifiability,
comparison search, reward ambiguity, or IRL misspecification.
