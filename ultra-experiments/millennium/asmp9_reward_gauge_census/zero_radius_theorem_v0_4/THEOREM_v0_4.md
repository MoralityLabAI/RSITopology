# Sharp exact-tie comparison width for bounded integer reward rays

## Theorem

Let `d>=2`. Let `P(d,B)` be the primitive nonzero integer vectors with
infinity norm at most `B`, with positive scale quotiented and negative scale
retained. An exact comparison query returns:

```text
sign(q dot z) in {-1,0,+1}
```

for a primitive integer normal `q`.

The smallest coefficient width sufficient in the worst case to distinguish
every pair in `P(d,B)` is:

```text
Q0*(B) = 1      for B in {1,2},
         B-1    for B>=3.
```

The formula is independent of dimension.

## Farey separation lemma

Let `N=B-1>=1`. The signs of comparisons against all reduced rational
thresholds in the Farey sequence `F_N` distinguish every reduced fraction in
`[0,1]` whose denominator is at most `B`.

Proof: between consecutive Farey fractions `a/b<c/d`, every interior reduced
fraction has denominator at least `b+d>N`. If `b+d>=B+1`, no fraction of
denominator at most `B` lies inside. If `b+d=B`, the mediant
`(a+c)/(b+d)` is the unique such interior fraction; every other interior
fraction has larger denominator. Thus each open Farey cell contains at most
one target fraction. Endpoints are identified by exact ties.

## Upper bound

Take distinct primitive vectors `z,z'`.

Coordinate queries first identify each coordinate's sign and zero status. If
those differ, a width-one query separates the pair.

Otherwise choose a common nonzero reference coordinate `k`. If every absolute
ratio:

```text
|z_i|/|z_k| = |z'_i|/|z'_k|
```

agrees, the shared coordinate signs make `z'` a positive rational multiple of
`z`. Primitivity then implies `z'=z`, contrary to the pair being distinct.

Therefore some coordinate `i` has unequal ratios. If both ratios exceed one,
take reciprocals by swapping `i` and `k`; if they straddle one, the threshold
one separates them. Otherwise both lie in `[0,1]`.

Reduce both ratios. Their numerators and denominators are at most `B`.
The Farey lemma supplies a threshold `p/q` in `F_{B-1}` that lies between them
or equals exactly one. The two-sparse query:

```text
q * sign(z_i) on coordinate i,
-p * sign(z_k) on coordinate k
```

has width at most `B-1` and gives different exact ternary signs. For `B=1`,
width one suffices directly. This proves the upper bound.

## Lower bound

Width zero contains no nonzero query, so width one is necessary at `B=1,2`.

For `B>=3`, embed:

```text
z =(B,   B-1),
z'=(B-1, B-2).
```

Let scores be `A` and `C`. If their exact signs differ, orient the query so
that `A>=1` and `C<=0`. Then:

```text
x+y=A-C>=1
```

and:

```text
C=(B-1)(x+y)-y<=0.
```

Hence `y>=B-1`. Reversing the orientation gives `y<=-(B-1)`. The query

```text
(B-2,-(B-1))
```

attains the bound with scores `-1` and `0`.

## Discontinuity at model error zero

Combining this theorem with v0.3.1 gives:

```text
delta = 0:       Q0*(B) = B-1       for B>=3;
0 < delta < 1:   Q*(B)  = 2B-1      for B>=2.
```

An arbitrarily small positive adversarial threshold radius nearly doubles the
worst-case query expressivity required. The discontinuity is caused by the
loss of exact ties.

## Claim boundary

This is an exact theorem for bounded integer cycle-return coordinates after
potential shaping has been removed. It is not finite-sample preference
learning, reward recovery from behavior, discounted shaping, or a model of
human inconsistency. The proof is a classical Farey-sequence specialization;
novelty is not claimed.

