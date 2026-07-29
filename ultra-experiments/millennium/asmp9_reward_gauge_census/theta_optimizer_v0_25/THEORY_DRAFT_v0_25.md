# ASMP-9 v0.25 theory draft: exact optimization on generalized theta blocks

Status: development-only; not registered and not claim-eligible.

## 1. Graph class

A simple generalized theta block consists of `k>=2` internally
vertex-disjoint paths with common terminals `s,t`.  At most one path has
length one, so the graph remains simple.  The overlapping-cycle case begins
at `k=3`.

Edge `e` receives a positive integer count `n_e` in the independent
fair-microtrial model at `epsilon=1/2`.

## 2. Exact path-state formula

For path `j`, define

```text
A_j = product_(e in path j) (2^(n_e)-1),
B_j = product_(e in path j) (2^(n_e)-2).
```

After division by `2^(sum_e n_e)`:

- `A_j` is the numerator for the path supporting a declared terminal
  direction;
- `B_j` is the numerator for the path supporting both terminal directions;
- `A_j-B_j` is the numerator for exactly one declared direction; and
- `2A_j-B_j` is the numerator for the path supporting at least one complete
  terminal direction.

The full residual orientation is strongly connected exactly when:

1. every path supports at least one complete terminal direction; and
2. the collection contains at least one `s->t` path and at least one `t->s`
   path.

The two excluded events are "every path is forward only" and "every path is
reverse only."  Therefore the exact common-denominator numerator is

```text
S(n)
  = product_j (2A_j-B_j)
      - 2 product_j (A_j-B_j),

F_G(n) = S(n) / 2^(sum_e n_e).
```

This identity is independently checked against the v0.23 edge-multivariate
evaluator.

## 3. Strict path-internal balancing

Fix one path and all other paths.  Write

```text
P = product_(h != j) (2A_h-B_h),
Q = product_(h != j) (A_h-B_h).
```

Since `A_h>B_h>=0`,

```text
P >= 2^(k-1) Q >= 2Q.
```

The part of `S` depending on path `j` is

```text
2(P-Q) A_j - (P-2Q) B_j.
```

Set

```text
alpha = 2(P-Q) > 0,
beta  = P-2Q >= 0.
```

Because `Q>0`,

```text
2 beta < alpha.
```

Now choose two edges of path `j` with counts `p>=q+2`, and move one trial
from the high edge to the low edge.  With `X=2^p`, `Y=2^q`, and with `A_0`,
`B_0` denoting the products over the other path edges:

```text
Delta A_j = A_0 (X/2-Y) > 0,
Delta B_j = 2 B_0 (X/2-Y).
```

Hence

```text
Delta S
  = (X/2-Y) (alpha A_0 - 2 beta B_0)
  > 0,
```

because `B_0<=A_0` and `2 beta<alpha`.

Therefore:

> In every global optimum on a generalized theta block, counts within each
> individual path differ by at most one.

This is not a global edge-balancing theorem.  Different paths can receive
different total budgets.

## 4. Exact reduced optimizer

Let path `j` have length `l_j` and total count `s_j`.  The preceding theorem
fixes its products:

```text
q_j, r_j = divmod(s_j,l_j),

A_j(s_j)
  = (2^(q_j+1)-1)^(r_j)
      (2^q_j-1)^(l_j-r_j),

B_j(s_j)
  = (2^(q_j+1)-2)^(r_j)
      (2^q_j-2)^(l_j-r_j).
```

Thus exact global optimization reduces to:

```text
maximize S(s_1,...,s_k)
subject to s_j>=l_j and sum_j s_j=N.
```

Enumerating the

```text
binomial(N-|E|+k-1,k-1)
```

path-total compositions and evaluating the closed form returns an exact
global optimizer.  For fixed `k`, this uses `O(N^(k-1))` exact arithmetic
evaluations.  It is polynomial when the physical trial budget is unary and
pseudopolynomial when `N` is binary encoded.  It is not claimed fixed-
parameter tractable in `k+log N`.

## 5. Burned endpoint counterexample

Development inspection of the simple theta block with path lengths `(1,2,2)`
at total budget `N=10` gives exact optimum path totals

```text
(1,4,5) and (1,5,4).
```

One corresponding allocation has counts

```text
(1 ; 2,2 ; 2,3)
```

and exact availability `375/512`.  The globally balanced allocation

```text
(2 ; 2,2 ; 2,2)
```

has availability `367/512`.

The cell was read before registration and is burned.  It usefully shows why
the theorem stops at within-path balance and retains the path-total search.

## 6. Claim boundary

The registered mathematical result is an exact access-model formula, a
strict path-internal balancing theorem, and a reduced exact optimizer for one
declared generalized-theta class at `epsilon=1/2`.  Majorization and
Schur-convex reliability allocation are classical; no novelty claim is made
for the specialized lemma.

It is not:

- a new reliability-block-diagram calculus;
- a polynomial-time result for binary-encoded unbounded budgets;
- a global algorithm for arbitrary series-parallel or biconnected graphs;
- optimizer hardness;
- arbitrary endpoint probability, adaptive, dependent, or misspecified
  response analysis;
- behavioral reward identification or general inverse reinforcement
  learning; or
- a resolution of ASMP-9.
