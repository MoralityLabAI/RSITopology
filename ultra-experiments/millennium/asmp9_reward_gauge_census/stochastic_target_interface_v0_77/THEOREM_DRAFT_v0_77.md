# ASMP-9 finite stochastic target interface v0.77

Status: **unregistered classical finite-hypothesis development**.

## Object

Let `X` be a finite parameter registry. Each parameter `x` has:

- a registered target label `T(x)`; and
- a known one-sample observation law `P_x` on a finite alphabet.

Samples are iid conditional on `x`. This is a finite stochastic extension of
the deterministic factorization distinction in v0.76.

## Theorem 1: population interface

If an oracle reveals the exact law, the target is recoverable iff:

```text
P_x = P_x' implies T(x) = T(x').
```

The observation law is representative-insensitive iff:

```text
T(x) = T(x') implies P_x = P_x'.
```

Both conditions give an exact stochastic target interface. As in v0.76,
target recoverability and representative leakage are separate questions.

## Theorem 2: finite-sample Hellinger bound

Define Hellinger affinity and squared Hellinger distance by:

```text
rho(P,Q) = sum_y sqrt(P(y) Q(y));
H2(P,Q)  = 1-rho(P,Q).
```

Use maximum likelihood over the finite parameter registry and return its target
label. Under true parameter `x`, comparison with a wrong-target parameter
`x'` has:

```text
Pr_x[L_(x') >= L_x] <= rho(P_x,P_(x'))^n.
```

This follows because on the likelihood-ratio event, the true product mass is
at most the geometric mean of the two product masses; summing gives product
affinity.

Therefore the worst-case target error obeys:

```text
max_x Pr_x[target error]
 <=
max_x sum_(x': T(x') != T(x)) rho(P_x,P_(x'))^n.
```

The bound is constructive and finite whenever every cross-target affinity is
strictly below one. It is a conservative union bound, not an exact minimax
rate.

## Theorem 3: TV misspecification stress

Suppose the actual one-sample law for the true parameter is within total
variation `epsilon` of its registered law, while the decoder remains frozen.
Then:

```text
TV(P_actual^n, P_registered^n)
 <= 1-(1-epsilon)^n.
```

Consequently:

```text
actual target error
 <= registered error bound + 1-(1-epsilon)^n,
```

capped at one.

This is a worst-case robustness bound. It exposes a real tradeoff: more iid
samples shrink the registered discrimination term but enlarge the accumulated
misspecification allowance. A nominal sample threshold is not automatically a
robust threshold.

## Frozen exact binary control

The development fixture uses:

```text
P = (9/10, 1/10)
Q = (1/10, 9/10)
alpha = 1/20.
```

Its affinity and gap are exact:

```text
rho(P,Q)=3/5;
H2(P,Q)=2/5.
```

For one competitor, the Hellinger union bound first falls below `1/20` at:

```text
n=6, bound=(3/5)^6=729/15625=0.046656.
```

The exact equal-prior binary Bayes error, computed from the rational binomial
count laws, first falls below `1/20` at:

```text
n=3, exact error=7/250=0.028.
```

The difference is reported explicitly: six is a certified sufficient count
for the generic bound, not the fixture's sharp sample complexity.

At the certified `n=6`, a per-sample TV stress of only `1/1000` gives the
worst-case penalty:

```text
1-(999/1000)^6,
```

which pushes the robustified upper bound above `1/20`. This does not prove an
adversary attains the bound; it shows the nominal certificate is not robust to
that registered misspecification ball.

## ASMP-9 consequence

Version v0.77 closes one finite stochastic access cell:

```text
known finite iid laws
+ finite target registry
-> population criterion, explicit finite-sample upper bound,
   exact binary calibration, and a misspecification penalty.
```

It also supplies a liveness rule: population identifiability is insufficient
for a finite-sample claim unless a positive cross-target distributional gap is
registered.

## Claim boundary

The laws, iid sampling, finite registry, target labels, and TV ball are assumed.
The result does not estimate those objects from human/model behavior, address
adaptive or dependent data, give a general minimax-optimal rate, or establish
the moral adequacy of the target. ASMP-9 remains unresolved.
