# ASMP-9 v0.45 theorem draft: decision-directed sample allocation

## 1. Registered setting

There are four targets, three binary queries

```text
root  : {0,1} versus {2,3}
left  : 0 versus 1
right : 2 versus 3,
```

and horizon two. Each query `q` has one shared symmetric flip parameter
`p_q`. A known-target calibration draw reveals a binary error indicator.
Because that indicator has the same Bernoulli law for every target, the
target-by-query acquisition table is sufficient through the pooled query
counts

```text
n = (n_root,n_left,n_right).
```

All counts are positive and sum to the frozen budget `N`.

The two decision problems are:

1. four-class zero-one identification; and
2. root-group zero-one loss, which distinguishes only `{0,1}` from `{2,3}`.

The center channel is the exact deterministic query library inherited from
v0.41. Every deterministic policy generator carries its center risk and
target-wise expected query occupancy.

## 2. Simultaneous empirical KL event

For a binary empirical law from `n_q` iid draws, the method of types gives

```text
Pr[KL(P_hat_q || P_q) >= epsilon]
  <= (n_q+1) exp(-n_q epsilon).
```

For `Q=3` and familywise error `alpha`, define the outward rational toll

```text
kappa(n_q)
  = ceil_1e-12(
      log(Q(n_q+1)/alpha) / n_q
    ).
```

A union bound gives, simultaneously for every query,

```text
KL(P_hat_q || P_q) <= kappa(n_q)
```

with probability at least `1-alpha`.

For a policy generator `pi`, target `theta`, and center-channel occupancy
`omega_pi(theta,q)`, the KL chain rule gives

```text
I_pi(theta;n)
  = sum_q omega_pi(theta,q) kappa(n_q).
```

Pinsker and the loss span `s(theta)` give the outward risk radius

```text
b_pi(theta;n)
  = s(theta)
    min(1,sqrt(I_pi(theta;n)/2)).
```

This is the v0.44 generator-specific box with data-acquisition counts made
explicit.

## 3. Exact finite allocation theorem

Let `G(n)` be the center risk generators with radii `b_pi(theta;n)`, and let
the perfect-revelation reference have zero radius. For each positive integer
allocation with total `N`, define

```text
U(n) = D(G_plus(n),{0}),
```

where `D` is the inherited exact directed upper-deficiency LP.

Because the allocation universe is finite,

```text
n_star in argmin_{n_q >= 1, sum n_q=N} U(n)
```

is exactly computable. Version v0.45 freezes `N=60`, so the universe contains

```text
C(59,2) = 1711
```

allocations per decision problem.

### Constructive bounds

The perfect center classification policy uses the root and exactly one branch
query. Uniform randomization over four terminal actions supplies the
no-information bound. Hence

```text
U_class(n)
  <= min(
       3/4,
       sqrt(
         (kappa(n_root)
          + max(kappa(n_left),kappa(n_right))) / 2
       )
     ).
```

For root-group loss, a perfect center policy uses only the root and uniform
terminal randomization supplies `1/2`:

```text
U_group(n)
  <= min(1/2,sqrt(kappa(n_root)/2)).
```

These are safe constructive bounds, not asserted to equal the exact LP at
every allocation. Burned development at `N=54` found 92 asymmetric
classification allocations where the first bound was conservative, while it
never underbounded the exact LP and selected the same unique optimum. The
registered `N=60` census independently tests that prediction.

### Matched control

For a synthetic policy that uses each of the three queries exactly once, the
information objective is

```text
kappa(n_root)+kappa(n_left)+kappa(n_right).
```

The registered exact integer census predicts that its unique optimum is the
uniform allocation. This distinguishes decision-directed allocation from a
generic preference for unequal counts.

## 4. Exact two-point lower benchmark

Let

```text
p_minus = 1/2-d,
p_plus  = 1/2+d.
```

For `n` iid Bernoulli draws, compute the exact rational equal-prior Bayes
testing error

```text
e_n(d) = (1-TV(Bin(n,p_minus),Bin(n,p_plus)))/2.
```

If a confidence set has coverage at least `1-alpha` under both points and
always has radius strictly below `d`, it induces a test with both errors at
most `alpha`. Therefore

```text
e_n(d) > alpha
```

certifies that such a uniform radius is impossible. Version v0.45 exhausts
`d=j/200` and reports the largest obstructed `d` for every count used by the
optimal and uniform designs.

This is a registered-grid two-point lower benchmark. It does not match the
constructive KL endpoint and therefore explicitly classifies the achieved
certificate as constructive rather than minimax.

## 5. Expected confirmation

Before exact `N=60` LP outcomes are read, the constructive calculations
predict:

| Problem | Predicted allocation | Constructive upper | Uniform allocation | Uniform upper |
|---|---:|---:|---:|---:|
| four-class | `(26,17,17)` | `0.589535161433` | `(20,20,20)` | `0.597447361697` |
| root-group | `(58,1,1)` | `0.265419024703` | `(20,20,20)` | `0.422459080858` |
| all-query serial control | `(20,20,20)` | information objective | `(20,20,20)` | same |

The exact confirmation is permitted to refute these predictions.

## 6. Claim boundary

This draft specializes classical finite-alphabet concentration, controlled
sensing, exact risk-polytope comparison, and two-point lower bounds. It may
establish a unique exact integer allocation for the frozen shared-flip
grammar. It does not establish optimal simultaneous constants, a general
minimax deficiency modulus, cell-specific allocation under target-dependent
channels, efficient policy enumeration, strategic misspecification, real
reward/value access, or ASMP-9 resolution.
