# When More Verification Options Destroy Cooperation

## An exact finite program-equilibrium survival experiment

Adding more admissible programs does not necessarily expand the set of
cooperative outcomes. In a complete census of a small source-reading program
language, cooperation was perfectly stable while the temptation payoff did not
exceed the cooperation reward, then became vulnerable immediately after that
inequality reversed.

The result is exact for the registered finite class. It is not evidence about
language-model cooperation or a new general program-equilibrium theorem.

## Central result

We enumerated all 512 ordered catalogs of three deterministic source-reading
programs. Each program maps the public source ID of its opponent to cooperate
or defect. We crossed the nested program budget with two payoff families and
eight exact-rational temptation values.

The cooperation reward was fixed at `R=3`.

| payoff region | catalogs losing a cooperative equilibrium as budget grows |
|---|---:|
| every registered `T <= R` | **0/512** |
| every registered `T > R` | **174/512** |

The transition was exact on the canonical witness:

| temptation | deviation margin | cooperation survives? |
|---:|---:|---|
| `2.99` | `+0.01` | yes |
| `3.00` | `0` | yes under the registered no-strict-improvement convention |
| `3.01` | `-0.01` | no |

Thus the knife edge depends explicitly on equilibrium semantics: a tied
deviation at `T=R` does not destroy equilibrium because only strictly
profitable deviations count.

## Why the zero below the boundary matters

Suppose a program profile currently produces mutual cooperation, giving each
player reward `R`. A newly admitted unilateral deviation can produce only one
of the registered outcome payoffs `R`, `S`, `P`, or `T`. In both frozen payoff
families, `S` and `P` are no greater than `R`. Therefore no new deviation can be
strictly profitable while `T<=R`.

Once `T>R`, exploiting an opponent that continues to cooperate becomes
profitable. The canonical catalog proves that such a death is possible, and
the complete census measures how often it occurs.

This is elementary game-theoretic reasoning, not a novelty claim. Its role is
to identify the exact liveness boundary of the bounded source-program
instrument.

## What caused the 174 deaths?

The total partitions as follows:

| catalog class and mechanism | count |
|---|---:|
| Duplicate-extensional catalogs with genuinely new behavioral deviations | 134 |
| Non-extensional catalogs exploiting a behaviorally identical program under a different source label | 16 |
| Other non-extensional deaths | 24 |
| **Total** | **174** |

Equivalently, 134 deaths occurred among the 374 catalogs satisfying the
duplicate-extensionality restriction, while 40 occurred among the 138
non-extensional catalogs. The syntax-equivalence mechanism accounts for 16 of
those 40, not for all non-extensional deaths.

This matters because it separates two conclusions:

1. literal source-label trust creates a specific brittle failure that an
   extensionality requirement removes; but
2. even extensionally disciplined catalogs can lose cooperation when the
   larger budget admits a genuinely different profitable deviation.

The second result prevents the experiment from collapsing into the familiar
“compare behavior rather than literal code” critique.

## Robustness coverage

The experiment evaluated 32,064 cooperative-equilibrium margins for profiles
with at least one nontrivial admitted deviation.

- 12,384 had strictly positive margin and received a robustness certificate.
- 19,680 had margin exactly zero.
- No checked profile fell into an unreported intermediate category.

For positive margin `m`, perturbing every payoff entry by at most `m/4` leaves
worst-case residual margin at least `m/2>0`. Zero-margin profiles receive no
such certificate and may change status under arbitrarily small adverse
perturbations.

Profiles at budget one with no alternative admitted program are not included in
the 32,064-margin denominator.

## Cooperation is not the whole equilibrium surface

The `T=R` boundary applies specifically to destruction of already-cooperative
pure equilibria. The complete equilibrium payoff correspondence changes in
additional lower-temptation strata:

| family | `T=0` | `T=1/2` | `T=1` | `T=2` | `T=3` | `T>3` |
|---|---:|---:|---:|---:|---:|---:|
| PD-order catalogs with payoff death | 118 | 118 | 118 | 187 | 187 | 234 |
| Chicken-order catalogs with payoff death | 195 | 258 | 258 | 258 | 272 | 313 |

Accordingly, catalog growth is inert below `T>R` as a threat to existing
cooperative pure equilibria—not as a transformation of the entire equilibrium
correspondence.

## What is persistent here?

The admitted program sets and their profitable-deviation graphs grow with the
budget. Equilibrium is a derived sink property and can appear or disappear.
The equilibrium sets themselves are not nested, so this experiment does not
claim an ordinary persistence module or bifiltration.

A later mathematical construction could use a directed deviation-graph
filtration together with zigzag or constructible persistence. That construction
has not yet been supplied and is not needed for the present finite phase
result.

## Relation to prior work

[Tennenholtz](https://doi.org/10.1016/j.geb.2004.02.002) characterizes the
unrestricted feasible, individually rational program-equilibrium payoff set.
[Cooper, Oesterheld, and Conitzer](https://arxiv.org/abs/2412.14570) provide
modern simulation-based characterizations and robustness results. General
sensitivity of equilibrium sets to added strategies is classical; the
[sustainable-equilibrium literature](https://doi.org/10.1016/j.jet.2023.105736)
also makes strategy addition explicit.

The contribution here is narrower: a preregistered complete finite census of
when cooperation dies under a source-program budget, with an exact payoff phase
boundary and a decomposition of syntax-sensitive versus extensional deaths.

## Verification record

- 7 preregistered scientific gates passed.
- 4 v0.2 implementation tests passed.
- 4 earlier v0.1 regression tests also passed, for 8 combined ASMP-12 tests.
- An independent implementation reproduced the primary cooperative-death
  counts at `T=2,3,4,5` as `0,0,174,174`.
- Prereveal source commit: `9416b63`.
- Registration commit: `0dc9235`.
- Result commit: `fd6117d`.

## Claim boundary

This experiment establishes an exact pure-equilibrium survival phase only for
the registered three-program lookup-table language and two payoff families. It
does not characterize mixed or unrestricted program equilibria, bounded proof
search, equilibrium-selection dynamics, language-model source conditioning,
or cooperation among deployed systems.

