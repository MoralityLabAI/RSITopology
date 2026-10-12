# Hostile proof audit: general incomplete-menu theorem v0.56

Status: **internal development audit, not independent peer review**.

## Claim under audit

For a finite universe of `n>=3` alternatives and unrestricted positive
completion of unqueried non-singleton menus:

1. every proper-domain dataset with a RUM completion also has a non-RUM
   completion; and
2. every proper-domain dataset with a Luce completion also has a RUM
   non-Luce completion.

## Dependency audit

### A. Explicit non-RUM completion

**Status: valid under the registered grammar.**

Every proper domain omits a non-singleton menu.  Altering that menu and, only
when necessary, one other unobserved comparable menu creates a strict
regularity violation while preserving all observed probabilities.  Strict
positivity is retained by choosing probabilities in the open simplex.

This argument would not apply if the completion class itself imposed
regularity or another cross-menu structural law.  The theorem explicitly says
unrestricted completion.

### B. Full affine dimension of the RUM polytope

**Status: self-contained proof supplied.**

An affine functional constant on all ranking kernels remains constant under
every adjacent swap.  For a fixed swapped pair, varying the lower set produces
the Boolean zeta transform of the within-menu coefficient differences.
Möbius inversion sets every difference to zero.  Only menu-normalization
equalities remain.

The machine check confirms the corresponding affine ranks for `n=3,4,5` and
the zeta-system invertibility through width five.  Those checks exercise but
do not replace the general proof.

### C. Interior Plackett-Luce point

**Status: valid.**

Positive Plackett-Luce weights induce positive mass on every strict ranking.
A positive convex combination of every finite generator is in the relative
interior of their convex hull.  Full affine dimension upgrades relative
interior to ambient interior in the product of menu simplices.

### D. RUM fiber dimension

**Status: valid.**

Observed complete menu vectors are a coordinate projection of the ambient
product.  The projection has rank

```text
d_D = sum_{A in D} (|A|-1).
```

At an interior point, its level set intersects the RUM polytope in a relatively
open set of dimension `k=d-d_D`.

### E. Luce fiber dimension

**Status: valid for strictly positive observations.**

Observed probability ratios fix weight ratios within each connected component
of the observed co-occurrence graph.  If there are `c` components, the
remaining component scales have dimension `c-1` after quotienting global
scale.  The resulting full-kernel Luce family is a rational, hence
semialgebraic, image of at most that dimension.

Zeros would require a separate censored-choice treatment.  They are excluded.

### F. Strict dimension gap

**Status: valid and sharp at `n=3`.**

If the observed graph is connected, properness leaves at least one missing
coordinate, so `k>=1>0=c-1`.

If it has `c>=2` components, every cross-component pair menu is missing.  For
component sizes `n_i`,

```text
k >= sum_{i<j} n_i*n_j > c-1
```

when `n>=3`.  For two components, the left side is at least `n-1>=2`.
For at least three components, it is at least `choose(c,2)>c-1`.

At `n=2`, the empty-domain fiber dimensions are equal and every positive
binary kernel is Luce.  Thus the theorem's `n>=3` condition is necessary.

### G. Dimension implies a non-Luce RUM point

**Status: valid.**

The RUM fiber contains a relatively open `k`-ball.  Its matching Luce subset
is semialgebraic of dimension at most `c-1<k`, hence has empty relative
interior.  The ball contains a non-Luce RUM point.  Taking it sufficiently
close to the positive Plackett-Luce point preserves strict positivity.

## Prior-art audit

The following are explicitly attributed:

- limited-domain RUM feasibility and extension variables: McFadden-Richter,
  Stoye, Turansick, and Clark;
- complete-domain random-scale representation: Falmagne;
- arbitrary-menu Luce falsification, identification, and prediction:
  Alos-Ferrer and Mihm.

The exact tier-identification corollary has not been located in this bounded
search.  Absence from the search is not evidence of novelty.  A direct match
would subsume the candidate theorem without changing its use as an ASMP-9
access lemma.

## Scope audit

- Singleton menus are omitted because their choice probability is fixed at
  one and they contribute no access coordinate.
- Menus are exogenous and fully observed when queried.
- Rankings are strict; ties are excluded.
- Probabilities are exact and positive.
- Completion is unrestricted except for positivity.
- The theorem identifies a model tier of the response kernel, not moral value,
  welfare, a human preference, or a language-model objective.

## Audit verdict

**`proof_ready_for_prospective_verification`**

No counterexample remains inside the declared finite exact grammar.  The
result remains a candidate theorem until prospective verification and
independent external proof review.
