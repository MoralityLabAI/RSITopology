# Conditional exactness does not imply nuisance-uniform unconditional power

## Setup

Let `C_k` be a consistently oriented simple cycle. Every edge receives `n`
independent Bernoulli comparisons. Write:

```text
Y=(Y_1,...,Y_k),  0 <= Y_e <= n.
```

The edge odds under the scalar null are positive rationals
`s=(s_1,...,s_k)` satisfying:

```text
product_e s_e = 1.
```

This is exactly the multiplicative gradient condition on one cycle. The
one-sided cycle alternative multiplies the first edge odds by `R>1`, so its
gauge-invariant circulation odds are `R`.

## Lemma 1: fiber geometry

Two count vectors on the oriented cycle have the same vertex win balance if
and only if they differ by an integer multiple of the all-ones vector.
Canonicalize a fiber by subtracting its minimum coordinate:

```text
a(y) = y - min(y) 1.
```

The fiber has:

```text
n - max(a(y)) + 1
```

members. It exposes the one-dimensional cycle quotient if and only if it has
at least two members, equivalently:

```text
max(Y)-min(Y) < n.
```

It is singleton exactly when some edge count is zero and another is `n`.

## Lemma 2: exact availability

For independent `Y_e ~ Bin(n,p_e)`, define:

```text
P0_e = (1-p_e)^n,
Pn_e = p_e^n.
```

The probability `A(p)` of realizing an informative fiber is:

```text
A(p)
  = product_e (1-P0_e)
  + product_e (1-Pn_e)
  - product_e (1-P0_e-Pn_e).
```

This follows by taking the complement of the event that at least one edge is
zero and at least one edge is `n`.

## Lemma 3: exact conditional test on every fiber

On a canonical fiber `a`, the admissible outcomes are:

```text
y(z)=a+z 1,  z=0,...,n-max(a).
```

Conditioning cancels every scalar nuisance because `product_e s_e=1`. Under
the alternative, the conditional likelihood ratio is proportional to:

```text
R^z.
```

It is strictly increasing. Therefore the randomized upper-tail test is
uniformly most powerful at exact conditional size `alpha` on every
informative fiber.

On a singleton fiber the null and alternative conditional laws coincide. A
size-`alpha` rule can only reject with probability `alpha`; that randomization
contains no information about cycle circulation.

## Theorem: unconditional excess-power factorization and collapse

Apply the exact conditional test on informative fibers and randomize at
`alpha` on singleton fibers. Its unconditional null size is exactly `alpha`.
Its alternative power satisfies:

```text
Power_s(R)-alpha
  = sum over informative fibers t
      P_(s,R)(T=t)
      [Power_t(R)-alpha].
```

Consequently:

```text
0 <= Power_s(R)-alpha
   <= (1-alpha) A(p_(s,R)).
```

Now choose the scalar nuisance family:

```text
s(q) = (q^(k-1), q^(-1), ..., q^(-1)).
```

Its product is one. For fixed `R>1`, as `q -> infinity`, the first edge count
converges in probability to `n` while every other edge count converges to
zero. Hence:

```text
A(p_(s(q),R)) -> 0
```

and therefore:

```text
Power_(s(q))(R) -> alpha.
```

If singleton fibers are instead treated as unavailable and never rejected,
both unconditional size and power converge to zero.

Thus exact conditional nuisance cancellation does not provide a nontrivial
nuisance-uniform unconditional power guarantee when the scalar nuisance is
unbounded.

## Corollary: an interior nuisance class restores a positive guarantee

Suppose every alternative edge probability obeys:

```text
epsilon <= p_e <= 1-epsilon
```

for one declared `epsilon>0`. The event that no edge count is zero is a subset
of the informative event, so:

```text
A(p) >= [1-(1-epsilon)^n]^k.
```

For fixed finite `(k,n,R,alpha)` with `R>1`, every informative fiber has
conditional power strictly above `alpha`. Define:

```text
g_min(k,n,R,alpha)
  = minimum over informative fibers t
      [Power_t(R)-alpha] > 0.
```

Then:

```text
Power_s(R)-alpha
  >= [1-(1-epsilon)^n]^k
     g_min(k,n,R,alpha)
  > 0.
```

Thus a declared probability-interior condition is sufficient for a uniform
positive unconditional power gain in the frozen finite experiment, while the
unbounded scalar-gradient family makes such a guarantee impossible.

## ASMP-9 consequence

Any positive access theorem based on this conditional experiment must add at
least one of:

- a bounded item-strength or edge-probability interior;
- a design intervention that controls comparison balance;
- an unconditional model for the nuisance distribution; or
- a declared availability floor.

Without such an assumption, “exact conditional test” is compatible with
arbitrarily weak unconditional detection.

## Claim boundary

This is elementary finite conditional-inference mathematics. It concerns an
oriented cycle, equal fixed edge counts, independent Bernoulli comparisons,
a known logistic link, and one multiplicative cycle alternative. It is not a
new general theorem about conditional likelihood, a minimax Bradley-Terry
result, a behavioral validation, or an ASMP-9 resolution.
