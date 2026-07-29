# ASMP-9 v0.42 theorem draft: confidence-valid finite-sample access

## Setup

Let `Theta`, the finite query library, every query outcome alphabet, and every
registered terminal action set be finite. Query `q` has true channel
`P_q(.|theta)` and empirical channel `P_hat_q(.|theta)`. Policies may adapt
queries to past outcomes for at most horizon `h`.

For decision problem `d`, define the target-wise terminal loss span:

```text
s_d(theta)
  = max_a L_d(theta,a) - min_a L_d(theta,a).
```

Suppose a simultaneous event gives:

```text
TV(P_q(.|theta), P_hat_q(.|theta))
  <= eta(theta,q)
```

for every registered target-query cell.

## Lemma 1: policy-uniform trajectory coupling

For every deterministic or randomized adaptive policy `pi`, match the same
policy tree under `P` and `P_hat`. Its target-wise terminal risks satisfy:

```text
|R_P(pi,theta) - R_Phat(pi,theta)|
  <= s_d(theta)
     min(1, h max_q eta(theta,q)).
```

### Proof

Couple the two executions while their histories agree. Because the policy
sees the same history, it selects the same query. Couple that query's outcomes
maximally; the conditional probability of first divergence is at most its
TV radius. A union bound over at most `h` steps gives history-divergence
probability at most:

```text
min(1, h max_q eta(theta,q)).
```

Before divergence, terminal decisions coincide. After divergence, the
target-specific loss difference is at most its action span. Multiplication
gives the claim. Randomized policies follow by conditioning on their shared
random seed.

## Theorem 1: adaptive upper-risk-set perturbation

Let:

```text
b_A(theta)
  = s_d(theta)
    min(1, h max_(q in A) eta(theta,q)).
```

Every risk vector in the true adaptive upper risk set `U_h(d,A;P)` has a
matched vector in `U_h(d,A;P_hat)` within coordinate-wise distance `b_A`,
and conversely.

This follows by matching every deterministic policy tree and then taking
convex mixtures and upper closures.

## Theorem 2: directed-deficiency confidence interval

Let:

```text
Delta_P(A,B)
```

be the v0.41 directed access deficiency from source library `A` to reference
library `B`, and let `Delta_hat(A,B)` be its empirical-channel value. Then on
the simultaneous channel event:

```text
|Delta_P(A,B) - Delta_hat(A,B)|
  <= max_theta [b_A(theta) + b_B(theta)].
```

If the reference is exact perfect revelation rather than an estimated
channel, set `b_B = 0`.

### Proof

Take any true reference risk vector. Match it to an empirical reference vector
within `b_B`. Apply the empirical directed-containment certificate at
`Delta_hat`. Match its empirical source witness back to a true source witness
within `b_A`. This proves:

```text
Delta_P <= Delta_hat + max_theta(b_A+b_B).
```

Swap true and empirical channels for the reverse inequality.

## Corollary 1: simultaneous multinomial certificate

For one target-query cell with `K` outcomes and `n` iid samples, the
Weissman et al. inequality gives:

```text
Pr(TV(P_hat,P) >= eta)
  <= (2^K-2) exp(-2n eta^2).
```

Allocate total error probability `alpha` over the frozen cell universe by
Bonferroni. Substituting the resulting simultaneous radii into Theorem 2 gives
a finite-sample `(1-alpha)` confidence interval for directed access
deficiency, uniform over all adaptive policy trees.

## Corollary 2: total three-state gate

For access tolerance `epsilon_0` and registered practical margin `m`:

```text
pass
  iff upper confidence bound < epsilon_0 - m;

fail
  iff lower confidence bound > epsilon_0 + m;

inconclusive
  otherwise.
```

Equality is inconclusive. A point estimate never opens access by itself.

## Shared binary-flip sample floor

If each of `Q` queries has one symmetric flip parameter shared across
`Theta` targets and receives `n` balanced samples per target, then:

```text
eta(n)
  = sqrt(log(2Q/alpha)/(2 Theta n)).
```

With one estimated side, common loss span `s`, horizon `h`, and true
containment gap `g`, the smallest certifying sample count is the first integer
strictly exceeding:

```text
n >
  h^2 s^2 log(2Q/alpha)
  / (2 Theta g^2).
```

When both source and reference are estimated from disjoint query families of
`Q` shared flip parameters each, replace `h` by `2h` in the width and replace
`Q` by `2Q` in the simultaneous-radius logarithm. If query cells overlap,
Bonferroni is instead over the exact frozen union and Theorem 2 uses the two
resulting risk radii directly.

## Claim boundary

Multinomial concentration, coupling, simulation lemmas, Bonferroni
simultaneity, and confidence-set propagation are classical. The candidate
contribution is the ASMP-9-specific theorem chain from channel uncertainty to
adaptive upper-risk-set uncertainty and a non-discretionary access gate. It
does not establish optimal confidence regions, matching minimax lower bounds,
strategic-source robustness, continuous-channel results, or a real-model
certificate.
