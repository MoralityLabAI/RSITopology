# ASMP-9 unknown-link frontier: prior-art boundary

## Primary anchors

1. Bradley and Terry, *Rank analysis of incomplete block designs: I. The method
   of paired comparisons*, Biometrika 39 (1952), 324-345.

   The known logistic-link model and its scale/location conventions are
   classical.

2. Lin and Kulasekera, *Identifiability of single-index models and
   additive-index models*, Biometrika 94 (2007), 496-501,
   DOI `10.1093/biomet/asm029`.

   Single-index identifiability with an unknown link depends on support and
   normalization assumptions. The finite-design counterexample here does not
   contradict positive results under rich covariate support.

3. Balabdaoui, Durot, and Jankowski, *Least squares estimation in the monotone
   single index model*, arXiv `1610.06026`.

   Estimation with an unknown monotone ridge function is an established
   semiparametric problem. ASMP-9 does not claim the nuisance-link issue or its
   normalization as new.

4. Skalse, Farrugia-Roberts, Russell, Abate, and Gleave, *Invariance in Policy
   Optimisation and Partial Identifiability in Reward Learning*, ICML 2022,
   arXiv `2203.07475`.

   Reward-learning data sources already have extensively characterized
   infinite-data invariances. The present result is only a finite
   pairwise-design access obstruction.

5. Skalse and Abate, *Partial Identifiability and Misspecification in Inverse
   Reinforcement Learning*, arXiv `2411.15951`.

   Unknown or wrong behavioral models are already treated in a broad
   misspecification framework. The explicit rational three-item witness is a
   transparent specialization, not a replacement for that theory.

## Exact contribution boundary

The ASMP-9 contribution is the separation:

```text
known link + unknown positive temperature
  -> translation and positive-scale gauge only;

unknown unrestricted monotone link on a finite comparison design
  -> a larger labelled-difference-order equivalence class.
```

The exact rational witness and prospective instrument make the distinction
auditable. No novelty claim is made for monotone single-index
nonidentifiability.
