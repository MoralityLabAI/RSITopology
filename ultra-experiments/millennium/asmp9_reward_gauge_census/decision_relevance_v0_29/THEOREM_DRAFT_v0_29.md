# ASMP-9 v0.29 draft: quotient error to policy regret

Status: development-only and unregistered.

## 1. Decision-compatible reward gauge

Let a finite policy family have occupancy vectors `mu_pi in R^p`. A declared
linear reward gauge `G` is decision-null for this family exactly when:

```text
g^T(mu_pi-mu_pi') = 0
```

for every `g in G` and every pair of policies. This condition is not optional:
if it fails, two reward representatives in one declared gauge class can rank
the policies differently, so a quotient-level policy certificate is
ill-posed.

## 2. Plug-in regret theorem

Let `r` be the true reward, `r_hat` an estimate, and:

```text
delta = inf_(g in G) ||r_hat-r-g||_2.
```

Let `pi_star` maximize `r^T mu_pi`, and let `pi_hat` maximize
`r_hat^T mu_pi`, using one frozen tie rule. If `G` is decision-null, then:

```text
Regret_r(pi_hat)
  <= delta ||mu_(pi_star)-mu_(pi_hat)||_2
  <= delta D,
```

where:

```text
D = max_(pi,pi') ||mu_pi-mu_pi'||_2.
```

The first inequality is sharp, including on a two-policy, two-feature family
with a constant reward gauge.

## 3. Policy-identity certificate

For every competitor `pi`, define the estimated margin:

```text
m_pi = r_hat^T(mu_(pi_hat)-mu_pi).
```

If:

```text
m_pi > delta ||mu_(pi_hat)-mu_pi||_2
```

for every competitor, then `pi_hat` is also uniquely optimal under `r`.
Equality is inconclusive.

## 4. Composition with calibrated occupancy access

Version v0.28 gives:

```text
delta <= ||e||_2 / sigma_min(XU)
```

for localized occupancy error `e` and an orthonormal quotient basis `U`.
Therefore:

```text
Regret_r(pi_hat)
  <= D ||e||_2 / sigma_min(XU).
```

This is the missing decision-relevance handoff: measurement quality, access
geometry, and policy-family diameter enter as separate factors.

## 5. The positive-scale fork

Positive reward scale is irrelevant to a fixed-MDP argmax policy:

```text
argmax_pi alpha r^T mu_pi = argmax_pi r^T mu_pi, alpha>0.
```

It is not irrelevant to a fixed cardinal claim. The numerical regret of a
fixed policy scales by `alpha`, so two v0.28-observationally equivalent
reward-link pairs can fall on opposite sides of a fixed regret threshold.

Thus:

- policy selection may be well-defined on the positive-scale quotient;
- a fixed-unit regret certificate requires a calibrated scale; and
- the declared downstream decision target determines whether scale
  nonidentification matters.

## 6. Proof

Optimality of `pi_hat` under `r_hat` gives:

```text
r_hat^T(mu_(pi_star)-mu_(pi_hat)) <= 0.
```

For any `g in G`, decision-nullness gives:

```text
g^T(mu_(pi_star)-mu_(pi_hat)) = 0.
```

Therefore:

```text
Regret_r(pi_hat)
  = r^T(mu_(pi_star)-mu_(pi_hat))
  <= (r-r_hat-g)^T(mu_(pi_star)-mu_(pi_hat)).
```

Cauchy-Schwarz and minimization over `g` prove the bound. Applying the same
argument to each estimated policy margin gives the identity certificate.

For sharpness, take policy occupancies `(1,0)` and `(0,1)`, gauge
`span(1,1)`, true reward `(-a,a)`, estimate `(0,0)`, and a tie rule selecting
the first policy. The regret is `2a`, while both the quotient error and policy
diameter are `sqrt(2)` multiples whose product is exactly `2a`.

## 7. Claim boundary

Downstream-task invariances in reward learning, feature-expectation performance
bounds, plug-in optimization inequalities, and robust argmax margins are
established mathematics. Novelty is not claimed.

This theorem does not show that the reward estimate is correct, that the policy
family contains a safe policy, that small reward regret captures all safety
loss, or that ASMP-9 is resolved.
