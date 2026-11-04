# Exact stochastic complexity on a Gaussian reward quotient

Status: **proved classical specialization; development-only and unregistered**.

## 1. Relation to v0.69

Version v0.69 turns a linear reward gauge `G`, physical measurement channel
`A`, and additive measurement nuisance `N` into the
representative-insensitive effective channel

```text
B_bar : R/G -> Y/(N+A(G)).
```

Its smallest singular value gives deterministic conditioning, but not a
sample-complexity theorem. Version v0.70 supplies the exact stochastic law
for one declared noise family.

Choose orthonormal quotient coordinates `x in R^d`. Each available scalar
query/intervention contrast has row `b_i in R^d`. Under allocation
`n=(n_1,...,n_q)`, observe independent samples

```text
Y_(i,j) = b_i^T x + epsilon_(i,j),
epsilon_(i,j) ~ Normal(0,sigma_i^2).
```

The query rows and noise variances are frozen before outcomes.

## 2. Information and exact access

Define

```text
M(n) = sum_i (n_i/sigma_i^2) b_i b_i^T.
```

### Theorem 1: stochastic access criterion

The following are equivalent:

1. the complete Gaussian transcript identifies every quotient coordinate;
2. the allocated query rows span `R^d`;
3. `M(n)` is positive definite.

If `M(n)` is singular, any nonzero `h in ker M(n)` satisfies

```text
b_i^T(x+t h) = b_i^T x
```

for every allocated query and every real `t`. The complete transcript laws
are therefore identical along an unbounded non-gauge direction.

If `M(n)` is positive definite, weighted least squares is

```text
x_hat =
  M(n)^(-1)
  sum_i (b_i/sigma_i^2) sum_j Y_(i,j),
```

with exact law

```text
x_hat ~ Normal(x, M(n)^(-1)).
```

#### Proof

For every `h`,

```text
h^T M(n) h =
  sum_i (n_i/sigma_i^2) (b_i^T h)^2.
```

This vanishes exactly when every allocated row annihilates `h`. The
least-squares distribution follows by linearity and direct covariance
calculation.

## 3. Exact minimax recovery risk

### Theorem 2: squared quotient loss

For squared Euclidean loss on the unbounded quotient `R^d`,

```text
inf_xhat sup_x E_x ||x_hat-x||_2^2
  =
  trace(M(n)^(-1))
```

when `M(n)` is positive definite. When it is singular, the minimax risk is
infinite.

When `M(n)` is positive definite, the same argument gives, for every
positive-semidefinite quadratic loss matrix `W`,

```text
inf_xhat sup_x
  E_x [(x_hat-x)^T W (x_hat-x)]
  =
  trace(W M(n)^(-1))
```

without changing the estimator.

#### Proof

Weighted least squares has constant risk `trace(W M^-1)`, giving the upper
bound. For the lower bound, place the Gaussian prior

```text
x ~ Normal(0,tau^2 I).
```

Its Bayes posterior covariance is

```text
(M + tau^(-2) I)^(-1),
```

so every estimator has worst-case risk at least the corresponding Bayes risk.
Letting `tau -> infinity` gives `trace(W M^-1)`. If `M` is singular, use a
prior whose variance diverges along an unobserved direction charged by `W`.

For a scalar policy-margin functional `c^T x`, the exact minimax mean-squared
error is therefore

```text
v_c(n) = c^T M(n)^(-1) c.
```

## 4. Exact two-policy consequence

Let the registered value difference between the optimal policy and one
competitor be

```text
Delta = c^T x > 0.
```

The plug-in rule selects the competitor exactly when
`c^T x_hat <= 0`. Hence

```text
P(error) =
  Phi(-Delta/sqrt(v_c(n))),

E[simple regret] =
  Delta Phi(-Delta/sqrt(v_c(n))).
```

This is an exact consequence for the plug-in rule, not a claim that every
multi-policy decision problem reduces to one margin. For a finite policy
family, applying the same calculation to every optimal-versus-competitor
occupancy difference gives a union bound; correlations between margins remain
available for a sharper joint calculation.

## 5. Exact integer allocation

For a fixed total sample budget `T`, the allocation universe

```text
{n in Z_+^q : sum_i n_i=T}
```

is finite. Parameter recovery minimizes the classical A-optimal objective

```text
trace(M(n)^(-1)),
```

while one policy margin minimizes

```text
c^T M(n)^(-1)c.
```

These objectives need not select the same experiment.

The exact development fixture has rows

```text
b_0=(1,0), b_1=(0,1), b_2=(1,1),
sigma_i^2=1,
T=12.
```

All 91 weak compositions are enumerated. The unique parameter-recovery
optimum is

```text
n=(5,5,2),
trace(M^-1)=14/45.
```

For policy functional `c=(1,0)`, the two optima are

```text
n=(11,1,0) or (11,0,1),
c^T M^-1 c=1/11.
```

Thus decision-directed allocation can spend only one sample maintaining
global quotient identifiability while concentrating the rest on the relevant
margin. That is a conditional design fact, not permission to ignore other
downstream uses.

## 6. Exact fixed-bias misspecification

If query `i` has an unmodelled fixed mean shift `mu_i`, weighted least squares
has bias

```text
bias(n,mu) =
  M(n)^(-1)
  sum_i (n_i/sigma_i^2) b_i mu_i.
```

Its exact squared-error risk is

```text
trace(M(n)^(-1)) + ||bias(n,mu)||_2^2.
```

For a registered rectangle `|mu_i| <= delta_i`, the worst fixed-bias risk is
the maximum of this convex quadratic over the `2^q` vertices. The verifier
enumerates all eight vertices in the three-query fixture.

This bound makes the role of conditioning explicit but does not bound the
physical misspecification radii `delta_i`.

## 7. ASMP-9 consequence

Versions v0.69-v0.70 now give one complete finite linear-Gaussian chain:

```text
reward gauge + measurement nuisance
  -> maximal representative-insensitive quotient;

allocated Gaussian query rows
  -> necessary and sufficient stochastic access;

information matrix
  -> exact minimax recovery and policy-margin variance;

fixed mean misspecification
  -> exact bias amplification.
```

This closes the joint stochastic-complexity obligation only for an unbounded
finite-dimensional linear Gaussian target with known variances and
nonadaptive allocation.

## 8. Claim boundary

The Gaussian linear model, generalized least squares, Gaussian Bayes lower
bound, and A/c-optimal design objectives are classical. No novelty is claimed
for them.

Version v0.70 does not establish:

- that a physical preference or reward channel is Gaussian or linear;
- that quotient coordinates are semantically valid;
- unknown-variance, heavy-tailed, dependent, adaptive, or strategic rates;
- optimal adaptive experiment design;
- policy safety rather than estimation of a declared margin;
- existence of a coherent scalar value object in humans or models; or
- resolution of ASMP-9.
