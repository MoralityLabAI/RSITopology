# ASMP-9 v0.10 prior-art boundary

## Primary anchors

1. Ng, Harada, and Russell, *Policy invariance under reward transformations:
   theory and application to reward shaping*, ICML 1999, 278-287.

   Potential-based reward shaping and its policy invariance are classical.

2. Cao, Cohen, and Szpruch, *Identifiability in inverse reinforcement
   learning*, NeurIPS 2021, arXiv `2106.03498`.

   This is the load-bearing adjacent result. It characterizes rewards inducing
   a given entropy-regularized policy and proves recovery up to a constant
   from two distinct discounts or sufficiently different environments. ASMP-9
   v0.10 does not claim either fact as new.

3. Skalse, Farrugia-Roberts, Russell, Abate, and Gleave, *Invariance in policy
   optimisation and partial identifiability in reward learning*, ICML 2022,
   arXiv `2203.07475`.

   The invariance classes of policies, demonstrations, and trajectory
   comparisons are substantially characterized there. A finite census cannot
   replace that general theory.

4. Kim, Garg, Shiragur, and Ermon, *Reward identification in inverse
   reinforcement learning*, ICML 2021, PMLR 139, 5496-5505.

   Environment design for reward identification is established prior art.

## Exact contribution boundary

The registered contribution is an executable specialization:

- exact shaping-subspace intersection dimensions;
- a component-count formula for a self-loop reference plus deterministic
  transition interventions;
- an exact minimum of two environments or discounts in the structured cyclic
  family;
- a matched deterministic-policy nonidentifiability witness; and
- a direct one-step trajectory-comparison control.

These are theorem-seed and access-audit artifacts, not new general IRL
identifiability theory.
