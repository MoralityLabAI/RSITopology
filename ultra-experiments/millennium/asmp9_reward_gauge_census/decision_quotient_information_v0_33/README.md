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
  matrix shapes; and
- [`COMPOSITE_PROBE_DESIGN_v0_33_1.md`](COMPOSITE_PROBE_DESIGN_v0_33_1.md)
  for the 18-probe factorized basis and 48-query entrywise comparator; and
- [`FINITE_UPPER_BOUND_DEVELOPMENT_v0_33_2.md`](FINITE_UPPER_BOUND_DEVELOPMENT_v0_33_2.md)
  for an exact uniformly error-controlled fixed rule on the native registry;
  and
- [`QUERY_SPAN_CERTIFICATE_v0_33_3.md`](QUERY_SPAN_CERTIFICATE_v0_33_3.md)
  for the fail-closed access gate, exact witnesses, and the noise-optimized
  factorized basis.

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

python ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33/run_composite_probe_development.py

python ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33/run_finite_upper_bound_development.py

python ultra-experiments/millennium/asmp9_reward_gauge_census/decision_quotient_information_v0_33/run_query_span_development.py
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

The factorized design supplies a candidate grammar—six behavioral-cell
perturbations crossed with three policy-contrast readouts—but no model
intervention or linearity validation has yet established that those composite
queries are physically available.

On the finite stochastic side, an exact midpoint-grid search now supplies a
3,324-query fixed rule with error strictly below `0.05` on every native
hypothesis. This brackets the base-instance change-of-measure lower bound
within a factor of about `2.16`, but assumes known independent Bernoulli laws
and is neither adaptive nor globally optimized.

The query-span successor turns any proposed physical grammar into a total
decision: full span with a reconstruction error multiplier, or failure with
an invisible-but-policy-changing coupling witness. The preferred exact basis
keeps 18 probes while reducing worst-case infinity-norm amplification from
12 to 8. Physical availability remains untested; the v0.34 protocol is still
a draft.
