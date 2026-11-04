# Gaussian liveness and sample threshold for path-factorization tests

Status: **proved classical specialization; development-only and unregistered**.

## 1. Why v0.71 needs a separate liveness gate

Version v0.71 separates two population questions:

```text
reward identification:
  does the path-incidence design identify edge-reward coordinates?

Markov factorization:
  do the observed path values lie in that design's column space?
```

These require different ranks. A square full-rank path design can identify a
unique edge reward for every possible observed table, making Markov
factorization impossible to falsify. A redundant path relation is required
for lack-of-fit testing.

## 2. Known-variance Gaussian path model

Freeze `m` registered nonempty paths and `d` edge coordinates. Let

```text
X in R^(m x d)
```

be their path-edge incidence matrix. For each path `p`, collect `n_p`
independent observations with known per-observation variance `sigma_p^2`.
The sample-mean vector has law:

```text
y_bar ~ Normal(mu,V),
V = diag(sigma_p^2/n_p).
```

The Markov null is:

```text
H0: mu in col(X).
```

## 3. Falsifiability rank

### Theorem 1

Define:

```text
rank_reward = rank(X),
nu = m-rank(X).
```

Then:

1. all registered edge coordinates are identifiable exactly when
   `rank(X)=d`;
2. Markov factorization is testable exactly when `nu>0`; and
3. both are possible exactly when `rank(X)=d<m`.

If `nu=0`, every possible mean vector lies in `col(X)`. No amount of repeated
sampling can distinguish Markov factorization from an arbitrary mean table on
that path set.

This is an instrument-liveness statement, not a low-power statement.

## 4. Exact residual law

Whiten:

```text
z = V^(-1/2) y_bar,
Z = V^(-1/2) X.
```

Let `P_Z` be the orthogonal projector onto `col(Z)` and define:

```text
T = ||(I-P_Z)z||_2^2.
```

### Theorem 2

Under the Markov null:

```text
T ~ chi_square(nu).
```

For arbitrary fixed mean `mu`:

```text
T ~ noncentral_chi_square(nu,lambda),

lambda =
  min_r (mu-Xr)^T V^-1 (mu-Xr).
```

Therefore the size-`alpha` residual test rejects when:

```text
T > chi_square_quantile(nu,1-alpha),
```

and has exact power:

```text
P_reject =
  survival_noncentral_chi_square(
    chi_square_quantile(nu,1-alpha);
    nu,
    lambda
  ).
```

#### Proof

The whitened residual is Gaussian with covariance `I-P_Z` and mean
`(I-P_Z)V^-1/2 mu`. The projector is symmetric, idempotent, and has rank
`nu`. An orthogonal basis diagonalizes it into `nu` identity coordinates and
zeros, yielding the central or noncentral chi-square law.

This is the classical known-variance Gaussian linear-model lack-of-fit test.

## 5. Equal-allocation sample threshold

When every path receives `n` observations with common sample variance
`sigma^2`,

```text
V = (sigma^2/n) I
```

and:

```text
lambda =
  (n/sigma^2)
  dist(mu,col(X))_2^2.
```

Thus the exact minimum equal repeat count is the first integer `n` whose
noncentral chi-square survival probability clears the frozen target power.
No asymptotic normal approximation is needed.

## 6. Frozen reconvergent fixture

The four nonempty paths from v0.71 are ordered:

```text
a, b, a/z, b/z.
```

Their incidence matrix over edges `(a,b,z)` is:

```text
X =
  [1 0 0
   0 1 0
   1 0 1
   0 1 1].
```

It has:

```text
rank(X)=3,
nu=1,
primitive left-null contrast=(1,-1,-1,1).
```

The planted interaction mean:

```text
mu=(0,0,1,0)
```

has exact squared distance:

```text
dist(mu,col(X))^2 = 1/4.
```

With:

```text
sigma^2=1,
alpha=0.05,
target power=0.80,
```

the distribution-exact noncentral-chi-square calculation, evaluated
independently at 80 decimal digits for the boundary cells, gives:

```text
31 repeats/path -> power 0.7950080284  (fails);
32 repeats/path -> power 0.8074304194  (passes).
```

Monotonicity in the noncentrality parameter and the strict high-precision
boundary inequalities make `32` the smallest equal repeat count under the
frozen model and effect.

## 7. Matched liveness control

Delete one of the four path rows. The remaining `3 x 3` design has full edge
rank:

```text
rank(X_reduced)=3,
nu_reduced=0.
```

It still identifies one unique edge-reward vector from any exact three-path
table, but it can never test whether that reward generalizes to the missing
path. Reporting a successful factorization test on this design would be
vacuous.

This is the path-valued analogue of the liveness certificates already
required for discrete holonomy tests.

## 8. ASMP-9 consequence

Versions v0.71-v0.72 now provide:

```text
population existence:
  f in col(X);

exact no-go witness:
  a in ker(X^T), a^T f != 0;

test liveness:
  residual dimension nu>0;

known-variance sample threshold:
  exact noncentral chi-square power;

replacement on failure:
  endpoint/time-respecting history quotient.
```

This closes one noisy finite branch of the history replacement problem.

## 9. Claim boundary

Linear-model residual tests, chi-square laws, and noncentral power
calculations are classical. No novelty is claimed.

Version v0.72 assumes:

- a complete frozen path design;
- independent Gaussian observations;
- known variances;
- fixed nonadaptive equal allocation in the headline threshold; and
- a fixed alternative effect.

It does not cover unknown variance, missing-not-at-random paths, adaptive
querying, multiple testing over selected interactions, strategic answers,
physical acquisition, moral validity, or resolution of ASMP-9.
