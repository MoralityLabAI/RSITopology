# ASMP-9 bounded context-degree development result v0.57

Status: **unregistered development result; not claim eligible**.

## Result

The proposed structured-completion theorem survived its first proof and
implementation audit.

For a positive stochastic-choice kernel, let every pairwise log-odds function
over the remaining menu context have Boolean Mobius degree at most `r`.
Then:

1. observing all menus through size `r+2` reconstructs every unobserved
   pairwise odds ratio and therefore the full kernel;
2. menus through size `r+1` are insufficient for full-kernel recovery; and
3. for every fixed `n>=r+2` and `r>=1`, the lower domain cannot even
   distinguish a uniform Luce kernel from a positive kernel that violates RUM
   regularity.

This supplies a non-circular positive counterpart to v0.56's unrestricted
completion no-go: bounded context degree restricts how responses extend across
menus without assuming that the completed kernel is Luce or RUM.

## Fixed-universe lower witness

For a selected `(r+2)`-menu `A_0`, the non-RUM kernel is uniform on every menu
through size `r+1`. On `A_0`, one alternative has probability

```text
(r+2)/(2r+3) > 1/2,
```

while its probability on every binary submenu is `1/2`. This is an explicit
regularity violation. A contextual-score construction extends the witness to
every larger menu while keeping all pairwise log odds at degree at most `r`.

The construction was checked for all 21 `(n,r)` cells with

```text
3 <= n <= 8,
1 <= r <= n-2.
```

## Approximation quantity

The proof also yields the exact deterministic interpolation condition number.
For a target pair context of size `s>r`, low-context sup-norm error `epsilon`
can amplify to

```text
K(s,r) epsilon,

K(s,r)
  = sum_(u=0)^r choose(s,u) choose(s-u-1,r-u).
```

The coefficient is sharp for the unconstrained interpolation operator.
Representative worst-target values `K(n-2,r)` are:

| `n` | values across `r=0,...,n-2` |
|---:|---|
| 3 | `1, 1` |
| 4 | `1, 3, 1` |
| 5 | `1, 5, 7, 1` |
| 6 | `1, 7, 17, 15, 1` |
| 7 | `1, 9, 31, 49, 31, 1` |
| 8 | `1, 11, 49, 111, 129, 63, 1` |

The terminal `1` occurs because `r=n-2` requires observing the full menu, so
the largest context is no longer extrapolated. The large interior constants
show why exact identifiability does not imply statistically useful recovery.
Tier decisions additionally require probability floors and separation from
the Luce and RUM boundaries.

## Verification

Development test suite:

```text
7 passed
```

Independent verifier, which does not import the implementation module:

```json
{
  "degree_cells": 21,
  "exact_probability_checks": 9335,
  "high_degree_zero_checks": 4952,
  "r0_boundary_checked": true,
  "reconstructed_pair_contexts": 15366,
  "registered": false,
  "regularity_witnesses": 77,
  "status": "development_checks_passed",
  "universe_sizes": [3, 4, 5, 6, 7, 8]
}
```

These checks support the finite implementation and witness family. They do not
prove the arbitrary-`n` theorem.

## Prior-art verdict

The log-ratio hierarchy is Batsell-Polking, and Boolean/contextual order
decompositions plus context-model identifiability have direct modern precedent
in Seshadri, Peysakhovich, and Ugander. Mobius inversion is classical. The
candidate residual is only the sharp nested menu-access/tier consequence and
its fixed-universe lower witness. Novelty is not established.

## Freeze decision

Do **not** register yet. Before a prospective freeze:

1. independently review the indexing in the pairwise-degree construction;
2. search the Batsell-Polking descendants for the exact same access threshold;
3. decide whether the deterministic condition number belongs in the frozen
   theorem or in a separate approximate successor; and
4. freeze an explicit tier-margin object before making any finite-sample claim.

## Claim boundary

This development closes neither empirical model selection nor finite-sample
tier certification. It does not show bounded context degree in human or model
choice, handle zeros/ties/endogenous menus, provide welfare semantics, or
resolve ASMP-9.
