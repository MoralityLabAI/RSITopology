# ASMP-9 v0.29 prior-art gate

Status: development source audit. Registration is not yet authorized.

## Owned ingredients

1. Abbeel and Ng, *Apprenticeship Learning via Inverse Reinforcement Learning*
   (ICML 2004, <https://doi.org/10.1145/1015330.1015430>), own the classical
   feature-expectation route from linear reward uncertainty to policy
   performance.
2. Skalse, Farrugia-Roberts, Russell, Abate, and Gleave, *Invariance in Policy
   Optimisation and Partial Identifiability in Reward Learning* (ICML 2023,
   PMLR 202, <https://proceedings.mlr.press/v202/skalse23a.html>), explicitly
   own the comparison between data-source invariances and downstream-task
   invariances.
3. Kim, Garg, Shiragur, and Ermon, *Reward Identification in Inverse
   Reinforcement Learning* (ICML 2021, PMLR 139,
   <https://proceedings.mlr.press/v139/kim21c.html>), own finite deterministic
   MDP reward-identification criteria and reward equivalence classes.
4. Damiani, Manganini, Metelli, and Restelli, *Balancing Sample Efficiency and
   Suboptimality in Inverse Reinforcement Learning* (ICML 2022, PMLR 162,
   <https://proceedings.mlr.press/v162/damiani22a.html>), own an explicit
   reward-estimation versus learned-policy suboptimality treatment.
5. Zhao, Wang, and Bai, *Is Inverse Reinforcement Learning Harder than Standard
   Reinforcement Learning?* (ICML 2024, PMLR 235,
   <https://proceedings.mlr.press/v235/zhao24m.html>), own modern finite-sample
   IRL guarantees in strong downstream metrics.
6. Cauchy-Schwarz, support-function bounds, quotient norms, and robust argmax
   margins own the mathematical proof.
7. ASMP-9 v0.28 owns this repository's calibrated occupancy-error and quotient
   spectral-floor handoff.

## Surviving contribution

The proposed v0.29 contribution is only a program-level decision ledger:

```text
declared gauge decision-null on policy differences
  -> quotient certificate is well-posed;

quotient reward error delta
  -> policy regret at most delta times occupancy diameter;

estimated margin above directional uncertainty
  -> policy identity certificate;

positive-scale quotient
  -> sufficient for argmax, insufficient for fixed-unit regret.
```

This consolidates established ingredients into the exact claim boundary needed
by the ASMP-9 resolution audit. No new IRL, apprenticeship-learning, robust
optimization, or regret theorem is claimed.

## Required controls before registration

1. a sharp two-policy equality witness;
2. a gauge-invalid cell returning unavailable rather than a numeric bound;
3. positive-scale policy invariance paired with a fixed-regret-threshold flip;
4. nonzero-regret and zero-regret policy cells;
5. strict-margin pass and equality/inconclusive controls;
6. exact rational arithmetic for every finite decision; and
7. no claim that reward regret alone establishes safety.
