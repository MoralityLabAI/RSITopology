# Sharp robust comparison width for bounded integer reward rays

## Corrected theorem

Let `d>=2`, `B>=1`, and let `P(d,B)` contain the primitive nonzero integer
vectors `z` with `||z||_infinity<=B`. Positive scale is quotiented; `z` and
`-z` remain different reward rays.

A comparison query is a primitive integer normal `q`. Its response may be
perturbed by an adversarial threshold offset:

```text
sign(q dot z + e), where |e| <= delta.
```

For every **strictly positive** radius:

```text
0 < delta < 1,
```

the smallest coefficient width sufficient to robustly distinguish every pair
of rays in `P(d,B)` is:

```text
Q*(B) = 2        if B=1,
        2B-1     if B>=2.
```

The formula is independent of dimension once `d>=2`.

## Why the interval is open at zero

All scores are integers. For `0<delta<1`, a zero score can produce any of
`{-1,0,+1}`. Two possible-response sets are disjoint exactly when the two
integer scores have strict opposite signs.

At `delta=0`, a zero score returns an exact tie. A tie and a nonzero score are
distinguishable, so strict opposite signs are no longer necessary. The
zero-radius access threshold is a separate problem.

This endpoint distinction supersedes the v0.3 statement that incorrectly used
`0<=delta<1`.

## Constructive upper bound

Take distinct primitive representatives `z,z'`.

If they are linearly dependent, primitivity implies `z'=-z`; one signed
coordinate separates them.

Otherwise choose coordinates `i,j` with:

```text
D = z_i z'_j - z_j z'_i != 0.
```

Write `(a,b)=(z_i,z_j)`, `(c,d)=(z'_i,z'_j)`, and `s=sign(D)`. The normal:

```text
(x,y)=s(d+b,-c-a)
```

has scores `|D|` and `-|D|`. Its width is at most `2B`, proving the `B=1`
case.

For `B>=2`, the width is already at most `2B-1` unless one component equals
`+/-2B`. Suppose, after swapping coordinates, that `a=c=sigma B` and `b!=d`.
Absorb `sigma` into the first query coefficient and swap the two rays if
needed so that `h=b-d>0`.

If `h>=2`, choose:

```text
y=B, x'=-d-1.
```

The scores are `B(h-1)` and `-B`.

If `h=1` and `b>=1`, choose:

```text
y=B+1, x'=-b.
```

The scores are `b` and `b-B-1`.

If `h=1` and `b<=0`, choose:

```text
y=B+1, x'=1-b.
```

The scores are `B+b` and `b-1`; `d=b-1>=-B` makes the first at least one.

Every coefficient is at most `B+1<=2B-1`. The other extreme-coordinate case
is symmetric. Dividing the normal by its coordinate gcd preserves strict
opposite signs and cannot increase width.

## Sharp lower witnesses

For `B=1`, use:

```text
z=(1,0), z'=(1,1).
```

A strict-opposite comparison requires width at least two.

For `B>=2`, use:

```text
z=(B,B-1), z'=(B-1,B-2).
```

If `q=(x,y)` gives scores at least `1` and at most `-1`, then `x+y>=2` and:

```text
(B-1)(x+y)-y <= -1,
```

so `y>=2B-1`. Reversing the score signs gives `y<=-(2B-1)`. These witnesses
embed in every higher dimension.

For contrast, at `delta=0` the same witness is separated by a narrower
tie-producing query. For `B>=2`:

```text
q=(B-2,-(B-1))
```

gives scores `-1` and `0`. That explicit endpoint control is part of the v0.3.1
verification.

## Adaptive consequence

Below `Q*(B)`, every admitted query has overlapping possible-response sets on
the lower-witness pair. An adversary can choose a common response after each
adaptive query, keeping both worlds on the same decision-tree path. Therefore
adaptivity cannot defeat the width lower bound.

At `Q*(B)`, the complete primitive-query family separates every pair. A finite
nonadaptive separating subfamily consequently exists, although this theorem
does not give its minimum cardinality.

## Claim boundary

This is a theorem about bounded integer cycle-return coordinates after
potential shaping has already been quotiented. It is not reward recovery from
behavior, a human-consistency theorem, a discounted-shaping theorem, or a
finite-sample preference-learning result. Its proof is elementary. The exact
formula's novelty is not established.

