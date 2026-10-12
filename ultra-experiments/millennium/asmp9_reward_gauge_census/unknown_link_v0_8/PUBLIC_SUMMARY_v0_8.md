# Unknown monotone response links enlarge the value gauge

## Result

Consider exact population pairwise-choice probabilities

```text
P(j preferred to i) = F(beta (u_j-u_i)),
```

where `beta>0` and `F` is strictly increasing and symmetric:

```text
F(-x)=1-F(x), F(0)=1/2.
```

The identifiability boundary depends on what is known about `F`.

When `F` is known and injective, applying `F^-1` to a connected comparison
graph recovers

```text
beta (u-u_root).
```

Unknown positive inverse temperature therefore contributes only positive
utility scale, together with the usual additive constant.

When `F` may be any strictly increasing symmetric link, even the complete
population probability law on a finite item set need not identify a utility
ray. Utilities that share the labelled weak order and equality pattern of all
pairwise differences can be made observationally identical by choosing
separate admissible links. This ambiguity is strictly larger than positive
affine reward gauge once there are at least three items.

## Exact rational witness

Take

```text
u  = (0,1,3),
u' = (0,1,4).
```

The two vectors are not positive-affine equivalent. Nevertheless, separate
strictly increasing symmetric links give the identical complete law

```text
P(1>0) = 3/4,
P(2>1) = 5/6,
P(2>0) = 7/8.
```

One source link is, for `x>=0`,

```text
F(x) = 1/2 + x/(2(1+x)),
```

extended by symmetry. The target link interpolates monotonically through

```text
(0,1/2), (1,3/4), (3,5/6), (4,7/8).
```

Thus repeated samples cannot remove the ambiguity: the two population laws
are exactly equal, not merely close.

Three items are minimal. With two distinct items, every nonzero utility gap is
positive-scale equivalent to every other. For three ordered items

```text
(0,a,a+b), a>0, b>0,
```

the finite-design invariant records whether `a<b`, `a=b`, or `a>b`, while the
positive-affine utility ray still depends continuously on `a/b`.

## Prospective verification

The theorem, prior-art boundary, implementation, tests, protocol, and runner
were hash-sealed before the fresh cells ran. The CPU-only execution checked:

- 32,768 known-link cases with 2 through 16 items and 1,477,970 exact edges;
- all 3,762 primitive three-item rays with final coordinate 65 through 128;
- two strict difference-order classes, each containing 1,881 rays;
- 16,384 fresh same-order, non-affine ambiguity pairs;
- 8,192 two-item minimality controls;
- 8,192 opposite-order rejection controls; and
- 144 prereveal mathematical tests.

There were zero recovery, affine-classification, law-matching,
known-link-separation, link-validity, minimality, or rejection mismatches. All
nine registered gates and the independent artifact verifier passed.

## Access consequence

Complete finite pairwise probabilities are insufficient when the response
link is an unrestricted monotone nuisance. Identifying more than labelled
difference order requires an additional assumption or access channel, such
as:

- a known parametric link;
- a normalized, sufficiently restricted link family;
- interventions that calibrate the link beyond the finite observed gaps; or
- an explicitly weaker ordinal target.

Positive semiparametric single-index results under rich covariate support are
not contradicted. This experiment deliberately freezes a finite item design.

## ASMP-9 contribution and remaining gap

This closes one narrow response-parameter question:

```text
known injective link + unknown positive temperature
  -> translation and positive-scale gauge only;

unknown unrestricted monotone link on a finite design
  -> strictly larger difference-order equivalence classes.
```

It does not resolve ASMP-9. It supplies neither finite-sample confidence
regions, a minimal link-calibrating intervention family, general finite-MDP
policy access, nor robustness to contextual, dependent, or history-sensitive
demonstrators. The underlying monotone single-index nonidentifiability is
classical; novelty is not claimed.
