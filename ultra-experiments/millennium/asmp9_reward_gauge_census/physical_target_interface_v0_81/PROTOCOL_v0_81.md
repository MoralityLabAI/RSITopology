# ASMP-9 structured physical target-interface protocol v0.81

Status: **frozen prereveal protocol; no v0.81 outcome has been executed**.

## Question

Can the known algebra of controlled reward interventions repair v0.80's
finite-sample cardinal-recovery failure at the same per-query sample count,
while preserving the frozen leakage and misspecification thresholds?

## Preserved object

Version v0.81 preserves from v0.80:

- the exact four-edge finite MDP;
- base, shaping, and matched-norm non-gauge reward deltas;
- construction and holdout context margins;
- `beta in {0.5, 1, 2}`;
- 512 iid Bernoulli samples per arm/query cell;
- target semantics and the `0.15` uniform cardinal-error threshold;
- the `0.12` representative-leakage threshold;
- per-sample TV radius `1e-5` and robust bound threshold `0.05`; and
- deterministic primary/replay equality.

Only the decoder and fresh seed universe change. The v0.80 outcomes are burned
design evidence and cannot enter v0.81's rows.

## Structured decoder

For context `c`, let `theta_c` be its unknown base route margin. The registered
decoder arms have known intervention offsets

```text
base:             0
nongauge_plus:   +2
nongauge_minus:  -2.
```

For decoder arm `a` and inverse temperature `beta`,

```text
Pr(left) = sigmoid(beta * (theta_c + d_a)).
```

The primary estimator maximizes the joint Jeffreys-corrected binomial
log-likelihood over all nine decoder-arm/query cells in one context. It is
implemented as fixed-iteration bisection of the strictly decreasing score:

```text
sum_{a,beta} beta * [(successes + 1/2)
  - (samples + 1) sigmoid(beta * (theta + d_a))] = 0.
```

The fitted target for every arm is `theta_hat + d_a`, with zero offset for
both shaping representatives. Shaping rows are excluded from the target
likelihood and used only by `L0`; this prevents representative leakage from
becoming target information.

The v0.80 armwise average-of-inverse-logits estimator is reported as a burned-
design comparator on the fresh rows but cannot affect any gate.

## Misspecification accounting

`M0` applies to one context-local structured decoder. Its finite hypothesis
set is the four frozen base margins. For every ordered pair, the registered
Hellinger affinity is multiplied across the three decoder arms, three beta
values, and 512 samples per cell. The TV penalty is

```text
1 - (1 - 1e-5)^(3 * 3 * 512).
```

No shaping sample is counted because no shaping response is consumed by the
target decoder. Conversely, every decoder-consumed sample is counted.

## Frozen gates

### W0 — target/gauge well-posedness

Pass iff exact rational arithmetic confirms shaping invariance, non-gauge
target change, and matched squared norm, exactly as in v0.80.

### I0 — replay identity

Pass iff primary and replay response rows and result files are byte-identical.

### D0 — decoder admission

Pass iff the registered offsets equal the exact route-margin effects, the
decoder uses exactly `{base, nongauge_minus, nongauge_plus}`, shaping rows are
excluded, and the score changes sign inside the frozen MLE bracket for every
context.

### R0 — structured cardinal recovery

Pass iff, across all 20 context/arm targets,

```text
maximum absolute error <= 0.15
and every estimated margin has the correct sign.
```

Equality passes. No sign-only substitution is allowed.

### L0 — representative leakage

As in v0.80, pass iff the maximum empirical probability difference between
base and either shaping representative is at most `0.12`.

### M0 — robust finite-hypothesis bound

Pass iff the structured-decoder Hellinger union bound plus the accumulated TV
penalty is at most `0.05`. Equality passes.

## Fixed sequence

```text
W0 -> I0 -> D0 -> R0 -> L0 -> M0.
```

Only `pass` opens the next gate. Any invalid instrument makes the affected gate
`not_evaluated`; fail or inconclusive stops. There is no near-pass override.

## Claim boundary

A full pass establishes only that known intervention offsets repair one
finite-sample acquisition failure in one exactly controlled softmax-planner
fixture. It does not show that such offsets are available in natural systems,
validate softmax behavior, identify human or language-model values, establish
moral adequacy, or resolve ASMP-9.

