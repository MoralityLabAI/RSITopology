# ASMP-8 v0.4 claim packet: dynamic audit thresholds

## Correction to v0.3a

The v0.3a optimizer-transfer gate required one policy in every optimizer
family to certify in at least 50% of audit replicates. That fraction was a
registered policy threshold, not a mathematical phase boundary. Version 0.4
removes it rather than replacing it with another chosen fraction.

## Primary estimand

For one nested audit stream, let `U_q(m)` be a simultaneous upper confidence
bound on the hidden proxy-error norm at registered checkpoint `m`. Define its
monotone envelope

```text
Ubar_q(m) = min_{j <= m} U_q(j)
```

and the robust certificate margin

```text
C(m) = max_q [proxy_gain - Ubar_q(m) * dual_movement_q].
```

The dynamic threshold is the hitting time

```text
m_cross = min {m on the registered grid : C(m) > 0}.
```

Because every `Ubar_q` is nonincreasing, `C(m)` is nondecreasing. A certified
policy cannot revert on the registered grid. There is no certification-
probability cutoff.

## Outcome classes

- `crossed`: a stream reaches positive certified margin by the audit cap;
- `budget_censored`: the exact oracle margin is positive, but the stream does
  not cross by the cap;
- `structurally_uncertifiable`: the exact oracle margin is non-positive under
  every registered error geometry.

Across streams, the full hitting-time distribution and crossing CDF are
reported. Quantiles summarize the distribution; they are not gates.

## Claim boundary

This experiment measures audit sample complexity for a synthetic finite
reward-error registry under a finite-grid simultaneous Hoeffding construction.
It does not establish a learned reward model's uncertainty set, make a
universal claim about sequential confidence sequences, or resolve ASMP-8.
