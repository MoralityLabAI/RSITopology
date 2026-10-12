# ASMP-9 v0.38 theorem draft: a decision-relative access threshold

## Status

`proved_for_registered_symmetric_family_confirmation_pending`

This is a finite specialization of classical experiment-comparison results.
The candidate contribution is the reward-gauge/query-access instantiation and
its exact threshold, not a new deficiency theorem.

## Family

There are three reward/decision classes `theta in {0,1,2}` and three policies.
The normalized policy-regret loss is zero for the matching policy and one for
the other two policies.

For rational `0 <= low < high <= 1`, define two conditionally independent
binary target queries:

```text
q_0:
  P(1 | theta=0) = high
  P(1 | theta=1) = P(1 | theta=2) = low

q_1:
  P(1 | theta=1) = high
  P(1 | theta=0) = P(1 | theta=2) = low.
```

A nuisance bit selects between reward representatives `r_theta` and
`r_theta + c*1`. A third query reveals that bit. Its conditional nuisance law
is target-independent. Full access is `(q_0,q_1,q_gauge)`.

Let

```text
gap = high - low.
```

## Theorem 1: exact one-query deletion cost

After marginalizing the target-independent nuisance law,

```text
delta_D(q_1, (q_0,q_1)) = gap/2
delta_D(q_0, (q_0,q_1)) = gap/2.
```

For this registered loss, the value equals ordinary target-experiment
deficiency.

### Upper bound

Suppose access retains `q_1` and omits `q_0`. Preserve the observed `q_1`
bit, then synthesize an independent `q_0` bit with probability

```text
m = (high + low)/2.
```

For every target, the synthesized and reference laws share the `q_1`
marginal. Their total-variation distance is therefore just the distance
between Bernoulli `m` and the required Bernoulli `high` or `low`, exactly
`gap/2`. The ordinary randomization bound transfers every `[0,1]`-valued
policy loss with that relaxation.

### Lower bound

Under `q_1`, targets `theta=0` and `theta=2` have identical observation laws,
so every source rule induces the same action distribution on them.

Consider the full-access rule that chooses policy 0 when `q_0=1` and policy 2
when `q_0=0`, ignoring `q_1`. Its risks on these two targets are

```text
R_full(theta=0) = 1 - high
R_full(theta=2) = low.
```

If a source rule transferred both risks with relaxation `epsilon`, and
`p_0,p_2` are its probabilities of choosing policies 0 and 2, then

```text
p_0 >= high - epsilon
p_2 >= 1 - low - epsilon.
```

Because `p_0 + p_2 <= 1`,

```text
epsilon >= (high - low)/2 = gap/2.
```

The opposite deletion is symmetric.

## Theorem 2: target-independent gauge observation is ancillary

If the nuisance law is the same for every target, the marginal distribution
of `q_gauge` is target-independent and conditionally independent of the two
target queries. One kernel drops it; another appends a fresh draw from its
registered marginal law. Therefore

```text
delta_D((q_0,q_1), full_access) = 0
```

and adding or deleting `q_gauge` cannot change any target-relative access
threshold.

This is a statement about the full data-generating law, not the label
“gauge.” If the choice of representative is correlated with `theta`, observing
the representative may leak target information even though the
transformation itself is decision-preserving.

## Theorem 3: expanded reconstruction still charges the gauge bit

Keep `(theta,xi)` as the expanded parameter and let `q_gauge=xi`
deterministically. Access to only `(q_0,q_1)` has identical laws at fixed
`theta` across the two nuisance states, whereas full access has disjoint
`q_gauge` outputs.

By the total-variation triangle inequality, any one simulation kernel has
worst-cell error at least `1/2`. Appending a fair synthetic gauge bit attains
`1/2`. Hence

```text
delta_full((q_0,q_1), full_access) = 1/2.
```

Thus exact policy-decision sufficiency does not require exact reconstruction
of the reward representative.

## Access consequence

For every tolerance

```text
epsilon < gap/2,
```

both target queries are necessary and sufficient relative to full access.
At `epsilon = gap/2`, either single target query is sufficient. Whether the
empty family is also sufficient at that boundary is a separate finite risk-set
calculation and is reported rather than inferred.

## Burned checks

The exact implementation reproduced `gap/2` for:

| `(high,low)` | `gap/2` | Computed `delta_D` | Ordinary deficiency |
| --- | ---: | ---: | ---: |
| `(2/3,1/3)` | `1/6` | `1/6` | `1/6` |
| `(3/4,1/4)` | `1/4` | `1/4` | `1/4` |
| `(4/5,1/5)` | `3/10` | `3/10` | `3/10` |
| `(3/5,2/5)` | `1/10` | `1/10` | `1/10` |

These points are burned and excluded from confirmation.

## Claim boundary

This theorem covers one three-class symmetric query grammar, one normalized
policy-regret type, and target-independent constant-shift nuisance. It does
not characterize arbitrary rewards, adaptive interventions, correlated or
strategic nuisance, non-expected-utility demonstrators, or the full ASMP-9
problem.

