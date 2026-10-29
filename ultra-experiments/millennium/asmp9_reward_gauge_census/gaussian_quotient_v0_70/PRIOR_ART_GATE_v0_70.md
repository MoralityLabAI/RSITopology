# Prior-art gate for ASMP-9 Gaussian quotient v0.70

Status: **subsumed mathematical ingredients; ASMP-9 specialization only**.

## Classical sources and concepts

The result is an application of established theory:

1. generalized least squares gives covariance `M^-1` in a full-rank Gaussian
   linear model;
2. Gaussian-prior Bayes risks approaching the flat-prior limit give the
   classical minimax location risk;
3. A-optimal design minimizes `trace(M^-1)`;
4. c-optimal design minimizes `c^T M^-1 c`; and
5. information singularity is the standard estimability obstruction.

Kiefer and Wolfowitz's optimal-design theory and the later approximate-design
literature are stronger and more general than the finite allocation census.
Version v0.70 claims no new equivalence or optimal-design theorem.

## Relation to the existing ASMP-9 chain

- v0.28 gives deterministic quotient conditioning for calibrated finite-MDP
  occupancy rows.
- v0.42 gives finite-alphabet confidence intervals uniform over adaptive
  policy trees but does not match them with a minimax lower bound.
- v0.44-v0.46 give decision-specific finite-channel information and allocation
  ledgers with conservative or fixture-specific endpoints.
- v0.69 composes reward gauge and physical measurement nuisance but stops at
  deterministic conditioning.

Version v0.70 fills only the exact Gaussian cell downstream of v0.69.

## Residual deliverable

The useful artifact is the explicit handoff:

```text
v0.69 effective quotient rows
  -> Gaussian information M(n)
  -> exact minimax quotient risk trace(M^-1)
  -> exact policy-margin variance c^T M^-1 c.
```

This turns “conditioning matters” into one matched upper/lower stochastic law
and shows why parameter-optimal and policy-directed allocations differ.

## Hostile-review questions

1. Were quotient coordinates normalized before assigning isotropic squared
   loss?
2. Are query variances known independently of the measured outcomes?
3. Is Gaussian noise a physical model or merely a calibration case?
4. Does the selected policy functional exhaust every downstream use?
5. Does adaptive query selection change the attainable information region?
6. Is fixed mean bias being confused with stochastic variance?

Any public summary must answer these by retaining the registered scope rather
than generalizing from the fixture.
