# Balanced allocation is the maximin informative-fiber design

## Setup

Let `C_k` be a consistently oriented cycle with `k>=3`. Edge `i` receives
`n_i>=1` independent Bernoulli comparisons, with

```text
sum_i n_i = N
```

and

```text
epsilon <= p_i <= 1-epsilon,
0 < epsilon <= 1/2.
```

Write

```text
r=1-epsilon,  s=epsilon,
x_t=1-r^t,
y_t=1-s^t,
z_t=1-r^t-s^t.
```

As in v0.15, separate concavity reduces nature's continuous probability
choice to endpoint labels. At a low endpoint an edge contributes `(x_t,y_t)`
to the no-zero and no-full products; at a high endpoint the pair is swapped.
The interior factor is always `z_t`.

For allocation `n`, define

```text
F(n)
  = min over endpoint labels
      [product(no-zero)
       + product(no-full)
       - product(interior)].
```

The design problem is to maximize `F(n)` over positive integer allocations
with total `N`.

## Lemma 1: order of the endpoint ratios

The ratio

```text
q_t=y_t/x_t
```

is nonincreasing in `t`.

One proof extends `t` to the positive reals. For `0<u<1`,

```text
d/dt log(1-u^t)
  = -u^t log(u)/(1-u^t).
```

At fixed `t`, this derivative is increasing in `u`, because after setting
`v=u^t` it is proportional to

```text
-v log(v)/(1-v),
```

whose derivative has numerator `v-1-log(v)>=0`. Since `s<=r`,

```text
d/dt log q_t <= 0.
```

Thus for `a<=b`,

```text
x_a y_b <= y_a x_b.
```

## Lemma 2: the pairwise nuisance game

Fix two edge counts `a<=b-2` and fix the endpoint labels of every other edge.
Let

```text
U=product(other no-zero factors),
V=product(other no-full factors),
W=product(other interior factors),
M=max(U,V),
m=min(U,V).
```

Then

```text
0 <= W <= m <= M.
```

Minimizing over the four endpoint-label choices on the selected pair gives

```text
min(S_ab,O_ab),
```

where the best same-label choice is

```text
S_ab
  = M x_a x_b + m y_a y_b - W z_a z_b,
```

and the best opposite-label choice is

```text
O_ab
  = M x_a y_b + m y_a x_b - W z_a z_b.
```

The coefficient ordering follows from `x_t<=y_t` and Lemma 1.

## Lemma 3: balancing improves the same-label branch

The sequences `x_t`, `y_t`, and `z_t` are strictly log-concave on their
positive ranges. For example, each is the restriction of a positive concave
function:

```text
1-u^t
```

for `x_t,y_t`, and

```text
1-r^t-s^t
```

for `z_t`. A positive concave function is log-concave. The `z_1=0` boundary
is checked directly.

Define

```text
E_ab=x_a x_b+y_a y_b-z_a z_b.
```

Direct expansion gives

```text
E_ab=1-r^a s^b-s^a r^b.
```

If `d=b-a>=2`, then

```text
E_(a+1,b-1)-E_(a,b)
  =(rs)^a (r-s)(r^(d-1)-s^(d-1))
  >=0.
```

Now decompose

```text
S_ab
  = W E_ab
    +(m-W)(x_a x_b+y_a y_b)
    +(M-m)x_a x_b.
```

Every coefficient is nonnegative, and every displayed factor is
nondecreasing under `(a,b)->(a+1,b-1)`. Therefore

```text
S_(a+1,b-1) >= S_ab.
```

## Lemma 4: balancing improves the opposite-label branch

Define

```text
D_ab=x_a y_b+y_a x_b-z_a z_b.
```

Expansion gives the sum-only identity

```text
D_ab=1-r^(a+b)-s^(a+b),
```

so `D_ab` is invariant under balancing.

Also,

```text
x_(a+1)y_(b-1)-x_a y_b
  = sr[r^(a-1)-s^(b-2)]
    +(r-s)r^a s^(b-1)
  >=0.
```

Finally,

```text
x_a y_b+y_a x_b=D_ab+z_a z_b,
```

and log-concavity of `z_t` makes `z_a z_b` nondecreasing under balancing.
Using

```text
O_ab
  = W D_ab
    +(m-W)(x_a y_b+y_a x_b)
    +(M-m)x_a y_b
```

therefore proves

```text
O_(a+1,b-1) >= O_ab.
```

For `k>=3` and positive interior, at least one positive-coefficient term is
strict whenever `b-a>=2`, so the conditional pair minimum strictly improves.

## Theorem: unique balanced maximin allocation

For every fixed assignment of the other endpoint labels, Lemmas 3 and 4 show

```text
min(S_(a+1,b-1),O_(a+1,b-1))
  >
min(S_ab,O_ab).
```

Taking the minimum over the remaining labels preserves the inequality:

```text
F(...,a+1,...,b-1,...) > F(...,a,...,b,...).
```

Every non-balanced positive integer allocation contains a pair differing by
at least two. Repeated Robin-Hood transfers terminate at the allocation whose
counts differ by at most one. Hence that balanced allocation uniquely
maximizes `F`, up to edge permutation.

If

```text
N=qk+t,  0<=t<k,
```

the optimizer has `k-t` edges with `q` trials and `t` edges with `q+1`
trials.

## Corollary: exact optimal value and total-budget threshold

For the balanced allocation, nature's endpoint assignment depends only on:

- `j`, the number of low labels among the `k-t` edges with `q` trials; and
- `l`, the number of low labels among the `t` edges with `q+1` trials.

Consequently the global optimum is

```text
F_star(k,N,epsilon)
  = min over 0<=j<=k-t and 0<=l<=t of

      x_q^j y_q^(k-t-j)
      x_(q+1)^l y_(q+1)^(t-l)

    + y_q^j x_q^(k-t-j)
      y_(q+1)^l x_(q+1)^(t-l)

    - z_q^(k-t) z_(q+1)^t.
```

This requires only `(k-t+1)(t+1)` exact cells rather than enumerating all
`2^k` endpoint assignments.

For target availability `1-delta`, the exact fixed-total-budget threshold is

```text
N_star(k,epsilon,delta)
  = min {N>=k : F_star(k,N,epsilon) >= 1-delta}.
```

Increasing an edge count reduces both its zero and full probabilities, so the
informative event is monotone under adding trials. Hence `F_star` is
nondecreasing in `N`, and the threshold is both necessary and sufficient
within the frozen experiment class.

## Boundaries

- `epsilon=0`: the worst-case informative probability is zero for every
  finite allocation, so uniqueness fails.
- `k=2`: the opposite-label branch can depend only on the total count; the
  strictness argument uses the presence of at least one other edge.
- asymmetric probability interiors, dependent trials, unknown response
  links, adaptive allocation, multiple-cycle graphs, and downstream power
  rather than availability are not covered.

## Claim boundary

This is an exact maximin allocation theorem for one independent Bernoulli
cycle experiment. It is not a general Bradley-Terry design theorem, an
adaptive RL rollout policy, a behavioral validation, or an ASMP-9
resolution.
