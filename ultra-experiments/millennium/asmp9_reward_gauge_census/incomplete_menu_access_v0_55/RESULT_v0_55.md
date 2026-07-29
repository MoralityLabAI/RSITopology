# ASMP-9 incomplete-menu tier-identification result v0.55

## Verdict

**`incomplete_menu_tier_identification_verified`**

For the registered three-alternative unrestricted-completion grammar:

> Partial menu data can refute every random-utility completion, but a proper
> menu domain cannot certify that the unseen full response kernel belongs to
> random utility merely because one rationalizing completion exists.

Existential stochastic rationalizability is classical
McFadden-Richter ARSP. The result here is an exact access ledger separating
existence of one model from identification of the full-kernel value-object
tier.

## Prospective binding

- initial development commit:
  `8f5894f4da538a984e63a2a8d7046f35dbc5184d`
- positive-witness repair commit:
  `0f2b5d4aac55cbe58f0f8e6b1cfa74bf88fdbf3f`
- verification-source commit:
  `a7372842a21699c234ddd5cbce8257097d3fa4b8`
- registration commit:
  `43e5c82f0d6f743ff209fc0e8fb7900b93f8e25f`
- registration SHA-256:
  `2b9df78c26213db60749e8592dbfe18a2d23bfc8e2394ed13b648fc7a49b18a5`
- verification-result commit:
  `56016f617b0bb775d8be267df9945d554a6810bc`
- verification-result SHA-256:
  `2de6b2d5d229f12d112611a87de9c21eaadf9bffcf70a5923f6f399ab7282b2c`

The independent checker exposed a boundary-witness positivity seam before
registration. The repair was committed before the verification source and
registration were frozen.

## Gates

All nine registered gates passed:

| gate | result |
|---|---|
| H0 source integrity | PASS |
| T0 tests | PASS |
| D0 domain-lattice completeness | PASS |
| E0 existential compatibility | PASS |
| N0 non-RUM completion | PASS |
| R0 non-Luce RUM completion | PASS |
| TIER0 compatibility-set trichotomy | PASS |
| FULL0 complete-domain control | PASS |
| RESOURCE | PASS |

The registered test command passed `9/9` tests.

## Exact access lattice

There are four nontrivial menus:

```text
ab, ac, bc, abc
```

and 15 nonempty observed-menu domains. The verifier evaluated all 14 proper
domains and the complete-domain control.

Projecting the denominator-six full-kernel grid produced 1,125 distinct
proper-domain datasets when counted within domain:

| compatible complete-kernel tiers | datasets |
|---|---:|
| `{L,R,N}` | 128 |
| `{R,N}` | 422 |
| `{N}` | 575 |
| **total** | **1,125** |

Here:

```text
L = scalar_luce
R = random_utility_non_luce
N = no_random_utility_representation.
```

The complete-domain control reproduced v0.54:

| singleton tier | kernels |
|---|---:|
| `{L}` | 1 |
| `{R}` | 230 |
| `{N}` | 1,019 |

The complete 15-domain summary matched its prospective SHA-256:

```text
a584b8954bc7ddfb8901d7b6907fa90c0b5c0b45eb770de5c8cd30e9e6241e69
```

## Exact theorem mechanism

### Existential tests

A Luce completion exists exactly when the observed probability-ratio labels
form a consistent multiplicative potential on the comparison graph.

A random-utility completion exists exactly when the observed probability
vector lies in the convex hull of the six deterministic ranking signatures.
This is the classical ARSP result.

### Why missing menus prevent tier certification

If `abc` is unobserved, complete it so one alternative's ternary probability
exceeds its corresponding pair probability.

If `abc` is observed but a pair is missing, complete that pair below the
alternative's ternary probability.

Both constructions preserve every observation, remain strictly positive, and
violate random-utility regularity. The verifier produced such a completion for
every proper-domain projection:

```text
non-RUM construction failures  0.
```

### Why the middle tier remains live

For each of the 128 partial datasets admitting a Luce completion, the verifier
enumerated exact basic ranking mixtures and constructed a strictly positive
RUM completion outside the Luce identities:

```text
scalar-to-non-Luce-RUM witness failures  0.
```

For every one of the 422 scalar-incompatible but RUM-compatible datasets, it
also produced a positive RUM-but-non-Luce witness:

```text
middle-tier witness failures  0.
```

## The decision rule

For a proper observed domain:

```text
no RUM completion
    -> only N remains;

RUM completion but no Luce completion
    -> R and N remain;

Luce completion
    -> L, R, and N all remain.
```

Thus partial access is asymmetric: it can eliminate optimistic latent-object
classes, but cannot certify the full-kernel RUM class without assumptions on
unobserved menus.

## Prior-art boundary

The convex-hull/ARSP feasibility test, Luce graph-potential condition,
regularity inequality, and full-domain random-ordering representation are
classical. No representation-theorem novelty is claimed.

The contribution is the ASMP-9 distinction between:

```text
there exists a rationalizing completion
```

and:

```text
the observed access identifies the latent-object tier of the full response
kernel.
```

## What this does not establish

- A theorem for arbitrary finite universe size.
- A finite-sample or approximate tier decision.
- Results under structural restrictions on unobserved menus.
- Robustness to menu endogeneity, hidden alternatives, ties, weak or
  nontransitive relations, context dependence, strategic response, or
  nonstationarity.
- Human or language-model stochastic rationality.
- Moral or welfare relevance of a recovered scale.
- A physically valid preference-access channel.
- A complete ASMP-9 resolution.

## Resource record

The independent verification used one worker, completed in `19.636858`
seconds, and recorded `26,312,704` resident bytes, below the frozen 60-second
and 256-MiB caps.

## Claim boundary

Version v0.55 verifies an elementary finite completion-ambiguity theorem
layered on classical Luce and ARSP tests. ASMP-9 remains unresolved.
