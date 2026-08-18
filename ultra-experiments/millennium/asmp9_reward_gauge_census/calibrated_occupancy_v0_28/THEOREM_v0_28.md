# Calibrated occupancy access theorem

## Setting

Let the reward parameter be `r in R^p`. A reward-independent intervention
chooses a known occupancy-difference row `x in R^p` and observes a binary
population law

```text
P(Y=1 | x) = F(x^T r).
```

The link `F` is strictly increasing, satisfies `F(0)=1/2`, and belongs to a
class closed under positive rescaling:

```text
F_alpha(t) = F(t/alpha),  alpha > 0.
```

A deterministic adaptive experiment may choose its next row as an arbitrary
function of the preceding binary transcript. Let `G` be a declared linear
reward-gauge subspace.

## Theorem

### A. Homogeneous interventions do not identify positive scale

For every `alpha>0`, the parameter-link pairs

```text
(r, F)  and  (alpha r, F_alpha)
```

induce identical laws for every reward-independent occupancy row. They also
induce identical finite transcript laws under every deterministic adaptive
row-selection policy.

### B. An unknown-valued side feature is not a numeraire

Suppose each query may add `c` units of a feature with unknown reward
coefficient `nu`:

```text
P(Y=1 | x,c) = F(x^T r + c nu).
```

Then `(r,nu,F)` and `(alpha r,alpha nu,F_alpha)` remain observationally
equivalent for every positive `alpha`. Naming the feature money, tokens, or
reward points does not calibrate its value.

### C. A known additive consequence localizes occupancy values

Suppose instead that the experiment can add a known consequence `c`, measured
in the same declared cardinal units as the target:

```text
P(Y=1 | x,c) = F(x^T r + c).
```

If the allowed offset interval contains `-x^T r`, then the unique offset at
which the response probability is `1/2` is

```text
c_star = -x^T r.
```

Thus a population threshold query recovers `x^T r`. If only the sign relative
to `1/2` is used, bisection over radius `B` localizes the value to absolute
error `eta` in at most

```text
ceil(log2(B/eta))
```

queries, using the interval convention of the registered implementation.

### D. Exact quotient-identification criterion

Stack localized occupancy rows into a matrix `X`. Assume every row is
gauge-invariant:

```text
G subset ker(X).
```

Then the calibrated experiment identifies `r` modulo exactly `G` if and only
if

```text
ker(X) = G.
```

Equivalently,

```text
rank(X) = p - dim(G).
```

In particular, at least `p-dim(G)` independent scalar occupancy functionals
are necessary. They are sufficient whenever the allowed occupancy-row family
contains a matrix with that quotient rank.

### E. Robust quotient bound

Let `U` have orthonormal columns spanning `G^perp`, let

```text
y = X r = X U theta,
```

and suppose the localized vector is `y_hat=y+e`. If `ker(X)=G`, the quotient
least-squares estimate satisfies

```text
||theta_hat-theta||_2
  <= ||e||_2 / sigma_min(XU).
```

Exact rank is therefore the identifiability boundary, while the smallest
quotient singular value is the Euclidean stability boundary.

### F. Finite deterministic MDP realization

Every finite integer matrix `X in Z^(q x p)` is the occupancy-difference matrix
of one finite deterministic feature MDP with:

- one query initial state per row;
- two first actions per query;
- disjoint deterministic feature-emission paths;
- one common finite horizon; and
- a zero-reward padding transition.

For row `x_i`, place `max(x_ij,0)` copies of feature `j` on the positive path
and `max(-x_ij,0)` copies on the negative path. Pad both paths to

```text
H = max(1, max_i sum_j max(x_ij,0),
           max_i sum_j max(-x_ij,0)).
```

The positive-minus-negative feature occupancy is exactly `x_i`. This is an
existence construction inside the declared access class; it does not show that
a pre-existing environment exposes an arbitrary requested row.

## Proof

For A, for every row `x`,

```text
F_alpha(x^T(alpha r))
  = F((alpha x^T r)/alpha)
  = F(x^T r).
```

For an adaptive policy, assume the transcript laws agree through time `t`.
The same realized history selects the same next row, and the displayed
identity gives the same conditional Bernoulli law. Induction gives equality
of every finite transcript distribution.

For B, replace `r` and `nu` by their `alpha` multiples. The complete scalar
argument is multiplied by `alpha`, which `F_alpha` cancels.

For C, strict monotonicity and `F(0)=1/2` imply

```text
F(x^T r+c)=1/2  iff  x^T r+c=0.
```

Bisection follows from monotonicity and interval coverage.

For D, if `ker(X)` contains `h` outside `G`, then `r` and `r+h` give the same
localized vector but different quotient classes. Conversely, if
`ker(X)=G`, equality `Xr=Xr'` implies `r-r' in G`. Rank-nullity gives the
equivalent rank statement and the scalar-query lower bound.

For E, full quotient rank makes `(XU)^+` well defined on the quotient. Hence

```text
theta_hat-theta = (XU)^+ e
```

and the operator norm of the pseudoinverse is
`1/sigma_min(XU)`.

For F, the stated path construction has one occurrence difference per
integer coefficient. Padding adds zero reward and changes no occupancy
difference. All transitions, initial states, actions, and path lengths are
chosen without access to `r`.

## Access ledger

```text
environment or policy design  -> row span and ker(X)
known cardinal numeraire      -> positive reward scale
response margin               -> finite-sample threshold cost
sigma_min(XU)                 -> quotient error amplification
```

## Claim boundary

The ingredients are classical linear inverse problems, reward invariance,
occupancy measures, bisection, and numeraire normalization. Novelty is not
claimed.

The result does not establish that a practical consequence has stable known
cardinal utility, that a real intervention preserves reward semantics, that a
given environment exposes the required occupancy rows, that human or model
responses satisfy the declared link class, or that ASMP-9 is resolved.
