# Finite stochastic-choice trichotomy

## Frozen object

Let `X` be a finite set. A complete stochastic choice kernel assigns
`p(x | S) >= 0` for every nonempty menu `S subseteq X` and every `x in S`,
with `sum_{x in S} p(x | S) = 1`. Singleton probabilities equal one.

The registered finite census specializes to:

```text
X = {a,b,c}
all menus of size two and three
strictly positive rational probabilities with denominator six.
```

The theorem statements below apply to complete finite systems; the exact
census is an implementation check, not their proof.

## Tier 1: one scalar ratio scale

Assume all probabilities are positive. The kernel is `scalar_luce` iff there
are weights `v_x > 0` such that

```text
p(x | S) = v_x / sum_{y in S} v_y
```

for every menu. On three alternatives, write `X={a,b,c}` and set
`v_x = p(x | X)`. Then scalarity is equivalent to the three exact identities

```text
p(x | {x,y}) = v_x / (v_x + v_y).
```

The weights are unique up to a common positive factor.

This is Luce's classical ratio-scale representation.

## Tier 2: a random ordering, but no single Luce scale

Let `L(X)` be the strict linear orders on `X`. The kernel is
`random_utility` iff there is a probability vector `lambda` on `L(X)` with

```text
p(x | S) =
    sum_{rho in L(X): x is rho-maximal in S} lambda(rho).
```

For `x in A subseteq X`, define the Block-Marschak polynomial

```text
q(x,A) =
    sum_{B: A subseteq B subseteq X}
        (-1)^(|B|-|A|) p(x | B).
```

Falmagne's classical finite representation theorem states that a complete
system is induced by rankings iff every `q(x,A)` is nonnegative.

The `random_utility_non_luce` tier consists of kernels satisfying this
criterion but failing the Luce identities.

## Tier 3: no declared latent value object

A kernel with any negative Block-Marschak polynomial has no representation by
a probability distribution over strict rankings in this declared class. The
negative polynomial is an exact rational separating certificate.

This status is `no_random_utility_representation`. It does not mean that no
behavioral model of any kind exists.

## Total nested classification

For every complete positive finite choice kernel, exactly one status holds:

1. `scalar_luce`;
2. `random_utility_non_luce`; or
3. `no_random_utility_representation`.

The first class is contained in the second representation class: a Luce rule
induces the Plackett-Luce distribution on complete rankings.

## Sharp access witness on three alternatives

Binary menus do not determine the trichotomy.

Two complete kernels agree on all pairs:

```text
p(a | ab) = p(a | ac) = p(b | bc) = 1/2.
```

Kernel `K_scalar` has

```text
p(. | abc) = (1/3, 1/3, 1/3)
```

and is Luce-scalar. Kernel `K_none` has

```text
p(. | abc) = (3/4, 1/8, 1/8).
```

It violates regularity because `p(a | abc) > p(a | ab)`, hence cannot be a
random-utility kernel. Thus maximum menu size two is insufficient. Observing
the ternary menu completes the declared three-alternative kernel and makes the
classical criteria decisive.

## Nonempty middle-tier witness

Put probability `1/3` on each ranking

```text
a > b > c
b > c > a
c > a > b.
```

The resulting kernel is random-utility rationalizable and strictly positive,
but its binary odds disagree with the uniform full-menu probabilities, so it
has no single Luce ratio scale.

## Claim boundary

This document consolidates classical finite stochastic-choice representation
results into an ASMP-9 decision instrument. It is not a novelty claim and does
not establish finite-sample, incomplete-menu, strategic, continuous, or
welfare-relevant value identification.

