# ASMP-9 decision-quotient information v0.33

## Status

Development only. This directory is not registered and has no
claim-eligible result.

It tests the next resolution-audit obligation: whether behavioral and
environment-intervention access can be expressed in one fixed-confidence
information design after quotienting reward representations by the declared
policy answer.

Read:

- [`DEVELOPMENT_NOTE_v0_33.md`](DEVELOPMENT_NOTE_v0_33.md) for the proposed
  finite theorem and successor requirements; and
- [`PRIOR_ART_GATE_v0_33.md`](PRIOR_ART_GATE_v0_33.md) for the established
  controlled-sensing and pure-exploration results that subsume the generic
  information formula; and
- [`NATIVE_DEVELOPMENT_RESULT_v0_33.md`](NATIVE_DEVELOPMENT_RESULT_v0_33.md)
  for the unregistered result generated from v0.29-v0.32 objects; and
- [`COUPLING_QUOTIENT_THEOREM_v0_33.md`](COUPLING_QUOTIENT_THEOREM_v0_33.md)
  for the exact decision-equivalence quotient connecting the v0.31 and v0.32
  matrix shapes.

Run the planted channel-necessity control with:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33/run_development.py

python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33
```

Run the ASMP-9-native development fixture with:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33/run_native_development.py

python ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33/run_coupling_development.py
```

The fixture is intentionally small. Its role is to verify that:

- the optimal design allocates positive mass to all three access channels;
- deleting any one channel makes a policy-changing alternative
  indistinguishable; and
- an observationally identical same-policy gauge alias blocks parameter
  identification without blocking decision identification.

The native development fixture instantiates the hypothesis family from the
actual v0.28-v0.32 reward, mechanics, behavior, and policy objects. The
coupling theorem shows that the v0.31-v0.32 composition has 18
decision-relevant coordinates and a 30-dimensional decision-null gauge. The
remaining pre-freeze seam is empirical: no registered acquisition grammar
yet says which linear functionals of that quotient can be measured.
