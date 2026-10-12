# Conditional fibers expose exactly the finite Bradley-Terry cycle quotient

## Status

Development theorem draft. The result is a specialization of classical
conditional inference for discrete exponential families and the toric
Bradley-Terry model. Novelty is not claimed.

## Observation model

Fix an oriented finite graph with `m` edges and vertex-edge incidence matrix:

```text
D^T : R^m -> R^|V|.
```

Edge `e` receives `N_e` independent binary comparisons. Let `Y_e` be the
number of target-node wins and let:

```text
lambda_e = logit(p_e).
```

The joint mass function is:

```text
P_lambda(Y=y)
  = h_N(y) exp(lambda^T y)
      / product_e (1+exp(lambda_e))^N_e,

h_N(y) = product_e choose(N_e,y_e).
```

A scalar Bradley-Terry value has:

```text
lambda = D theta.
```

## Theorem 1: exact nuisance elimination

Condition on the vertex win-balance statistic:

```text
T = D^T Y = t.
```

On the finite fiber:

```text
F_t = {y : 0 <= y_e <= N_e and D^T y=t},
```

the conditional law is:

```text
P_lambda(Y=y | T=t)
  = h_N(y) exp(lambda^T y)
      / sum_{z in F_t} h_N(z) exp(lambda^T z).
```

If `lambda=D theta`, the exponential term is:

```text
exp(theta^T t),
```

which is constant on the fiber. The scalar-value nuisance therefore cancels
exactly:

```text
P_scalar(Y=y | T=t)
  = h_N(y) / sum_{z in F_t} h_N(z).
```

This is finite-sample and parameter-free. No asymptotic approximation is
used.

## Theorem 2: exact visible quotient and fiber liveness

Let:

```text
S_t = span_R {y-z : y,z in F_t}.
```

Two edge-logit vectors `lambda` and `lambda'` induce the same conditional law
on `F_t` if and only if:

```text
lambda-lambda' lies in S_t^perp.
```

Because every fiber difference lies in `ker(D^T)`:

```text
S_t subseteq ker(D^T).
```

The conditional experiment identifies the complete edge-logit quotient
modulo scalar gradients exactly when:

```text
S_t = ker(D^T).
```

Equivalently:

```text
dim(S_t) = beta_1(G) = |E|-|V|+components(G).
```

When the dimension is smaller, only a lower-dimensional quotient is visible.
A singleton fiber has dimension zero and must return unavailable, not
`coherent`.

### Proof

The ratio of two conditional masses at `y,z in F_t` is:

```text
h_N(y)/h_N(z) * exp(lambda^T(y-z)).
```

Equality of the two conditional laws is therefore equivalent to:

```text
(lambda-lambda')^T(y-z)=0
```

for every fiber difference, which is precisely membership in `S_t^perp`.
The full-quotient statement follows from:

```text
ker(D^T)^perp = im(D).
```

## Corollary: one-cycle exact family

Let the graph be a consistently oriented simple cycle of length `k`, with
`N_e=n` on every edge. On the zero-balance fiber:

```text
D^T y=0,
```

every count is equal:

```text
y=(z,...,z),  z in {0,...,n}.
```

Let the cycle circulation be:

```text
Delta = sum_e lambda_e.
```

Then:

```text
P_Delta(Z=z | T=0)
  = choose(n,z)^k exp(Delta z)
      / sum_{u=0}^n choose(n,u)^k exp(Delta u).
```

Thus the conditional law depends on the edge logits only through their
gauge-invariant circulation. For `Delta>0`, the likelihood ratio against
`Delta=0` is proportional to `exp(Delta z)` and is strictly increasing in
`z`. The randomized upper-tail size-`alpha` test is therefore uniformly most
powerful for the one-sided conditional alternative by the
Neyman-Pearson/Karlin-Rubin argument.

When `R=exp(Delta)` is rational, every null probability, alternative
probability, randomized boundary probability, and power value is rational and
can be certified exactly.

## Scaling note

A local normal approximation to:

```text
choose(n,z)^k
```

gives null variance approximately `n/(4k)`. Exponential tilting by `Delta`
therefore yields standardized separation approximately:

```text
Delta sqrt(n/(4k)).
```

This predicts conditional per-edge sample complexity:

```text
n = Theta(k/Delta^2).
```

The registered experiment may test this scaling descriptively using exact
finite thresholds. The asymptotic statement is not claimed as a new theorem,
and it must not be conflated with the v0.9 simultaneous confidence-band task.

## Claim boundary

This theorem concerns independent fixed-count Bernoulli comparisons on a
known finite graph. It conditions on an observed sufficient statistic and
therefore gives conditional, not unconditional, error guarantees. It assumes
a logistic comparison channel and observed item identities.

It does not prove that human or model preferences follow Bradley-Terry,
certify scalarity from non-rejection, handle unknown links, dependent
responses, latent contexts, adaptive graph selection, sequential policies, or
resolve ASMP-9.
