# ASMP-9 finite stochastic-choice trichotomy result v0.54

## Verdict

**`finite_stochastic_choice_trichotomy_verified`**

For the registered complete three-alternative stochastic-choice grammar, the
verification assigns every kernel to exactly one of:

```text
one positive Luce ratio scale;
a random-utility distribution over strict rankings, but no Luce scale;
no random-utility representation in the declared class.
```

This is an exact instrument built from classical Luce and
Block-Marschak/Falmagne/McFadden-Richter representation results. It is not a
new stochastic-choice theorem.

## Prospective binding

- development commit: `bd657f184ce78750ab6e865d21a59696bd0297d1`
- verification-source commit: `b08d903dec85cc955376a2d00e8577c97baf1bb8`
- registration commit: `f2ac9a90186a868e07699960453c48009ea3c268`
- registration SHA-256:
  `0cb1d81be606d884c566eeabcfca17225bffb9e2f81bd1c869993403e8d80659`
- verification-result commit: `c3922c134b2648959dd1048b1067b46e9b6cd06b`
- verification-result SHA-256:
  `6dae986df802f327ac893b3ad0fece8043767d9d13d8288db5cc3dc26223b015`

The development census was committed before the independent verifier and
registration. The write-once result was generated only after the registration
commit.

## Gates

All nine registered gates passed:

| gate | result |
|---|---|
| H0 source integrity | PASS |
| T0 registered tests | PASS |
| C0 census completeness | PASS |
| E0 equivalent rationalizability decisions | PASS |
| S0 scalar tier | PASS |
| R0 middle tier | PASS |
| N0 no-object tier | PASS |
| A0 binary-access insufficiency | PASS |
| RESOURCE | PASS |

The registered test command passed `11/11` tests.

## Exact census

Every strictly positive stochastic choice kernel on `{a,b,c}` whose menu
probabilities lie on the denominator-six grid was classified:

| classification | kernels |
|---|---:|
| `scalar_luce` | 1 |
| `random_utility_non_luce` | 230 |
| `no_random_utility_representation` | 1,019 |
| **total** | **1,250** |

Across the full census:

```text
Block-Marschak / ranking-simplex decision mismatches  0
ranking-mixture reproduction failures                0
certificate failures                                  0
Luce kernels without a ranking mixture                0
```

## The three exact witnesses

### One scalar

Weights proportional to `(1,2,3)` generate:

```text
p(. | ab)  = (1/3,2/3)
p(. | ac)  = (1/4,3/4)
p(. | bc)  = (2/5,3/5)
p(. | abc) = (1/6,1/3,1/2).
```

The verifier recovered the normalized scale
`(1/6,1/3,1/2)` and an exact random-ordering mixture.

### Weaker stochastic preference object

Equal mass on the rankings

```text
a>b>c, b>c>a, c>a>b
```

induces a strictly positive random-utility kernel. It fails the Luce
pair/full-menu identities, so no single ratio scale represents it.

### No object in the declared class

Fair pairwise choices combined with

```text
p(. | abc) = (3/4,1/8,1/8)
```

violate regularity. The registered exact certificate is:

```text
q(a,{a,b}) = p(a | ab) - p(a | abc) = -1/4.
```

No nonnegative distribution over the six strict rankings reproduces this
kernel.

## Access result

The uniform Luce kernel and the no-object kernel agree on every binary menu,
yet lie at opposite ends of the trichotomy once the ternary menu is observed.
Therefore binary-menu access is insufficient to decide the declared
three-alternative value object. Full ternary-menu access is decisive in this
registered grammar.

## What this changes

Earlier ASMP-9 versions reconstructed and audited scalar responses under a
coherence promise. Version v0.54 makes the promise testable at the object
level:

```text
scalar reconstruction is authorized only in the Luce tier;
a random-ordering object replaces it in the middle tier;
and the declared latent-value interpretation is rejected in the final tier.
```

That closes one finite behavioral well-posedness cell identified as missing
after v0.53.

## What this does not establish

- Novelty of the representation mathematics.
- Identification on arbitrary incomplete menu domains.
- Finite-sample classification or minimax rates.
- Robustness to ties, weak orders, nonstationarity, strategic response, or
  context-dependent latent classes.
- That humans or language models follow Luce or random-utility laws.
- That a behaviorally recovered scale is morally or welfare relevant.
- A physically valid preference-access channel.
- A complete ASMP-9 resolution.

## Resource record

The independent verification used one worker, completed in `9.734329` seconds,
and recorded `21,999,616` resident bytes, below the frozen 60-second and
256-MiB caps.

## Claim boundary

Version v0.54 is a certificate-bearing finite specialization of classical
stochastic-choice theory. ASMP-9 remains unresolved.

