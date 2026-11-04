# ASMP-12 finite pure program-frontier result v0.1

## Verdict

`finite_pure_frontier_nonmonotonicity_demonstrated`

All six frozen gates passed across all 512 three-program catalogs and all three
registered base games. The result is an exact finite counterexample census,
not a novelty-bearing program-equilibrium theorem.

| gate | result |
|---|---|
| U0: complete universe | pass |
| W0: canonical syntax witness | pass |
| L0: nonmonotonicity liveness | pass |
| E0: extensional duplicate control | pass |
| N0: source-blind null | pass |
| P0: padded-encoding replay | pass |

## Primary census

| game | catalogs with cooperative death | catalogs with payoff death | catalogs with syntax-equivalence death |
|---|---:|---:|---:|
| Prisoner's Dilemma | 174/512 | 234/512 | 16/512 |
| Stag Hunt | 0/512 | 187/512 | 0/512 |
| Chicken | 174/512 | 313/512 | 16/512 |

The resource-indexed pure equilibrium payoff set is therefore not generally
monotone even in this tiny total program language. Adding one admissible
source-reading program can remove an existing equilibrium and its payoff.

## Canonical witness

The frozen catalog was:

```text
p0 = DDD
p1 = DCC
p2 = DDD
```

At budget 2, `(p1,p1)` produces mutual cooperation and payoff `(3,3)` in the
Prisoner's Dilemma. Deviating to `p0` is not profitable because `p1` defects
against source ID 0.

At budget 3, the newly admitted `p2` has exactly the same response table as
`p0`, but `p1` cooperates with source ID 2. Either player can switch from `p1`
to `p2`, changing the outcome from `CC` to `DC` or `CD` and gaining two payoff
units. The cooperative profile and payoff `(3,3)` both die.

This is a source-syntax failure: the incumbent assigns different trust to two
programs that behave identically over the complete registered program
universe.

## Controls and the important limitation

There were 374 catalogs satisfying the registered duplicate-extensionality
condition and eight source-blind catalogs. Neither class produced a death
classified as `syntax_equivalence_exploited`. The repaired canonical catalog
also retained its cooperative equilibrium after admitting the duplicate
program.

This does **not** mean extensionality restores monotonicity. A post-gate
descriptive regrouping found cooperative deaths in 134 of the 374 extensional
catalogs for both Prisoner's Dilemma and Chicken. Those deaths use genuinely
different response programs rather than extensionally duplicate source labels.
The cross-tab was not a frozen gate and is reported only to prevent an overly
broad interpretation of E0.

Thus the result separates two claims:

1. source-label sensitivity creates a specific, preventable class of brittle
   deaths; and
2. pure equilibrium frontiers can remain nonmonotone even after that class is
   removed.

## Why Stag Hunt differs

The absence of cooperative deaths in the registered Stag Hunt is structurally
expected. A player currently receiving the cooperative reward `R=4` cannot
gain by changing the source-induced action pair: the other available payoffs
are at most `T=3`, `P=2`, and `S=0`. In Prisoner's Dilemma and Chicken,
defecting while the opponent cooperates gives `T>R`, so a newly admitted
program can destroy a cooperative equilibrium by exploitation.

This is an explanatory observation about the frozen payoff tables, not an
additional registered general theorem.

## Encoding result

Adding two cost units to every program shifted every raw budget threshold by
exactly two while leaving every admitted program set and equilibrium record
identical after normalization. Absolute code-budget numbers are therefore
encoding-relative even in this elementary control. The experiment establishes
only this additive replay, not compiler invariance for general languages.

## Consequence for ASMP-12

The bounded object should not be assumed to be an expanding payoff frontier.
For a fixed program language it is more faithfully represented as a
resource-indexed birth/death diagram:

```text
budget -> admitted programs -> equilibrium profiles -> payoff births/deaths
```

Existence and selection also remain distinct. This experiment enumerates what
pure equilibria are available; it does not measure which equilibrium a
negotiation, mutation, proof-search, or learning dynamic selects.

## Artifact binding

- prior-art commit: `e9e76dae989ecb79fb2b37a30e23b71c4b7525bf`;
- prereveal source commit: `53c6cb2cb4d5cac0b0ea772a704276a0a18f6c91`;
- registration commit: `3b9d98c2624bd30fc34e23f506ba36d294d2ce0c`;
- registration SHA-256:
  `a958cd8647f17d5be4446bb650e79c4fbc3ebc6694f8dc2d0a16ecb354a80914`;
- result SHA-256:
  `7416476c6cfc85a0b538e4c5956b39741f9b1521fd26f7fbfbfd8056a971f887`;
- receipt SHA-256:
  `189aab3d0e10deedc93f1a970725238533aceaac97e5462f8b327a27ce13a5b8`;
- tests: `4 passed`.

## Claim boundary

The result establishes nonmonotonicity and one syntax-sensitive mechanism only
for pure equilibria in the registered three-program lookup-table language. It
does not characterize mixed or unrestricted program equilibria, proof-bounded
agents, simulation-based equilibria, equilibrium-selection dynamics, or real
AI cooperation. The prior-art audit classifies the work as an instrument and
classical finite-game reasoning, not a novel program-equilibrium theorem.
