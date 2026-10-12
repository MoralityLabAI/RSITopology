# Finite-sample cycle-coherence certificates

## Status

Development theorem draft for ASMP-9 v0.9. The concentration argument,
Bradley-Terry model, and graph-Hodge consistency criterion are classical.
Novelty is not claimed.

## Observation model

Let `G=(V,E)` be a finite directed comparison graph. Edge `e=(i,j)` has
independent Bernoulli observations with probability `p_e` that `j` is
preferred to `i`. Let

```text
l_e = logit(p_e).
```

For a scalar Bradley-Terry model,

```text
l_(i,j) = theta_j-theta_i.
```

Fix a deterministic spanning forest and its fundamental-cycle matrix `C`.
Scalar coherence is equivalent to

```text
C l = 0.
```

Graphs with `beta_1=0` contain no coherence test and must return
`unavailable_no_cycles`, not a vacuous positive certificate.

## Simultaneous edge event

Suppose every edge receives `n` independent comparisons. With `m=|E|`, set

```text
delta_n = sqrt(log(2m/alpha)/(2n)).
```

Hoeffding's inequality and a union bound give

```text
P(max_e |p_hat_e-p_e| > delta_n) <= alpha.
```

The operational admission rule requires every observed interval

```text
[p_hat_e-delta_n, p_hat_e+delta_n]
```

to lie inside the registered interior `[eta,1-eta]`. On the simultaneous
event, both `p_e` and `p_hat_e` then lie in that interval, and the mean-value
theorem yields

```text
|logit(p_hat_e)-logit(p_e)|
  <= delta_n/(eta(1-eta))
  = epsilon_edge.
```

For a fundamental cycle row `c`, define its length

```text
k_c = ||c||_1.
```

Then, simultaneously for every registered cycle,

```text
|c^T logit(p_hat)-c^T l| <= k_c epsilon_edge.
```

## Total three-way decision

Freeze two separated scientific margins:

```text
0 <= epsilon_coherent < epsilon_incoherent.
```

For each cycle, form the simultaneous band

```text
I_c = c^T logit(p_hat) +/- k_c epsilon_edge.
```

Return:

```text
certified_coherent_within_tolerance
```

only if every `I_c` lies inside
`[-epsilon_coherent,epsilon_coherent]`;

```text
certified_incoherent
```

only if at least one `I_c` lies entirely outside
`[-epsilon_incoherent,epsilon_incoherent]`; and

```text
inconclusive
```

otherwise.

On the simultaneous event, every positive certificate is valid for the
registered fundamental-cycle coordinates. The procedure never converts
failure to reject into evidence that a scalar exists.

## Conservative graph-dependent sample bound

Let `k_max` be the maximum registered fundamental-cycle length, and let `d_p`
be the minimum distance of every true edge probability from the registered
probability-floor boundary. Data-dependent interior admission is guaranteed
on the simultaneous event when

```text
2 delta_n <= d_p.
```

Conditional on admission, exact coherence is guaranteed to certify when

```text
2 k_max epsilon_edge <= epsilon_coherent.
```

A planted cycle with circulation magnitude `Delta` is guaranteed to certify
incoherent when

```text
Delta - 2 k_max epsilon_edge >= epsilon_incoherent.
```

Thus it suffices to choose `n` so that

```text
delta_n <=
  min(
    d_p/2,
    eta(1-eta)/(2 k_max)
      * min(epsilon_coherent, Delta-epsilon_incoherent)
  ).
```

The resulting conservative scaling is

```text
n = O(
  k_max^2 log(m/alpha)
  /
  (eta^2(1-eta)^2 margin^2)
).
```

This is a sufficient bound for the registered certificate, not a minimax
optimality theorem.

## Claim boundary

The result concerns independent fixed-count Bernoulli comparisons on a fixed
graph, a registered fundamental-cycle basis, and a declared probability
interior. It does not cover adaptive sample allocation, dependent human
responses, unknown links, contextual preferences, general IRL, or exact
finite-sample certification of zero circulation.
