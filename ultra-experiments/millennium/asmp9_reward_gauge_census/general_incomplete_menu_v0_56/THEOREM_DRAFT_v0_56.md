# General incomplete-menu tier theorem v0.56

Status: **candidate theorem; development only**.

## Setup

Let `X` be a finite set of `n >= 3` alternatives and let

```text
M(X) = {A subseteq X : |A| >= 2}
```

be the nontrivial menu universe.  A positive stochastic-choice kernel assigns
to each `A in M(X)` a strictly positive probability vector on `A`.

For an observed domain `D subseteq M(X)`, let `p_D` contain the complete
probability vector for every menu in `D`.  A completion is any positive full
kernel agreeing with `p_D`.

The full-kernel tiers are:

```text
L  positive Luce;
R  random utility but not Luce;
N  not random utility.
```

Random utility means a probability distribution over the `n!` strict
rankings, with choice equal to the highest-ranked available alternative.

## Candidate theorem

For every proper domain `D proper-subset M(X)`:

1. if `p_D` has a random-utility completion, it also has a positive non-random-
   utility completion;
2. if `p_D` has a positive Luce completion, it also has a positive
   random-utility, non-Luce completion.

Consequently the compatible full-kernel tier set is exactly:

```text
no RUM completion                 -> {N}
RUM but no Luce completion        -> {R,N}
Luce completion                   -> {L,R,N}.
```

The complete menu domain is therefore the unique domain that can identify a
singleton tier without restrictions connecting unobserved menus to observed
menus.

## Proof of clause 1

Start from any positive RUM completion `q` and choose a missing menu `A`.

If `A != X`, choose `x in A`, `y notin A`, and set `B=A union {y}`.  If `B`
is observed, choose a new positive vector on `A` with

```text
q'(x|A) < p_D(x|B).
```

If `B` is unobserved, choose positive vectors on both menus satisfying
`q'(x|A) < q'(x|B)`.  All other missing menus retain their values from `q`.

If `A=X`, choose a two-element `B subset X` containing `x`.  If `B` is
observed, choose a positive vector on `X` with

```text
q'(x|X) > p_D(x|B).
```

If `B` is unobserved, choose positive vectors on both menus satisfying the
same strict inequality.

Each construction changes only unobserved menus and violates random-utility
regularity:

```text
B subset A and x in B  implies  q(x|A) <= q(x|B).
```

Thus `q'` is a positive non-RUM completion.  This proves clause 1
constructively.

## Proof of clause 2

Let

```text
d = sum_{A in M(X)} (|A|-1)
d_D = sum_{A in D} (|A|-1)
k = d-d_D.
```

The classical random-utility polytope is full-dimensional in the `d`
dimensional product of menu simplices.  A positive Plackett-Luce distribution
assigns positive mass to every strict ranking, so its choice kernel lies in
the relative interior of that polytope.

Projecting onto the observed menus has rank `d_D`.  Therefore the RUM
completion fiber through a positive Luce kernel contains a relatively open
`k`-dimensional neighborhood.

Form the observed comparison graph `G_D`: alternatives are vertices, and two
alternatives are adjacent when they occur together in an observed menu.  If
`G_D` has `c` connected components, positive observed Luce ratios determine
the alternative weights inside each component.  The Luce completions matching
`p_D` therefore have dimension `c-1`, one relative component scale after
quotienting the global scale.

It remains to show `k > c-1`.

- If `c=1`, properness gives `k >= 1 > 0`.
- If `c>=2`, every pair whose endpoints lie in different components is an
  unobserved menu.  If the component sizes are `n_1,...,n_c`, then

```text
k >= sum_{i<j} n_i n_j.
```

  For `c=2`, this is at least `n-1 >= 2 > 1`.  For `c>=3`, it is at least
  `choose(c,2) > c-1`.

Hence the RUM fiber has strictly larger dimension than its Luce subset.  The
Luce subset cannot contain a relatively open neighborhood of the RUM fiber.
There is therefore a positive RUM completion arbitrarily close to the
Plackett-Luce point that is not Luce.  This proves clause 2.

## Machine-checkable support

The companion code checks:

- exact affine rank `d` of the deterministic-ranking choice polytope for
  `n=3,4,5`;
- `k>c-1` for every proper menu domain for `n=3,4`; and
- the explicit regularity-violation construction for every such domain.

These finite checks test the proof implementation.  They do not establish the
arbitrary-`n` claim.

## Proof debt before registration

1. Cite or supply a self-contained proof that the deterministic-ranking
   choice polytope is full-dimensional for every finite `n`.
2. State the semialgebraic-dimension step excluding a Luce-open subset of the
   larger RUM fiber with full precision.
3. Search specifically for an existing incomplete-menu tier-identification
   theorem that subsumes the result.
4. Obtain a hostile review of whether strict positivity and the treatment of
   singleton menus leave any exceptional domains.

## Claim boundary

Even if verified, this is a finite exact access theorem under unrestricted
completion.  It is not a finite-sample result, a theorem about endogenous or
strategic demonstrators, evidence about human or model values, a welfare
representation, or a full ASMP-9 resolution.
