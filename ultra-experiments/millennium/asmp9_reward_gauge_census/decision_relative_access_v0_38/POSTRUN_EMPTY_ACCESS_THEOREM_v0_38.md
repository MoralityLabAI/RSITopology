# Post-run theorem note: the empty-access radius

## Status

`proved_post_reveal_not_a_registered_v0_38_gate`

The v0.38 confirmation grid was registered only to require that no-query
access remain strictly above the one-query boundary. After reveal, its three
exact values exposed a stronger closed form. This note proves that formula
but does not retroactively add it to the v0.38 hypotheses.

## Statement

In the symmetric family of
[`THEOREM_DRAFT_v0_38.md`](THEOREM_DRAFT_v0_38.md), additionally assume

```text
high + low = 1
gap = high - low.
```

For the three-class zero-one policy-regret problem,

```text
delta_D(no queries, (q_0,q_1))
  = gap/2 + gap^2/6.
```

The same value is the ordinary directional deficiency from the constant
experiment to the two-query target experiment.

## Upper bound

Write `h=high` and `l=low`. The full experiment has outcomes ordered
`00,01,10,11`. From a constant observation, synthesize the distribution

```text
K = (a,a,a,h*l)
a = (h^2 + h*l + l^2)/3.
```

Because `h+l=1`, `3a+h*l=1`, so `K` is a probability distribution.

For `theta=0`, the full row is

```text
P_0 = (h*l, l^2, h^2, h*l).
```

The absolute coordinate differences are

```text
gap^2/3,
gap*(1+l)/3,
gap*(1+h)/3,
0.
```

Their sum is `gap + gap^2/3`; total variation is therefore

```text
gap/2 + gap^2/6.
```

The other two target rows give the same value by symmetry. Ordinary
deficiency is at most this amount, and the `[0,1]` randomization bound gives
the same upper bound for `delta_D`.

## Lower bound

Use the deterministic full-access rule

```text
00 -> policy 2
01 -> policy 1
10 -> policy 0
11 -> policy 1.
```

Its risk vector is

```text
r_0 = 1 - h^2
r_1 = l
r_2 = 1 - h^2.
```

A no-query rule is one fixed action distribution `(p_0,p_1,p_2)`. If it
transfers this risk vector with relaxation `epsilon`, then

```text
p_theta >= 1 - r_theta - epsilon
```

for all three targets. Summing and using `sum p_theta=1` gives

```text
epsilon >= (2 - sum_theta r_theta)/3.
```

Substituting `h=(1+gap)/2` and `l=(1-gap)/2` yields

```text
epsilon >= gap/2 + gap^2/6.
```

The bounds coincide.

## Observed v0.38 instances

| `gap` | Formula | Sealed no-query value |
| ---: | ---: | ---: |
| `3/7` | `12/49` | `12/49` |
| `3/4` | `15/32` | `15/32` |
| `1/4` | `13/96` | `13/96` |

These matches are descriptive because the formula was identified after
reveal. A successor can register the formula on disjoint strengths or use it
as an analytic component without presenting v0.38 as prospective evidence
for it.

