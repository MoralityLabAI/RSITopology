# ASMP-9 v0.23 theory: multivariate local value and an exchange trap

## 1. Setting

Let `G=(V,E)` be one finite simple biconnected comparison block.  Edge `e`
receives a positive integer number `n_e` of independent fair Bernoulli
comparisons.  After conditioning out the scalar reward nuisance as in the
predecessor chain, its sufficient status is:

```text
ZERO      probability z_e
FULL      probability z_e
INTERIOR  probability 1-2z_e,
z_e = 2^(-n_e).
```

`ZERO` and `FULL` supply one of the two residual directions; `INTERIOR`
supplies both.  Quotient liveness inside the bridgeless block is strong
connectivity of this residual digraph.

## 2. Edge-multivariate representation

For indeterminates `k_e,l_e`, give each oriented edge either direction with
weight `k_e` and each bidirected edge weight `l_e`.  The strongly connected
weighted enumerator is

```text
SC_G(k,l)
  = - product_e k_e
      Z_G(-1,{1+l_e/k_e}),
```

where

```text
Z_G(q,{v_e})
  = sum_{A subset E} q^k(A) product_{e in A} v_e.
```

### Coefficient proof

Fix the set `B` of bidirected edges.  The coefficient of

```text
product_{e in B} l_e product_{e not in B} k_e
```

on the right is

```text
-sum_{A superset B} (-1)^k(A).
```

Contracting the bidirected set `B`, the remaining coefficient counts the
totally cyclic orientations of the resulting multigraph, including the
factor of two for each induced loop.  By the classical
`T_H(0,2)` orientation interpretation, the same number is the count of
strong oriented completions with bidirected set `B`.  Equality holds
coefficientwise.

Substituting `k_e=z_e` and `l_e=1-2z_e` gives:

```text
F_G(n)
  = - product_e z_e
      Z_G(-1,{z_e^(-1)-1})
  = -2^(-N) Z_G(-1,{2^(n_e)-1}),
N = sum_e n_e.
```

At fixed total trial count `N`, exact maximin design is therefore equivalent
to maximizing the integer

```text
-Z_G(-1,{2^(n_e)-1})
```

over positive integer count vectors.  This is a representation, not an
efficient algorithm: even uniform value evaluation is #P-hard by v0.22.1.

## 3. K4 exchange trap

Order the edges of `K4` as

```text
(01,02,03,12,13,23).
```

For each integer `s>=2`, compare:

```text
x_s = (s-1,s,s+1,s+1,s,s-1),
y_s = (s,s,s,s,s,s).
```

Both have total count `6s`.  The opposite edge pairs of `x_s` receive
counts `s-1`, `s`, and `s+1`.

Let `t=2^s`.  When the three opposite pairs have edge powers `x,y,w`, direct
evaluation of the `q=-1` polynomial yields the common-denominator numerator:

```text
S(x,y,w)
  = (xyw)^2 - 2(x^2+y^2+w^2) - 8xyw
    + 12(x+y+w) - 24.
```

Thus:

```text
S(t,t,t)-S(t/2,t,2t)
  = 3t(3t-4)/2 > 0.
```

The balanced point is strictly better.

Every ordered one-unit transfer from the trap falls into one of the nine
factor classes in `DEVELOPMENT_NOTE_v0_23.md`.  Each trap-minus-neighbor gap
is strictly positive for `t>=4`.  Hence `x_s` is a strict one-exchange local
maximum for every `s>=2`, despite being suboptimal.

## 4. Explicit non-M-concavity certificate

Let `x=x_s`, `y=y_s`.  Pick either high edge `i` of `x` and either low edge
`j`.  The only eligible exchange coordinates for the M-concavity axiom are
the two low edges.  For each one:

```text
f(x)+f(y)-f(x-e_i+e_j)-f(y+e_i-e_j)
  = t^2(4t-5)/2 > 0.
```

M-concavity requires at least one eligible `j` for which this quantity is
nonpositive.  Both are positive, giving a direct axiom violation.

## 5. Consequence and boundary

The result closes the representation of the exact nonuniform local value
table at `epsilon=1/2` and refutes a tempting local-exchange solution
principle.  It does not classify the global optimizer or its computational
complexity.  It does not extend to arbitrary endpoint probabilities,
adaptive allocation, misspecified response laws, or behavioral reward
identification.
