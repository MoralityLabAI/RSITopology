# ASMP-9 v0.28 draft: homogeneous interventions versus a calibrated numeraire

Status: development-only and unregistered.

## 1. Occupancy-query model

Let `r in R^p` be a reward vector. Every registered trajectory, policy, or
environment comparison supplies a known occupancy-difference row

```text
x_q in R^p
```

and an unknown strictly increasing symmetric response link produces

```text
P(Y_q=1)=F(x_q^T r).
```

The intervention may select `x_q` adaptively, but it has no direct access to
`r`.

## 2. Transition-only scale obstruction

Assume the link class is closed under positive rescaling. For every
`alpha>0`, define:

```text
r'=alpha r,
F'(t)=F(t/alpha).
```

Then for every possible occupancy direction:

```text
F'(x_q^T r')=F(x_q^T r).
```

The equality holds pathwise under adaptive querying, because identical past
laws induce the same next query distribution. No finite or infinite family of
reward-independent transition interventions can identify cardinal reward
scale under this link class.

This is not necessarily a safety failure when positive scale belongs to the
declared reward gauge. It is fatal only for targets—such as cardinal regret,
cross-system aggregation, or fixed-temperature response prediction—that
require that scale.

## 3. Unknown side-payment value is not a numeraire

Suppose a comparison includes `c` units of a new feature whose reward
coefficient `nu` is unknown:

```text
x_q^T r + c nu.
```

This is merely an additional reward coordinate. Scaling `(r,nu)` and
rescaling the unknown link preserves every law. Calling the feature “money,”
“tokens,” or “reward points” does not calibrate it mathematically.

## 4. Known numeraire breaks homogeneity

Now assume `c` is an externally calibrated return in the same declared units
as the target:

```text
P(Y_(q,c)=1)=F(x_q^T r+c).
```

Varying `c` across an interval containing `-x_q^T r` locates the indifference
threshold and recovers:

```text
y_q=x_q^T r.
```

This is exactly the v0.26 threshold operation applied to an occupancy
functional rather than one coordinate.

## 5. Necessary and sufficient quotient criterion

Stack the occupancy rows into `X`. Let `G` be the declared linear reward-gauge
subspace. Assume `G` is known and every row annihilates it:

```text
G subset ker(X).
```

Calibrated threshold access identifies `r` modulo exactly `G` if and only if:

```text
ker(X)=G.
```

Equivalently:

```text
rank(X)=p-dim(G).
```

Necessity is immediate: a vector in `ker(X)\G` changes reward outside the
declared gauge without changing any threshold. Sufficiency follows because
the recovered vector `Xr` determines the coset in `R^p/G`.

Any quotient basis `U` for `G^perp` gives the constructive system:

```text
XU theta = y.
```

The minimum number of independent occupancy directions is `p-dim(G)`.

## 6. Robust boundary

If threshold localization returns `y_hat=y+e`, least squares on the quotient
obeys:

```text
||theta_hat-theta||_2
  <= ||e||_2 / sigma_min(XU).
```

Thus:

- rank is the exact identification boundary;
- the smallest quotient singular value is the stability boundary; and
- v0.26's link-margin condition controls the cost of producing each entry of
  `y_hat`.

All three are necessary parts of a finite-sample access theorem.

## 7. Consequence for “environment realization”

Changing transition kernels, initial-state distributions, horizons, or policy
constraints can enrich the row span of `X` and eliminate shaping directions.
It cannot by itself create a known additive reward unit. The v0.26 offset is
realized only when the interface includes an externally calibrated
consequence whose coefficient is fixed outside the unknown reward vector.

This places v0.10 and v0.26 on one ledger:

```text
environment design controls ker(X);
numeraire calibration controls reward scale;
response margins control finite-sample cost.
```

## 8. Claim boundary

Linear inverse problems, occupancy measures, reward invariance, experimental
design, bisection, and numeraire normalization are classical. Novelty is not
claimed.

The theorem does not show that money or any concrete consequence has stable
known utility, that real interventions preserve the target reward semantics,
that arbitrary policies expose linear occupancy differences, or that ASMP-9
is resolved.

