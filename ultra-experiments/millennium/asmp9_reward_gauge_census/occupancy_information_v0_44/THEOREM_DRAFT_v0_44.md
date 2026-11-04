# ASMP-9 v0.44 theorem draft: information belongs to risk generators

## 1. Failure of the scalar occupancy proposal

Let `kappa(theta,q)` upper-bound the directed one-step KL between a center and
perturbed query cell. For a deterministic adaptive policy `pi`, define:

```text
I_pi(theta)
  = E_center,pi [
      sum_{t=1}^h kappa(theta,q_t(H_{t-1}))
    ].
```

The transcript KL chain rule gives:

```text
KL(P_pi,theta || P_hat_pi,theta) <= I_pi(theta).
```

If every query is repeatable and the policy class is unrestricted, then:

```text
sup_pi I_pi(theta) = h max_q kappa(theta,q).
```

The upper bound is immediate; equality is attained by repeating a maximizing
query. Consequently, taking the supremum before solving the decision problem
reproduces the v0.43 worst-cell scalar and cannot improve it.

## 2. Generator-specific information occupancy

Fix a finite decision problem with target-wise loss spans `s(theta)`. Every
deterministic policy tree `pi` generates:

```text
r_pi(theta) = expected terminal loss under the center channel
I_pi(theta) = expected accumulated information toll
b_pi(theta) = s(theta) min(1, sqrt(I_pi(theta)/2)).
```

Pinsker implies that the corresponding perturbed-channel policy has risk
`r'_pi` satisfying:

```text
|r'_pi(theta)-r_pi(theta)| <= b_pi(theta)
```

for every target. Randomized policies are convex mixtures of deterministic
generators, so the policy-specific boxes extend to the complete upper risk
polytope.

The implementation replaces exact KL with the rational upper bound:

```text
KL(P||Q) <= chi2(P||Q).
```

Every square root is rounded outward to a registered rational grid. The
resulting boxes are conservative and exact as serialized.

## 3. Robust directed-deficiency interval

Let source generator `i` have center `g_i` and coordinate radius `b_i`. Let
reference generator `j` have center `f_j` and radius `c_j`. Define the
coordinate-wise endpoint sets:

```text
G_minus = {g_i-b_i}
G_plus  = {g_i+b_i}
F_minus = {f_j-c_j}
F_plus  = {f_j+c_j}.
```

For one registered finite decision type, directed upper deficiency is:

```text
D(G,F)
  = max_j min_{w in simplex(G)}
      max_theta [
        sum_i w_i g_i(theta) - f_j(theta)
      ],
```

with nonnegative deficiency slack.

For every mixture `w` and reference generator `j`, coordinate monotonicity
gives:

```text
sum_i w_i (g_i-b_i) - (f_j+c_j)
  <=
sum_i w_i g'_i - f'_j
  <=
sum_i w_i (g_i+b_i) - (f_j-c_j).
```

Taking `max_theta`, then `min_w`, then `max_j` preserves the inequalities:

```text
D(G_minus,F_plus)
  <= D(G_true,F_true)
  <= D(G_plus,F_minus).
```

Both endpoints are ordinary exact rational deficiency LPs. This is the
generator-specific robust-containment theorem.

## 4. Why it can be strictly sharper

A uniform pre-optimization certificate gives every source generator the same
target radius:

```text
b_uniform(theta)
  = s(theta) min(
      1,
      sqrt(h max_q kappa(theta,q)/2)
    ).
```

The generator-specific interval can be strictly smaller because the
mixture selected by the containment LP may use policies with
`I_pi(theta) << h max_q kappa(theta,q)`.

It can also coincide with the uniform interval. No strict improvement is
claimed when every decision-relevant policy must spend the full information
budget.

## 5. Registered matched fixture

The fixture reuses the four-target query tree from v0.41:

```text
root  : separates {0,1} from {2,3}
left  : separates 0 from 1
right : separates 2 from 3.
```

The root channel is unchanged. Every row of `left` and `right` receives a
symmetric flip probability:

```text
eta in {1/100,1/50,1/20,1/10}.
```

Relative to the deterministic center:

```text
chi2 = eta/(1-eta)
```

for every target on `left` and `right`, while root information cost is zero.

### Four-class identification

At `eta=1/20`, the zero-risk center policy is:

```text
root(left(A0,A1), right(A2,A3)).
```

It uses exactly one uncertain leaf query per target:

```text
I_pi(theta) = 1/19.
```

The policy-specific upper deficiency radius is the outward rational enclosure
of:

```text
sqrt(1/38) = 0.162221...
```

namely:

```text
0.162221421131.
```

The uniform horizon-two radius instead encloses:

```text
sqrt(1/19) = 0.229415...
```

as:

```text
0.229415733871.
```

The actual perturbed deficiency is exactly `1/20`, contained by both, with
strictly smaller policy-specific width.

### Root-group decision

For the loss type that asks only which root group contains the target, the
policy:

```text
root(A0,A1)
```

has zero risk and zero information occupancy. Therefore the policy-specific
interval is exactly `[0,0]`, matching the perturbed deficiency. The uniform
certificate remains `[0,0.229415733871]` because it prices unrelated leaf
queries.

The contrast is decision-relative: the same channel library justifies
different uncertainty because the registered loss types need different
policies.

## 6. Scope

Version v0.44:

- exactly enumerates finite deterministic policy risk/information pairs;
- supports repeatable queries and registered pathwise query budgets;
- uses rational chi-square upper bounds and outward square-root enclosures;
- proves generator-specific robust directed-deficiency containment;
- checks uncertain source and reference generator boxes; and
- demonstrates strict, decision-dependent improvement over a uniform radius.

It does not:

- produce optimal KL confidence regions from data;
- prove that Pinsker boxes are the sharp deficiency modulus;
- make exponential policy-tree enumeration efficient;
- handle coupled/nonrectangular channel uncertainty;
- cover strategic or misspecified demonstrators;
- validate a real behavioral channel; or
- resolve ASMP-9.
