# Finite-sample upper construction for the native ASMP-9 registry

## Status

**Unregistered development result. Not claim-eligible.**

The earlier v0.33 calculation supplied a classical change-of-measure lower
bound but no procedure achieving a declared finite error. This note gives one
fixed-sample construction for the five-hypothesis native registry.

It is not an optimal adaptive algorithm and does not extend beyond the known,
independent Bernoulli laws in that registry.

The machine-readable result is
[`FINITE_UPPER_BOUND_DEVELOPMENT_v0_33_2.json`](FINITE_UPPER_BOUND_DEVELOPMENT_v0_33_2.json),
SHA-256
`7d16e8172dfdecfb48852c6eb4c0e7d2f905aee5e1f185657f105cee629d6da8`.

```text
focused v0.33 tests                    26 passed
v0.28-v0.33 predecessor/current tests 108 passed
```

## Rule

Three independent tests use:

```text
return channel     p0 = 1/4, p1 = 3/4
mechanics channel  p0 = 1/4, p1 = 3/4
mixture audit      p0 = 1/2, p1 = 9/17
```

Each sample count is a multiple of the exact midpoint denominator, so its
integer success threshold equals the midpoint exactly. The decision rule is:

1. if the mixture count crosses its threshold, return `not_certified`;
2. otherwise, if either return or mechanics crosses its threshold, return
   `policy_0`; and
3. otherwise return `policy_1`.

The `gauge_alias` has the base law and the same `policy_1` answer.

## Exact error accounting

Write `alpha_R, alpha_M, alpha_A` for false positives and
`beta_R, beta_M, beta_A` for false negatives. Under independent channel
samples, the five exact error probabilities are:

```text
base = gauge_alias
  = alpha_A
    + (1-alpha_A) [1 - (1-alpha_R)(1-alpha_M)];

reward_flip
  = alpha_A + (1-alpha_A) beta_R (1-alpha_M);

mechanics_flip
  = alpha_A + (1-alpha_A) beta_M (1-alpha_R);

mixture_invalid
  = beta_A.
```

Every binomial tail is summed as an exact rational. The result artifact stores
decimal renderings plus SHA-256 hashes of the complete numerator/denominator
strings to avoid placing multi-thousand-digit fractions in the JSON.

## Constructive certificate

At `delta = 1/20`, exhaustive exact search over the frozen midpoint-aligned
grid returns:

```text
return samples       64   threshold 32
mechanics samples    64   threshold 32
mixture samples    3196   threshold 1645
total queries       3324
worst error          0.049999700044997697
```

All five registered hypotheses have exact error strictly below `0.05`. The
worst case is the base/gauge answer class. The result is minimal only within
the declared grid and decision rule; thresholds were not optimized.

A conservative construction assigning `delta/3` separately to each channel
uses 5,344 queries. Joint exact accounting therefore removes 2,020 queries
without relaxing the uniform error target.

## Lower/upper bracket

At the base truth and equal unit query costs:

```text
change-of-measure expected-query lower bound  1538.6941488690566
fixed-query constructive upper bound          3324
upper/lower ratio                              2.1602733736546322
```

The lower bound applies to any uniformly `delta`-correct adaptive procedure
on the finite registry. The upper construction has a deterministic query
count, so its expected count at the base is also 3,324. This is a valid
finite-registry bracket, not an asymptotically matching characterization.

## What changed

The v0.33 native registry is no longer lower-bound-only. It now has:

- a decision-identifiability criterion;
- a characteristic-time lower bound;
- an explicit uniformly error-controlled decision rule; and
- a finite gap of about `2.16` between that fixed rule and the lower bound at
  the base instance.

## What remains open

- Optimize thresholds, channel error allocation, and adaptive stopping.
- Replace known independent laws with confidence sequences robust to unknown
  probabilities and dependence.
- Freeze nonuniform query costs.
- Connect the statistical channel to physically implemented composite probes.
- Extend beyond the five-hypothesis native registry.

Nothing here validates a human or model response law, proves a general
preference-learning rate, or resolves ASMP-9.
