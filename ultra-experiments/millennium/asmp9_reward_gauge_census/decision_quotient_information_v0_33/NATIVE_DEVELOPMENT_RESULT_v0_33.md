# ASMP-9-native decision-information development result

## Status

**Unregistered development result. Not claim-eligible.**

This run replaces the v0.33 XOR control with a finite observation model
generated from sealed ASMP-9 source objects:

- v0.29's quotient measurement matrix, decision-null gauge, true reward, and
  two policy occupancies;
- v0.28's rational calibrated-response link;
- v0.32's consistent and distorted mixture-affinity controls; and
- v0.31's and v0.32's registered matrix dimensions.

## Decision quotient

The five hypotheses and their downstream answers are:

| hypothesis | changed object | answer |
|---|---|---|
| `base` | none | `policy_1` |
| `reward_flip` | reward coordinates | `policy_0` |
| `mechanics_flip` | policy occupancies | `policy_0` |
| `mixture_invalid` | compound-lottery consistency | `not_certified` |
| `gauge_alias` | decision-null reward coordinate | `policy_1` |

The `gauge_alias` has exactly the same law as `base`. Consequently:

```text
full parameter information rate  0
decision-quotient information    positive
```

This is the intended distinction: exact reward representatives need not be
identified when they induce the same registered decision.

## Access boundary

The complete return, mechanics, and mixture-audit query family is
decision-identifying. Removing any one complete family makes one
decision-changing alternative observationally indistinguishable:

```text
remove return queries      characteristic rate 0
remove mechanics probe     characteristic rate 0
remove mixture audit       characteristic rate 0
```

Thus each channel is necessary in this finite registry.

## Equal-cost characteristic design

The three live divergences at the base instance are:

```text
d_R = KL(Ber(1/4) || Ber(3/4)) = (1/2) log(3)
d_M = KL(Ber(3/4) || Ber(1/4)) = (1/2) log(3)
d_A = KL(Ber(1/2) || Ber(9/17)) = (1/2) log(289/288)
```

Because the three alternatives are separated by disjoint query families:

```text
C* = 1 / (1/d_R + 1/d_M + 1/d_A)
   = 0.0017222364062393738.
```

The optimal equal-cost allocation is:

```text
return family       0.003135294268967823
mechanics family    0.0031352942689678235
mixture audit       0.9937294114620643
```

At `delta=0.05`, the registered change-of-measure expression evaluates to:

```text
kl(0.95,0.05)/C* = 1538.6941488690566
```

This is a lower bound in equal query-cost units for the finite model. It is
not a rounded sufficient sample count and not an operational budget.

The mixture audit dominates because the v0.32 distortion is only `1/16`
under the imported response link. The implementation supports arbitrary
positive query costs; a prospective protocol must freeze costs or a
sensitivity surface before interpreting the allocation.

## Integration gap found

The source chain is not yet end-to-end:

```text
v0.31 localized observation rows      8
v0.32 semantic cross-differences      6
registered map from residuals to rows absent
```

A matrix shape mismatch is not itself a defect: an `8 x 6`
observation-to-semantic coupling could connect the objects. The problem is
that no such coupling or coupling class was registered. The native fixture
therefore uses v0.29's complete measurement-to-policy cell and reports the
v0.31-v0.32 composition as unavailable.

## Next theorem obligation

Before v0.33 can freeze:

1. register the missing coupling, or quantify over a declared coupling class;
2. distinguish the exact nonasymptotic lower bound from imported asymptotic
   achievability;
3. freeze per-query costs;
4. add uniform, staged, and channel-ablated design controls; and
5. decide whether invalid behavioral models are answers
   (`not_certified`) or parameters outside the admitted model.

Nothing here establishes a practical response law, validates expected
utility, proves a finite-sample upper bound, or resolves ASMP-9.
