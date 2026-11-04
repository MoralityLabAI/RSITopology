# ASMP-9 v0.19 theory draft: exact finite-budget cactus design

Status: development-only; not registered and not claim-eligible.

## Setup

Inherit the v0.17 independent Bernoulli comparison model, the symmetric
probability interior

```text
epsilon <= p_e <= 1-epsilon,
```

positive integer trial counts `n_e`, and the event that the conditional count
fiber spans the complete reward-gauge quotient.

Assume the cyclic core of the comparison graph is a cactus: each nonbridge
edge belongs to exactly one simple cycle. Write the cycle blocks as

```text
C_1,...,C_c
```

with lengths `k_1,...,k_c`. Original bridges may be present.

For one cycle of length `k`, let

```text
f_k(N) = F_star(k,N,epsilon)
```

be the exact v0.16 maximin availability at total cycle budget `N`. Its
optimizer balances counts within that cycle.

## Theorem 1: exact cactus factorization

For any fixed positive edge allocation `n`,

```text
F_G(n) = product_j F_Cj(n restricted to C_j).
```

### Proof

Every nonbridge edge of a cactus belongs to one unique cycle block. A
residual directed cycle containing that edge cannot leave its block and return
without repeating the block's articulation vertex. Hence full quotient
liveness holds exactly when every cycle block is residually live.

The cycle events depend on disjoint edge sets. Under the registered
independent comparison model their probabilities multiply for every fixed
endpoint-label vector. The adversary's endpoint labels also separate across
the disjoint edge sets, so

```text
min_(all labels) product_j A_j(labels on C_j)
  = product_j min_(labels on C_j) A_j.
```

Original bridges affect neither liveness nor the product. QED.

## Corollary 2: two-level allocation

Fix a per-cycle total `N_j`. The v0.16 theorem uniquely optimizes each cycle,
up to edge permutation, by counts differing by at most one. Therefore every
global optimum:

1. gives each original bridge its minimum permitted count `1`;
2. balances counts within every cycle; and
3. solves the remaining integer problem

```text
maximize  product_j f_(k_j)(N_j)

subject to

  N_j >= k_j,
  sum_j N_j = N - number_of_bridges.
```

## Theorem 3: exact Bellman recursion

Let `D_j(b)` be the best product for the first `j` cycle blocks using exactly
`b` trials. Set

```text
D_0(0)=1
```

and leave other `D_0` states infeasible. Then

```text
D_j(b)
  = max_(k_j <= t <= b)
      D_(j-1)(b-t) f_(k_j)(t).
```

This recurrence returns the exact finite-budget maximin design and every
optimal vector of cycle totals.

Precomputing `f_k(t)` with the compact v0.16 endpoint formula costs at most
quadratic work in `k` per `(k,t)` entry. The direct recurrence uses
`O(c N^2)` exact-rational transitions and `O(N)` rolling-state memory, apart
from optional optimizer backpointers. This is a pseudo-polynomial exact
algorithm in the integer budget.

The recurrence is a classical separable integer resource-allocation dynamic
program. The ASMP-9-specific content is the reduction from conditional-fiber
liveness to this series product.

## Proposition 4: one-step marginal greedy is not exact

For two triangle blocks, `epsilon=1/4`, and total cyclic budget `N=10`,
consider the rule that gives each additional trial to a cycle maximizing

```text
f_k(t+1)/f_k(t).
```

Starting at `(3,3)`, every tie-breaking branch terminates at `(4,6)` or
`(6,4)`. Exact values are

```text
f_3(4) f_3(6) = 34551/262144,
f_3(5)^2       = 8649/65536.
```

The balanced cycle-total allocation `(5,5)` is strictly better by

```text
45/262144.
```

The failure is explained by an increasing marginal at the first step:

```text
f_3(4)/f_3(3) = 11/8,
f_3(5)/f_3(4) = 31/22 > 11/8.
```

Thus `log f_k` is not discretely concave in general, and the standard
diminishing-returns condition that licenses marginal greedy allocation does
not hold.

## Proposition 5: the asymptotic uniform design can fail finitely

The v0.18 cactus exponent theorem allocates asymptotic mass uniformly across
all cyclic edges. That is not an every-budget theorem.

For cycle lengths `(3,4)`, `epsilon=1/10`, and total cyclic budget `N=12`, the
best allocation whose seven edge counts differ by at most one induces cycle
totals `(4,8)`. Its exact product is

```text
1850892363/250000000000
  = 0.007403569452.
```

The exact finite optimum instead uses cycle totals `(3,9)` and has value

```text
76134573/10000000000
  = 0.0076134573.
```

The exact gap is

```text
26235981/125000000000.
```

The v0.19 runner must retain these fractions rather than treating the decimals
as certificates.

## Claim boundary

If prospectively registered and independently verified, v0.19 would close the
exact finite-budget allocation problem for cactus cyclic cores inside the
frozen independent-binomial, known-symmetric-interior model.

It would not give:

- an exact every-budget algorithm for arbitrary cyclic cores;
- an adaptive allocation theorem;
- dependent-response robustness;
- an unknown-link or misspecified-link theorem;
- downstream policy-estimation guarantees;
- behavioral reward identification; or
- a resolution of ASMP-9.
