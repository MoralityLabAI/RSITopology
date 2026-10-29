# Sharp informative-fiber availability under a probability interior

## Setup

Let `C_k` be a consistently oriented cycle. Edge `e` receives `n`
independent Bernoulli comparisons with success probability

```text
epsilon <= p_e <= 1-epsilon,
0 <= epsilon <= 1/2.
```

The realized balance fiber is informative exactly when it contains at least
two count vectors. Its probability is

```text
A(p)
  = product_e [1-(1-p_e)^n]
  + product_e [1-p_e^n]
  - product_e [1-p_e^n-(1-p_e)^n].
```

## Lemma 1: a minimum occurs at a box vertex

Hold every probability except `p_i` fixed and define

```text
u(p)=1-(1-p)^n,
v(p)=1-p^n,
w(p)=u(p)+v(p)-1.
```

Expanding the three products gives

```text
A(p_i)=c_0+c_1 u(p_i)+c_2 v(p_i),
```

where `c_1,c_2>=0`. For `n>=2`,

```text
d^2 A / d p_i^2
  = -n(n-1)
    [c_1(1-p_i)^(n-2)+c_2 p_i^(n-2)]
  <= 0.
```

For `n=1`, the coordinate section is affine. Thus `A` is separately concave.
Replacing one coordinate at a time by an endpoint cannot increase the
minimum. A global minimum on the box is therefore attained at

```text
p_e in {epsilon,1-epsilon}.
```

## Lemma 2: the worst vertex has the most even endpoint split

Set

```text
a=(1-epsilon)^n,
b=epsilon^n,
x=1-a,
y=1-b,
z=1-a-b.
```

At a vertex with `j` low-probability edges,

```text
A_j=x^j y^(k-j)+y^j x^(k-j)-z^k.
```

Because `0<=x<=y`, write `r=y/x>=1` when `x>0`. The varying factor is

```text
r^j+r^(k-j),
```

a symmetric discrete-convex sequence minimized at the integer or integers
nearest `k/2`. The `x=0` boundary follows directly from the displayed
formula.

## Theorem 1: exact equal-count minimax availability

Let

```text
m=floor(k/2),
h=ceil(k/2).
```

Then

```text
min over p in [epsilon,1-epsilon]^k A(p)
  = x^m y^h + y^m x^h - z^k.
```

The bound is attained by assigning `epsilon` to `m` edges and
`1-epsilon` to the remaining `h` edges, or vice versa. It is a sharp minimax
identity, not a union bound.

## Corollary 1: exact equal-count trial threshold

For target availability `1-delta`, define

```text
n_star(k,epsilon,delta)
  = min {n>=1 : A_min(k,n,epsilon) >= 1-delta}.
```

For `epsilon>0`, this is necessary and sufficient for the equal-count design
to guarantee the target uniformly over the declared probability interior.
For `epsilon=0`, the worst-case availability is zero for every finite `n`.

## Corollary 2: asymptotic scaling

For fixed `k` and `0<epsilon<1/2`, put `a_n=(1-epsilon)^n`. Since
`epsilon^n/a_n -> 0`,

```text
1-A_min(k,n,epsilon)
  = floor(k/2) ceil(k/2) a_n^2 [1+o(1)].
```

Therefore, as `delta -> 0`,

```text
n_star(k,epsilon,delta)
  = log(floor(k/2) ceil(k/2) / delta)
    / [2 log(1/(1-epsilon))]
    + O(1).
```

## Unequal allocation is not proved

For edge-specific counts `n_e`, separate concavity still reduces the
probability adversary to endpoint assignments. It does not by itself solve

```text
max over positive integers n_e with sum n_e=N
min over endpoint assignments A(n_1,...,n_k).
```

The registered unequal-count grid is a finite falsification target for the
balancing conjecture. Passing it cannot establish the general theorem.

## Scope

This is an elementary exact result for independent Bernoulli counts on an
oriented cycle. It is not a general Bradley-Terry optimal-design theorem,
an adaptive allocation theorem, a behavioral validation, or an ASMP-9
resolution.
