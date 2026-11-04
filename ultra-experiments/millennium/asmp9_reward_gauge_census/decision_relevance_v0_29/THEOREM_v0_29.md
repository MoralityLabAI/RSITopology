# Quotient reward error to policy regret

## Setting

Let a finite policy family have feature-occupancy vectors
`mu_pi in R^p`. Let `G` be a declared linear reward-gauge subspace.

The gauge is decision-null on the policy family when:

```text
g^T(mu_pi-mu_pi') = 0
```

for every `g in G` and every pair of policies. This precondition is
necessary: if it fails, two reward representatives in one declared gauge
class can rank the registered policies differently.

## Theorem

### A. Plug-in regret bound

Let `r` be the true reward and `r_hat` an estimate. Define the Euclidean
quotient error:

```text
delta = inf_(g in G) ||r_hat-r-g||_2.
```

Let `pi_star` maximize `r^T mu_pi`, and let `pi_hat` maximize
`r_hat^T mu_pi` under one fixed tie rule. If `G` is decision-null, then:

```text
Regret_r(pi_hat)
  <= delta ||mu_(pi_star)-mu_(pi_hat)||_2
  <= delta D,
```

where:

```text
D = max_(pi,pi') ||mu_pi-mu_pi'||_2.
```

The selected-pair and global-diameter inequalities are sharp. For example,
take policies with occupancies `(1,0)` and `(0,1)`, gauge `span(1,1)`, true
reward `(-a,a)`, estimated reward `(0,0)`, and a tie rule choosing the first
policy. The regret and both bounds equal `2a`.

### B. Policy-identity certificate

For every competitor `pi`, define the estimated margin:

```text
m_pi = r_hat^T(mu_(pi_hat)-mu_pi).
```

If:

```text
m_pi > delta ||mu_(pi_hat)-mu_pi||_2
```

for every competitor, then `pi_hat` is uniquely optimal under `r`. Equality
is inconclusive.

### C. Composition with calibrated occupancy access

Version v0.28 gives:

```text
delta <= ||e||_2 / sigma_min(XU)
```

for localized occupancy error `e`, calibrated row matrix `X`, and an
orthonormal quotient basis `U`. Hence:

```text
Regret_r(pi_hat)
  <= D ||e||_2 / sigma_min(XU).
```

Measurement error, quotient conditioning, and policy-family diameter therefore
enter as separate multiplicative factors.

### D. Positive-scale fork

Positive reward scale is irrelevant to a fixed-MDP argmax:

```text
argmax_pi alpha r^T mu_pi = argmax_pi r^T mu_pi,  alpha>0.
```

It is not irrelevant to a fixed cardinal claim. The numerical regret of a
fixed policy scales by `alpha`, so two observationally equivalent
reward-link pairs from the v0.28 homogeneous access model can lie on opposite
sides of one fixed-unit regret threshold.

Thus positive scale may be part of the gauge for policy identity while
remaining load-bearing for a cardinal loss certificate. The downstream
decision target determines which quotient is legitimate.

## Proof

Optimality of `pi_hat` under `r_hat` gives:

```text
r_hat^T(mu_(pi_star)-mu_(pi_hat)) <= 0.
```

For every `g in G`, decision-nullness gives:

```text
g^T(mu_(pi_star)-mu_(pi_hat)) = 0.
```

Therefore:

```text
Regret_r(pi_hat)
  = r^T(mu_(pi_star)-mu_(pi_hat))
  <= (r-r_hat+g)^T(mu_(pi_star)-mu_(pi_hat)).
```

The sign of `g` is immaterial because `G` is a subspace. Cauchy-Schwarz and
minimization over `g` prove the selected-pair bound; maximizing the occupancy
difference proves the diameter bound.

For the policy-identity statement, write the true margin against each
competitor as its estimated margin plus an error inner product. The same
quotient Cauchy-Schwarz bound is strictly smaller than the registered margin,
so every true margin is positive.

The composition result substitutes the v0.28 quotient reconstruction bound.
The scale statement follows by multiplying every policy value and regret by
the same positive scalar.

## Claim boundary

Feature-expectation performance bounds, downstream-task reward invariances,
quotient norms, Cauchy-Schwarz, and robust argmax margins are established
mathematics. Novelty is not claimed.

This theorem does not show that a learned reward estimate is correct; that the
registered policy family contains a safe policy; that reward regret captures
all safety loss; that an environment supplies calibrated occupancy access; or
that ASMP-9 is resolved.
