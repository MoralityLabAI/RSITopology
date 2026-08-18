# ASMP-9 v0.51 randomized-ordering verification protocol

## Status

This protocol freezes an exhaustive finite theorem audit. It registers no
model experiment and no novelty claim.

## Frozen universe

Reuse the complete v0.50 three-outcome universe:

```text
monotone binary tables with B(empty)=0: 19
ordered objective pairs:                 361
outcome orderings:                         6
reference vertices:                        2
scenarios per pair:                        4.
```

Reference vertices:

```text
(1/2,1/3,1/6)
(1/6,1/3,1/2).
```

For every ordered table pair, form the `6 x 4` regret matrix and solve the
optimizer and adversary LPs by exact rational vertex enumeration.

## Gates

### H0: source integrity

Every registered source hash must match.

### T0: tests

All seven scientific tests and all three verifier tests must pass.

### U0: universe completeness

The verifier must enumerate exactly 19 tables, 361 ordered pairs, six
orderings, and four scenarios per pair.

### P0: primal/dual equality

Every exact optimizer LP value must equal its adversarial dual value.

### C0: feasibility and complementary slackness

For every pair:

- optimizer probabilities are nonnegative and sum to one;
- every scenario expectation is at most the value;
- adversary probabilities are nonnegative and sum to one;
- every ordering expectation is at least the value; and
- positive-support actions and scenarios satisfy equality.

### Z0: zero-regret support theorem

For every pair, randomized value is zero if and only if at least one
deterministic ordering has zero regret in all four scenarios.

### R0: deterministic dominance

Randomized minimax regret must never exceed deterministic minimax regret.
The deterministic value must independently equal the minimum row maximum of
the regret matrix.

### B0: v0.50 recovery

Exactly 79 ordered table pairs must have a common zero-regret ordering and
282 must not. This count is a previously sealed v0.50 result, not a new
outcome threshold.

### M0: minimal strict-gain control

The two-outcome reference-switch control must have:

```text
deterministic value: 1/2
randomized value:    1/4
gain:                1/4
primal strategy:     (1/2,1/2)
dual strategy:       (1/2,1/2).
```

### RESOURCE

The single verification process must finish within 180 seconds and 512 MiB
peak working set.

## Unthresholded outcomes

The following are reported but cannot affect pass/fail:

- number of table pairs with strict randomization gain;
- complete exact gain histogram;
- maximum and mean absolute gain;
- primal and dual support-size distributions; and
- all 361 per-pair exact rows.

The burned 20-pair pilot count is not pooled.

## Stop rule

The theorem is verified only if every gate passes. There is no discretionary
near-pass. A post-outcome verifier correction must preserve the original
registration and result and be separately registered.

## Claim boundary

Passing verifies the finite Buehler specialization of established randomized
minmax-regret mathematics. It does not establish novelty, justify randomized
confidence reporting operationally, provide a large-width algorithm, handle
continuous or strategic uncertainty, validate a physical preference channel,
or resolve ASMP-9.
