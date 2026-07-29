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
  information formula.

Run the planted channel-necessity control with:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33/run_development.py

python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33
```

The fixture is intentionally small. Its role is to verify that:

- the optimal design allocates positive mass to both access channels;
- deleting either channel makes a policy-changing alternative
  indistinguishable; and
- an observationally identical same-policy gauge alias blocks parameter
  identification without blocking decision identification.

The next version must instantiate the hypothesis family from the actual
v0.28-v0.32 reward, mechanics, behavior, and policy objects before any
registration.
