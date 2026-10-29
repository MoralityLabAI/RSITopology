# Prior-art gate for ASMP-9 stochastic experiment v0.37

## Status

Primary disposition complete for the finite theorem claim:
`subsumed_instrument_consolidation`.

The exact finite implementation and its registered universe still require a
separate hostile review before any protocol is frozen.

## Results that already own the general language

- David Blackwell, **Equivalent Comparisons of Experiments**, *Annals of
  Mathematical Statistics* 24(2), 1953:
  <https://doi.org/10.1214/aoms/1177729032>.
  The comparison of experiments by attainable risk and by stochastic
  simulation is classical.
- Lucien Le Cam's deficiency theory supplies approximate comparison of
  statistical experiments. The standard book-length reference is *Asymptotic
  Methods in Statistical Decision Theory* (1986).
- Erik Torgersen, *Comparison of Statistical Experiments* (1991), develops
  sufficiency, randomization, deficiency, and experiment equivalence:
  <https://doi.org/10.1017/CBO9780511666353>.
- Prem Goel and Morris DeGroot, **Comparison of Experiments and Information
  Measures**, *Annals of Statistics* 7(5), 1979, discusses comparison and
  marginal information when nuisance parameters are present:
  <https://doi.org/10.1214/aos/1176344790>.
- Claude Shannon, **The Zero Error Capacity of a Noisy Channel** (1956),
  supplies the confusability-graph side:
  <https://doi.org/10.1109/TIT.1956.1056798>.
- Skalse et al., **Invariance in Policy Optimisation and Partial
  Identifiability in Reward Learning**:
  <https://arxiv.org/abs/2203.07475>.
- Skalse and Abate, **Partial Identifiability and Misspecification in Inverse
  Reinforcement Learning**:
  <https://arxiv.org/abs/2411.15951>.

## Subsumption posture

The following are not candidate-new claims:

- Blackwell dominance as a decision-uniform comparison;
- simulation/garbling characterizations in the classical finite experiment;
- Le Cam deficiency as an approximate risk-comparison device;
- zero-error confusability graphs; or
- the fact that equal observational laws define equivalence classes.

More strongly, the proposed quantity

```text
inf_K sup_(theta,xi)
  TV(K P^A_(theta,xi), P^B_(theta,xi))
```

is ordinary finite directional deficiency after expanding the statistical
parameter to `(theta,xi)`. Its `[0,1]`-loss risk-transfer inequality is a
direct classical corollary, not a new robust-deficiency theorem.

When the loss depends only on `theta`, full expanded-parameter deficiency is
a sufficient comparison but need not be necessary: it requires pointwise
simulation for nuisance distinctions the decision maker may not care about.
The relevant target-only comparison belongs to the established literature on
marginal information and nuisance parameters. Version 0.37 must not claim a
general converse without locating it in that literature.

The retained contribution is therefore an instrument consolidation:

1. make the ASMP-9 access object explicit as a compound statistical
   experiment;
2. keep exact fibers, pairwise confusability, component decision quotients,
   and bounded-risk deficiency separate;
3. freeze shared-versus-reset nuisance coupling as part of the access model;
   and
4. build an exact rational instrument that exposes both when a zero-error
   quotient is insufficient for bounded-risk safety decisions and when full
   expanded-state deficiency is conservative for target-only decisions.

## Searches completed

- Blackwell comparison for experiment simulation and decision risk;
- Le Cam/Torgersen deficiency and randomization;
- nuisance parameters as part of the statistical parameter space; and
- marginal experiment information when loss concerns only a parameter of
  interest.

These searches are sufficient to reject the proposed theorem-novelty sentence.

## Required checks before registration

- deficiency under total-variation contamination neighborhoods;
- inverse-reinforcement-learning results stated directly in decision-risk or
  experiment-comparison language; and
- exact finite LP formulations and dual certificates for deficiency.

The protocol must describe every theorem as classical or elementary. Its
claim-eligible output may be an exact ASMP-9 access ledger, a counterexample
to quotient-only reporting, and a calibration of deficiency conservatism. It
may not be presented as a new comparison-of-experiments theorem.
