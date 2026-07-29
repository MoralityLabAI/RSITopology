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

Development verification after adding the coupling quotient:

```text
focused v0.33 tests                    19 passed
v0.28-v0.33 predecessor/current tests 101 passed
coupling JSON replay                   byte-identical
coupling JSON SHA-256                  fec3848759731410ede1296300e5e33b20bdb5d7f21ed806ae7592d58f4fb433
```

These checks establish implementation consistency, not prospective
registration chronology or theorem novelty.

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

## Coupling quotient

The source chain contains two differently shaped registered objects:

```text
v0.31 localized observation rows      8
v0.32 semantic cross-differences      6
raw observation-to-semantic coupling  8 x 6 = 48 coordinates
```

No physical `8 x 6` coupling was registered or estimated. However, a unique
coupling is not required for the downstream decision question. Let `C` be
v0.32's cross-difference operator, `K` an arbitrary `8 x 6` coupling, `L`
v0.31's analysis map, and `Q` the registered policy-difference matrix. The
decision effect is:

```text
Q L K C.
```

Under column-major vectorization its canonical operator is
`transpose(C) kron (Q L)`. The sealed matrices give:

```text
rank(C)                         6
rank(Q L)                       3
decision-relevant dimension    18
decision-null gauge dimension  30
```

An exact nonzero coupling witness lies in the 30-dimensional gauge and has
zero policy effect; a one-coordinate coupling changes registered policy
margins. Restricting the answer to one policy pair reduces the relevant
dimension to six and enlarges the gauge to 42. The result is proved and
executed in
[`COUPLING_QUOTIENT_THEOREM_v0_33.md`](COUPLING_QUOTIENT_THEOREM_v0_33.md)
and
[`COUPLING_DEVELOPMENT_RESULT_v0_33.json`](COUPLING_DEVELOPMENT_RESULT_v0_33.json).

This characterizes the quotient over all possible couplings. It does not
estimate the physical coupling or show that arbitrary scalar queries of it
are available.

## Next theorem obligation

Before v0.33 can freeze:

1. register a coupling-acquisition grammar and test whether it spans the
   18-dimensional decision quotient;
2. distinguish the exact nonasymptotic lower bound from imported asymptotic
   achievability;
3. freeze per-query costs;
4. add uniform, staged, and channel-ablated design controls; and
5. decide whether invalid behavioral models are answers
   (`not_certified`) or parameters outside the admitted model.

Nothing here establishes a practical response law, validates expected
utility, proves a finite-sample upper bound, or resolves ASMP-9.
