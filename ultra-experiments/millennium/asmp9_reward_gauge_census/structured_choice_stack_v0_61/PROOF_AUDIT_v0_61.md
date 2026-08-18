# ASMP-9 v0.57-v0.60 proof and convention audit

## Audit verdict

The four development theorems form a coherent conditional stack after two
points are made explicit in v0.61:

1. `Q(n,r)` is the number of observed probability coordinates,
   `sum k*choose(n,k)`, not the number of menus.
2. The class-level minima in the contamination and bounded-recording radii are
   attained only after compactness of the probability-floor reconstruction
   class and its tier fibers is proved.

No contradiction was found in the access, metric, margin, contamination, or
selection conventions.  The development computations remain burned and are
not promoted by this audit alone.

## A. Bounded-degree reconstruction

For each ordered pair `(x,y)`, the degree-`r` Boolean function

```text
g_xy(S)=log[p(x|Sxy)/p(y|Sxy)]
```

is determined by its values on contexts through size `r`.  Möbius inversion
recovers its coefficients, and zeta summation recovers every larger context.
Within one menu, the recovered ratios to a root determine the unique
probability vector.

The sharp witness is consistent.  With one active `(r+1)`-set `B0`,

```text
u_x(A)=1{B0 subseteq A\{x}}.
```

All menus through size `r+1` are uniform.  On `A0=B0 union {x0}`, only `x0`
has exponent one, giving `(r+2)/(2r+3)>1/2` against binary probability `1/2`.
The resulting regularity violation certifies non-RUM.  Pairwise log odds are
degree at most `r` because the order-`r+1` terms contained entirely in the
common context cancel.

## B. Exact interpolation norm

For target context size `s>r`, the coefficient on one observed value at subset
size `u` is

```text
(-1)^(r-u) choose(s-u-1,r-u).
```

Summing absolute values over the `choose(s,u)` subsets gives the exact
`l_infinity` operator norm.  Choosing each perturbation sign to match its
coefficient attains the norm for the unrestricted low-layer interpolation
operator.

## C. Margin and likelihood-ratio handoff

If every observed probability is at least `a` and its coordinate estimate is
within `t<a`, each observed pair log-odds error is at most

```text
-2 log(1-t/a).
```

Interpolation gives root-log-score error at most `E`.  The log-likelihood
ratio errors across a target menu have range at most `2E`, so

```text
L1 <= 2 tanh(E/2).
```

The v0.58 tolerance is exactly the solution making this bound `gamma/3`.
The v0.58 classifier then follows by the triangle inequality around the
closed Luce and RUM model sets.

The two three-alternative paths are valid:

- the ranking-weight perturbation remains RUM, preserves uniform binaries,
  and leaves the Luce class immediately;
- the full-menu perturbation crosses a regularity face of the RUM polytope.

Their KL calculations use the direction required by Pinsker and give the
displayed `gamma^-2` lower exponent.

## D. Compactness and attainment lemma

Let `O_(n,r,a)` be the valid restrictions to `D_(r+2)` whose probability
coordinates are at least `a>0`.  It is a closed subset of a finite product of
simplices and is compact.

For any observed pair log odds,

```text
|g_xy(U)| <= log(1/a).
```

The interpolation norm therefore gives, for every reconstructed context,

```text
|g_xy(S)| <= K_star(n,r) log(1/a).
```

After normalization, every reconstructed full-kernel coordinate is bounded
below by the conservative uniform quantity

```text
a^(2 K_star(n,r))/n > 0.
```

The reconstruction map is continuous on `O_(n,r,a)`.  Its image is compact
and remains inside the positive kernel space.  Intersecting that image with

```text
Lbar,
P intersect {d(.,Lbar)>=gamma},
{d(.,P)>=gamma}
```

produces closed compact tier fibers.  Hence every nonempty cross-tier product
is compact, and the continuous observed-TV and symmetric-ratio objectives
attain the minima called `Delta` and `Lambda`.

This proves the attainment premise used in v0.59 and v0.60.  If the
probability floor is removed, only infimum statements are licensed.

## E. Huber contamination

A common mixture law must dominate `(1-epsilon)max(p_i,p'_i)` coordinatewise.
Its mandatory mass sums to

```text
(1-epsilon)[1+TV(p,p')].
```

This is at most one exactly when
`TV<=epsilon/(1-epsilon)`.  Adding leftover mass constructs the common law and
both contaminants.  Independent menu contaminants replace TV by maximum
menuwise TV.

The v0.59 inverse-modulus lower bound is a contrapositive use of the v0.58
reconstruction inequality; it is invoked only below the observed probability
floor, where the logarithm is defined.

## F. Selection timing

Recorded pre-response selection factorizes as

```text
J(A,x)=s(A)p_A(x).
```

The menu marginal and every positive-support conditional are therefore
identified, even when the unknown menu-frequency law is target-dependent.
Without a known relation from the target to the selection marginal, no
uniform missing-conditional information follows.

Outcome-dependent recording instead observes masses `h(x)=p(x)rho(x)`.
Unknown unrestricted positive `rho` can map any two positive clean laws to
the same complete record law and retention rate.

Under `ell<=rho<=u`, the coordinate intervals

```text
[ell p_i,u p_i] and [ell p'_i,u p'_i]
```

intersect for every coordinate exactly when the maximum symmetric probability
ratio is at most `u/ell`.  Their coordinatewise lower intersection endpoints
form a valid common subprobability law because they are no larger than either
clean coordinate.

## G. Prior-art conclusion

The representation, Boolean inversion, concentration, Le Cam, robust
contamination, missing-data, and choice-sampling ingredients are classical.
The v0.61 object is a checked composition for the ASMP-9 tier ledger.  Neither
this audit nor a passing verification establishes novelty.

