# Sharp informative-fiber availability under a probability interior

## Setup

Let `C_k` be a consistently oriented cycle. Each edge receives `n`
independent Bernoulli comparisons with success probability:

```text
epsilon <= p_e <= 1-epsilon,
0 < epsilon <= 1/2.
```

The realized balance fiber is informative exactly when it contains at least
two count vectors. As in v0.14, its probability is:

```text
A(p)
  = product_e [1-(1-p_e)^n]
  + product_e [1-p_e^n]
  - product_e [1-p_e^n-(1-p_e)^n].
```

## Lemma 1: the continuous minimum occurs at box vertices

Hold every probability except `p_i` fixed. Write:

```text
u(p)=1-(1-p)^n,
v(p)=1-p^n,
w(p)=u(p)+v(p)-1.
```

Then `A` has the form:

```text
A(p_i)=c_0+c_1 u(p_i)+c_2 v(p_i),
```

where:

```text
c_1 >= 0,
c_2 >= 0.
```

For `n>=2`:

```text
d^2 A / d p_i^2
  = -n(n-1)
    [c_1(1-p_i)^(n-2)+c_2 p_i^(n-2)]
  <= 0.
```

For `n=1` the function is affine. Thus `A` is separately concave in every
coordinate. Replacing one coordinate by an endpoint cannot increase its
minimum. Iterating over coordinates proves that a global minimum on the
probability box occurs at:

```text
p_e in {epsilon,1-epsilon}.
```

## Lemma 2: the worst vertex is the most even endpoint split

Define:

```text
a=(1-epsilon)^n,
b=epsilon^n,
x=1-a,
y=1-b,
z=1-a-b.
```

At a vertex with `j` low-probability edges and `k-j` high-probability edges:

```text
A_j=x^j y^(k-j)+y^j x^(k-j)-z^k.
```

Because `0<=x<=y`, the varying part is proportional to:

```text
r^j+r^(k-j),  r=y/x >= 1.
```

This symmetric discrete-convex expression is minimized when `j` is nearest
to `k/2`.

## Theorem 1: exact minimax availability

Let:

```text
m=floor(k/2),
h=ceil(k/2).
```

Then:

```text
min over p in [epsilon,1-epsilon]^k A(p)
  = x^m y^h + y^m x^h - z^k.
```

The bound is attained by assigning `epsilon` to `m` edges and `1-epsilon` to
the other `h` edges, or vice versa. It is therefore a sharp minimax identity,
not a union bound.

The one-high, `k-1`-low drift used to demonstrate v0.14's unbounded-nuisance
collapse is generally not the worst bounded-interior nuisance. For `k>=4`,
the balanced endpoint split is the relevant adversarial control.

## Corollary 1: exact equal-count trial threshold

For target availability `1-delta`, define:

```text
n_star(k,epsilon,delta)
  = min {n>=1 : A_min(k,n,epsilon) >= 1-delta}.
```

This is both necessary and sufficient for the equal-count design to guarantee
the target uniformly over the declared probability interior.

## Corollary 2: asymptotic scaling

For fixed `k` and `0<epsilon<1/2`, let:

```text
a_n=(1-epsilon)^n.
```

Since `epsilon^n/a_n -> 0`, expansion of the exact formula gives:

```text
1-A_min(k,n,epsilon)
  = m h a_n^2 [1+o(1)].
```

Therefore, as `delta -> 0`:

```text
n_star(k,epsilon,delta)
  = log(m h / delta)
    / [2 log(1/(1-epsilon))]
    + O(1).
```

The exponent `2n` is the operational gain hidden by the v0.14 one-sided
no-zero lower bound: an uninformative fiber requires both a zero edge and a
full edge.

## Unequal allocation remains open

For edge-specific counts `n_e`, the same separate-concavity argument reduces
the probability adversary to endpoint assignments. The remaining total-budget
problem is:

```text
max over positive integers n_e with sum n_e=N
min over endpoint assignments A(n_1,...,n_k).
```

Finite development censuses suggest that counts differing by at most one are
optimal. This draft does not claim the general balancing theorem without a
pairwise-exchange or majorization proof.

## Claim boundary

This is elementary probability and discrete optimization for an equal-count
independent Bernoulli cycle experiment. It is not a general optimal-design
theorem for Bradley-Terry models, a behavioral validation, an adaptive
allocation result, or an ASMP-9 resolution.
