# ASMP-9 general incomplete-menu theorem result v0.56

## Verdict

**`general_incomplete_menu_theorem_verified`**

For every finite alternative universe with `n>=3`, let the observed domain be
a proper subset of the non-singleton menus and allow unrestricted positive
completion of unqueried menus.  Then:

```text
no RUM completion             -> compatible tiers {N}
RUM but no Luce completion    -> compatible tiers {R,N}
Luce completion               -> compatible tiers {L,R,N}.
```

Thus partial menu data can refute random utility, but cannot certify the
unseen full kernel as random utility merely because one rationalizing
completion exists.  Complete nontrivial-menu access is the sharp exact access
threshold for identifying a singleton tier under this completion grammar.

Here:

```text
L = positive Luce
R = random utility but not Luce
N = not random utility.
```

## Prospective binding

- proof-audit commit:
  `ba8a3cd7d5398d2e22ff1ce3532231a70544478f`
- verification-source commit:
  `bea9b7e6340f0759da57dd9158f8afb8ffc49589`
- registration commit:
  `84b4a035f8ee70f54b0711803a03c6b67e2ecd5f`
- registration SHA-256:
  `16046963b9e7fa6db585ec63f68e09b685927ebcf0bea65ea1bcf4d3a001ad65`
- verification-result commit:
  `f133f7fe1812cfed7b99fcbd5a038351146ebb7a`
- verification-result SHA-256:
  `08cc4ff81ff66bd2c58ae48376cfb1e6ca6ca8da54ae09b53623d02ff11a88c9`

The development checks were burned before registration.  The `n=6` affine-
rank target, seeded five-alternative witness suite, partition range, resource
caps, and sharpness checks were frozen before the write-once verification.

## Proof

### Non-RUM completion

Choose any missing menu.  If it has a larger comparable menu, set the missing
menu's probability for one alternative below the larger-menu probability.  If
the missing menu is the full universe, set its probability above a smaller-
menu probability.  When the comparable menu is also missing, set both.

This preserves every observation, remains strictly positive, and violates
random-utility regularity.  Hence every proper-domain RUM-compatible dataset
also admits a positive non-RUM completion.

### RUM non-Luce completion

The ambient stochastic-choice dimension is:

```text
d = sum_A (|A|-1) = n*2^(n-1) - 2^n + 1.
```

An adjacent swap in a deterministic ranking yields, for every lower set, the
Boolean zeta transform of within-menu affine-coefficient differences.
Möbius inversion forces every difference to zero.  Consequently deterministic
ranking kernels affinely span the full ambient product of menu simplices.

A positive Plackett-Luce ranking mixture is therefore an interior point of the
RUM polytope.  If `k` choice coordinates are unobserved, its RUM completion
fiber contains a relatively open `k`-ball.

If the observed co-occurrence graph has `c` connected components, the matching
Luce completions have dimension at most `c-1`: observed ratios fix weights
inside components, leaving only relative component scales.  Properness gives:

```text
k > c-1
```

for every `n>=3`.  The lower-dimensional Luce subset cannot fill the RUM
fiber, so a positive RUM non-Luce completion exists arbitrarily close to the
Plackett-Luce point.

### Sharpness

At `n=2`, the proper empty-domain RUM and Luce fibers both have dimension one,
and every positive binary choice vector is Luce.  The second clause fails.
The condition `n>=3` is necessary.

## Verification

All nine gates passed:

| gate | result |
|---|---|
| H0 source integrity | PASS |
| T0 tests | PASS |
| A6 held-out affine rank | PASS |
| Z0 Möbius-system rank | PASS |
| G0 component-gap partitions | PASS |
| N0 constructive non-RUM extensions | PASS |
| S0 `n=2` sharpness | PASS |
| F0 ambient-dimension formula | PASS |
| RESOURCE | PASS |

The registered tests passed `11/11`.

Held-out measurements:

```text
n=6 ranking signatures                 720
affine columns                         130
rank modulo 1,000,003                  130
component partitions checked         2,692
partition failures                       0
five-alternative witness cases          312
witness failures                          0
```

Verification completed in `7.283694` seconds with `24,109,056` resident bytes
and one worker, below the frozen 120-second and 512-MiB caps.

## Prior-art boundary

Limited-domain random-utility feasibility and completion variables are
classical McFadden-Richter/Clark/Stoye territory and are implemented directly
by Turansick.  Complete-domain random-scale representation is classical
Falmagne.  Alos-Ferrer and Mihm characterize Luce falsification,
identification, and prediction on arbitrary menu collections.

No novelty is claimed for those ingredients.  The result packages them into
an ASMP-9 full-kernel tier-identification threshold.  Exact novelty of that
corollary has not been established.

## What this does not establish

- Approximate or finite-sample tier identification.
- Results with zeros, ties, weak or nontransitive rankings.
- Endogenous or hidden menus and unobservable alternatives within menus.
- Context-dependent, adaptive, strategic, or nonstationary behavior.
- Identification under structural restrictions on unqueried responses.
- Human or language-model stochastic rationality.
- Moral or welfare relevance of a recovered representation.
- A physically valid preference-access channel.
- A complete ASMP-9 resolution.

## Claim boundary

Version v0.56 verifies a finite exact full-kernel tier-identification theorem
under unrestricted positive completion.  It closes the arbitrary finite
strict-choice extension of v0.55, not the approximate, behavioral, strategic,
physical-channel, or welfare obligations.  ASMP-9 remains unresolved.
