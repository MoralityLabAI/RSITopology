# Sharp coefficient width for robust finite reward-ray identification

## Definitions

For integers `d >= 2` and `B >= 1`, let

```text
P(d,B) = {z in Z^d \ {0} : gcd(z_1,...,z_d)=1,
                            ||z||_infinity <= B}.
```

Positive scale is the gauge. Primitive representatives make every positive
rational ray appear once; `z` and `-z` remain distinct.

A width-`Q` comparison is a primitive integer vector `q` with
`||q||_infinity <= Q`. Its exact response on `z` is `sign(q dot z)`.
Under adversarial threshold perturbation `e in [-delta,delta]`, its possible
responses are:

```text
{sign(q dot z + e) : |e| <= delta}.
```

Two rays are robustly separated when some admitted query gives disjoint
possible-response sets.

## Theorem

Let `0 <= delta < 1`. Every pair of distinct positive rays in `P(d,B)` is
robustly separable by a primitive integer comparison of width at most:

```text
Q*(B) = 2        for B = 1,
        2B - 1   for B >= 2.
```

Both bounds are sharp for every `d >= 2`.

Consequently the complete family of primitive comparisons through width
`Q*(B)` identifies every registered reward ray modulo positive scale, while
for any smaller width at least one pair remains indistinguishable, regardless
of query count or adaptivity along their common transcript.

## Proof

Because all dot products are integers and `delta < 1`, disjoint response sets
are equivalent to strict opposite signs:

```text
q dot z >= 1 and q dot z' <= -1,
```

or the reverse.

### Upper bound

Take distinct primitive representatives `z,z'`.

If they are linearly dependent, primitivity implies `z'=-z`; a signed
coordinate query of width one separates them.

Otherwise choose coordinates `i,j` with nonzero minor

```text
D = z_i z'_j - z_j z'_i.
```

Write `(a,b)=(z_i,z_j)` and `(c,d)=(z'_i,z'_j)`. With
`s=sign(D)`, the two-coordinate normal

```text
(x,y) = s(d+b, -c-a)
```

satisfies

```text
xa+yb  = |D|,
xc+yd  = -|D|.
```

Its width is at most `2B`. For `B=1`, this proves the stated upper bound.
For `B>=2`, it already has width at most `2B-1` unless one component has
absolute value `2B`.

Suppose, after swapping the two selected coordinates if necessary, that
`|a+c|=2B`. Then `a=c=sigma B`, while `b != d`. Absorb `sigma` into `x` and,
if necessary, swap the two rays so that `h=b-d>0`.

If `h>=2`, choose

```text
y=B,  x'=-d-1.
```

Then the two scores are `B(h-1)` and `-B`. Both coefficients have absolute
value at most `B`, hence at most `2B-1`.

If `h=1` and `b>=1`, choose

```text
y=B+1,  x'=-b.
```

The scores are `b` and `b-B-1`.

If `h=1` and `b<=0`, choose

```text
y=B+1,  x'=1-b.
```

The scores are `B+b` and `b-1`. Since `d=b-1>=-B`, the first is at least one.

In both `h=1` subcases the coefficient width is at most `B+1`, which is at
most `2B-1` for `B>=2`. Reinsert `sigma` into the common-coordinate
coefficient. The case `|b+d|=2B` follows by swapping coordinates. This
completes the upper bound.

Finally divide the constructed normal by the gcd of its coordinates. Division
preserves strict opposite signs because the original scores are nonzero
integers, and cannot increase width.

### Lower bound for B=1

Embed:

```text
z=(1,0),  z'=(1,1).
```

A width-one normal cannot make `x` and `x+y` have strict opposite signs:
doing so would require `|y|>=2`. Width two is necessary.

### Lower bound for B>=2

Embed:

```text
z =(B,   B-1),
z'=(B-1, B-2).
```

Both are primitive. If `q=(x,y)` gives scores at least `1` and at most `-1`,
then:

```text
x+y >= 2.
```

Since

```text
q dot z' = (B-1)(x+y)-y <= -1,
```

we obtain `y >= 2B-1`. Reversing the score signs gives
`y <= -(2B-1)`. Thus every separating normal has width at least `2B-1`.

The witnesses embed in every dimension `d>=2`, proving sharpness.

## Access consequence

The theorem turns the v0.2 finite pattern into an exact grammar boundary:

- below `Q*(B)`, the access class has a deterministic kernel pair;
- at `Q*(B)`, all positive reward rays in the bounded lattice registry are
  distinguishable; and
- this statement is independent of how many queries an algorithm asks.

It does not determine the minimum number of queries at the sufficient width.
That remains a separate separating-family problem.

## Claim boundary

This theorem concerns cycle-return coordinates after potential shaping has
already been quotiented. It does not recover rewards from policies, handle
discounted shaping, model inconsistent humans, or give finite-sample error
bounds. The novelty status of the sharp elementary coefficient formula is
unestablished.

