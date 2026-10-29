# ASMP-9 v0.53 aggregate randomized coverage

## Status

Development theorem. Randomized confidence procedures are classical. The
candidate ASMP-9 result is an exact insufficiency statement for the
deterministic subset-bound compression.

## Randomized direct procedure

For finite outcomes `x`, reports `r`, parameters `theta`, scalar risks
`d(theta)`, and external randomness `Z`, write

```text
q_xr = P(U(x,Z)=r).
```

The exact finite optimization is:

```text
minimize  sum_x w_x sum_r r q_xr

subject to
  sum_r q_xr = 1                         for every x
  sum_x P_theta(x) sum_{r>=d(theta)} q_xr
      >= 1-alpha                         for every theta
  q_xr >= 0.
```

This is a rational linear program when the inputs are rational.

## Standard structural facts

1. Any conditional report law can be represented as a mixture of deterministic
   maps, for example using the product coupling over outcomes. Its deterministic
   components need not be valid individually.
2. With `n` outcome-normalization constraints and `k` coverage constraints, a
   basic feasible solution has at most `n+k` positive report atoms. Hence its
   total support beyond one atom per outcome is at most `k`.
3. Randomization can strictly improve over deterministic valid maps. With one
   outcome, risk `1`, reports `{0,1}`, and error budget `alpha`, the
   deterministic value is `1` while the randomized value is `1-alpha`.

These are standard randomized-decision and LP consequences.

## Theorem: subset-bound insufficiency

Let `alpha=1/2`, reports be `{0,1}`, and reference weights be `(1/2,1/2)`.
Consider one risk-one parameter under either experiment:

```text
P_A = (3/5, 2/5)
P_B = (9/10, 1/10).
```

Both experiments induce exactly the same deterministic subset-bound table:

```text
B(empty) = 0
B({x_0}) = 1
B({x_1}) = 0
B(X) = 1.
```

Both therefore have the same valid deterministic maps and deterministic
optimum:

```text
u* = (1,0)
value = 1/2.
```

Under aggregate randomized coverage, however:

```text
experiment A:
  P(report 1 | x_0) = 5/6
  randomized value = 5/12

experiment B:
  P(report 1 | x_0) = 5/9
  randomized value = 5/18.
```

The thresholded subset table is therefore insufficient to determine the
randomized optimum.

### Exact lower certificates

For `P=(p,1-p)`, set

```text
lambda = (1/2)/p.
```

Because `p>=1/2`,

```text
lambda P(x_i) <= 1/2 = w_i
```

for both outcomes. Any feasible success vector `s` obeys

```text
w dot s
  >= lambda P dot s
  >= lambda/2
  = 1/(4p).
```

The displayed procedures attain this bound. Substitution gives `5/12` and
`5/18`.

## Minimality

One outcome is sufficient for strict randomized gain but insufficient for a
same-subset-table/different-experiment witness, because its probability law is
uniquely `(1)`. Two outcomes are therefore minimal for the information-loss
statement.

## ASMP-9 implication

The subset-bound table is a sufficient statistic for deterministic direct
Buehler optimization but not for aggregate randomized optimization. Any
resolution path that admits aggregate randomized coverage must retain more of
the experiment—at least the probability magnitudes relevant to fractional
failure allocation.

## Claim boundary

This is a finite exact witness inside classical randomized confidence theory.
It does not establish novelty, operational desirability, continuous or
strategic robustness, a physical preference channel, or an ASMP-9 resolution.
