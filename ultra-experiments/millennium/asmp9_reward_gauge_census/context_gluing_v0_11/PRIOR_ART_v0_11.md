# ASMP-9 v0.11 prior-art boundary

## Primary anchors

1. Jiang, Lim, Yao, and Ye, *Statistical ranking and combinatorial Hodge
   theory*, Mathematical Programming 127 (2011), 203-244.

   Pairwise rankings as graph edge flows, global rankings as gradients, and
   cyclic inconsistency as the non-gradient component are established
   HodgeRank machinery. The one-context part of v0.11 is directly subsumed.

2. Abramsky and Brandenburger, *The sheaf-theoretic structure of non-locality
   and contextuality*, New Journal of Physics 13 (2011).

   Local compatibility versus existence of a global section is a general
   classical framework. The v0.11 theorem is only an elementary real-valued
   graph specialization; it makes no quantum-contextuality claim.

3. Tversky and Simonson, *Context-dependent preferences*, Management Science
   39 (1993), 1179-1189.

   Context-dependent value and preference reversals are established
   behavioral phenomena. The present finite cardinal model is an instrument,
   not a model of those experiments.

4. Skalse, Farrugia-Roberts, Russell, Abate, and Gleave, *Invariance in policy
   optimisation and partial identifiability in reward learning*, ICML 2023.

   Source-specific reward invariances and partial identifiability are already
   characterized for major reward-learning observation classes.

5. Skalse and Abate, *Partial identifiability and misspecification in inverse
   reinforcement learning*, Artificial Intelligence (2026; arXiv
   `2411.15951`).

   The general distinction between invariance and misspecification is prior
   art. Version v0.11 only gives an exact finite gluing specialization.

## Contribution boundary

The candidate contribution is not a new cohomology theorem. It is:

- a problem-ID-bound exact access grammar for context/history-labelled
  preference data;
- the explicit quotient
  `beta_1(M)-sum_c beta_1(G_c)` as the number of mixed-context checks;
- a total liveness rule that reports `shared_scalar_forced_by_design` at
  quotient dimension zero instead of counting it as a live test;
- exact minimal witnesses and matched gluable controls; and
- a prospectively gated finite census suitable for later finite-sample
  extension.
