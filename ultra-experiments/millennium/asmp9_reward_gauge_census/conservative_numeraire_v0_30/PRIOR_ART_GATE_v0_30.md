# ASMP-9 v0.30 prior-art gate

Status: development source audit. Registration is not yet authorized.

## Owned ingredients

1. Luce and Tukey, *Simultaneous Conjoint Measurement: A New Type of
   Fundamental Measurement* (Journal of Mathematical Psychology 1, 1964,
   <https://doi.org/10.1016/0022-2496(64)90015-X>), and Krantz, Luce, Suppes,
   and Tversky, *Foundations of Measurement, Volume I* (1971), own the
   additive-conjoint and scale-uniqueness foundations.
2. Ng, Harada, and Russell, *Policy invariance under reward transformations*
   (ICML 1999), own the potential-shaping policy-invariance boundary.
3. Dietterich, Trimponias, and Chen, *Discovering and Removing Exogenous State
   Variables and Rewards for Reinforcement Learning* (ICML 2018, PMLR 80,
   <https://proceedings.mlr.press/v80/dietterich18a.html>), formalize
   exogenous/endogenous MDP and reward decomposition.
4. Skalse, Farrugia-Roberts, Russell, Abate, and Gleave, *Invariance in Policy
   Optimisation and Partial Identifiability in Reward Learning* (ICML 2023,
   PMLR 202, <https://proceedings.mlr.press/v202/skalse23a.html>), own the
   data-source/downstream-task invariance comparison.
5. Kleine Buening, Villin, and Dimitrakakis, *Environment Design for Inverse
   Reinforcement Learning* (ICML 2024, PMLR 235,
   <https://proceedings.mlr.press/v235/kleine-buening24a.html>), own adaptive
   environment design for reward identification.
6. ASMP-9 v0.28 owns this repository's homogeneous-scale obstruction and
   calibrated-offset theorem. Version v0.29 owns the quotient-to-decision
   handoff.
7. Finite rectangular additivity, matrix rank, triangle inequality, and
   indistinguishable-model arguments own the proofs proposed here.

The registered scalar table is strictly stronger access than an ordinal
preference relation. Luce-Tukey-style axioms address when an additive cardinal
representation can be constructed from qualitative comparisons; v0.30 assumes
the scalar arguments are already available and only checks their finite
rectangular factorization. It therefore does not improve the classical
representation theorem.

## Surviving contribution

The proposed contribution is only a conservative-access ledger:

```text
same base mechanics at every consequence level
  -> base policy laws and occupancies are preserved;

complete anchored rectangular calibration
  -> the consequence is a known additive offset;

mechanics plus calibration
  -> the v0.28 threshold operation is semantically eligible;

mechanics without semantic evidence
  -> the coefficient is unidentifiable;

epsilon cell residual
  -> at most 2 epsilon two-sided offset bias.
```

This is a consolidation and executable gate, not a new result in MDP
decomposition, conjoint measurement, IRL, or reward invariance.

## Required controls before registration

1. independently perturb horizon, policy feasibility, transition law, and
   target feature map;
2. separate calibrated additivity, separable unknown scale, and
   context-interacting consequence values;
3. make incomplete semantic coverage unavailable rather than favorable;
4. certify the `m(n-1)` constraint rank and one omission witness per
   constraint;
5. attain the `2 epsilon` approximate bound;
6. verify the unknown-coefficient scale coupling over a complete response
   grid; and
7. forbid any claim that structural MDP checks establish a real consequence's
   cardinal utility.
