# Exact conditional access to the finite Bradley-Terry cycle quotient

## Theorem 1: scalar nuisance cancellation

Let an oriented finite graph have edge-vertex incidence matrix `D`. Edge `e`
receives `N_e` independent binary comparisons, with target-win count `Y_e`
and log odds `lambda_e`. The joint mass has exponential-family form:

```text
P_lambda(Y=y)
  = h_N(y) exp(lambda^T y)
      / product_e (1+exp(lambda_e))^N_e,

h_N(y) = product_e choose(N_e,y_e).
```

A scalar Bradley-Terry model has `lambda=D theta`. Conditional on:

```text
T = D^T Y = t,
```

the scalar-model law on the finite fiber:

```text
F_t = {y : 0 <= y_e <= N_e and D^T y=t}
```

is exactly:

```text
P(Y=y | T=t)
  = h_N(y) / sum_{z in F_t} h_N(z).
```

It is independent of `theta`.

### Proof

For `lambda=D theta`, the exponential term on the fiber is:

```text
exp(lambda^T y)
  = exp(theta^T D^T y)
  = exp(theta^T t),
```

which is constant and cancels on normalization. QED.

## Theorem 2: the visible quotient is the fiber-difference span

Define:

```text
S_t = span_R {y-z : y,z in F_t}.
```

Two edge-logit vectors `lambda` and `lambda'` induce the same conditional law
on `F_t` if and only if:

```text
lambda-lambda' lies in S_t^perp.
```

Every fiber difference lies in `ker(D^T)`. Therefore the conditional
experiment identifies the full edge-logit quotient modulo scalar gradients
exactly when:

```text
S_t = ker(D^T),
```

or equivalently:

```text
dim(S_t) = beta_1(G) = |E|-|V|+components(G).
```

A rank-deficient fiber identifies only a lower-dimensional quotient. A
singleton fiber identifies none and must not be reported as evidence of
coherence.

### Proof

For `y,z` in one fiber, their conditional probability ratio is:

```text
h_N(y)/h_N(z) * exp(lambda^T(y-z)).
```

The two conditional laws agree exactly when
`(lambda-lambda')^T(y-z)=0` for all fiber differences. Full quotient
identification then follows from:

```text
ker(D^T)^perp = im(D).
```

QED.

## Corollary: exact one-cycle conditional test

On a consistently oriented simple cycle of length `k`, let every edge receive
`n` trials and condition on zero vertex balance. Every count vector is then:

```text
y=(z,...,z),  z=0,...,n.
```

Writing the gauge-invariant cycle circulation as:

```text
Delta = sum_e lambda_e,
```

the conditional law is:

```text
P_Delta(Z=z | T=0)
  = choose(n,z)^k exp(Delta z)
      / sum_u choose(n,u)^k exp(Delta u).
```

For `Delta>0`, the likelihood ratio against `Delta=0` is proportional to
`exp(Delta z)` and is strictly increasing. Hence the randomized upper-tail
size-`alpha` test is uniformly most powerful for the one-sided conditional
alternative. When `R=exp(Delta)` is rational, its size, randomization, and
power are rational and exactly computable.

## Claim boundary

These statements are classical conditional exponential-family and graph
linear algebra specialized to the registered ASMP-9 access grammar. Novelty
is not claimed.

They concern independent fixed-count Bernoulli comparisons, a known logistic
link, known item identities, and conditional rather than unconditional error.
They do not validate Bradley-Terry for human or model behavior, turn
non-rejection into proof of scalarity, handle unknown links, dependent
responses, latent contexts, adaptive graph selection, sequential policies, or
resolve ASMP-9.
