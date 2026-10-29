# ASMP-12 finite pure program-frontier protocol v0.1

## Status and prior-art binding

This protocol follows `PRIOR_ART_v0_1.md`, SHA-256
`9fd0606ff82af0da3441efe895ccae22755ebe27295dce8f6c67457c3806bd3f`.
The experiment is an exact diagnostic and counterexample census, not a new
program-equilibrium theorem.

## Program language

Freeze three public source IDs `{0,1,2}`. A total deterministic program is a
three-bit response row. Bit `p[j]` is the action program `p` returns after
reading opponent source ID `j`, with `1=cooperate` and `0=defect`.

A catalog is an ordered triple of response rows, one per public source ID.
Rows may be identical: this represents distinct source labels with identical
behavior on the complete registered opponent universe. All `8^3=512` catalogs
are enumerated.

The primary encoding assigns costs `(1,2,3)`. Budget `B` admits programs with
cost at most `B`, so the program sets are nested. A pure program equilibrium is
a pair of admitted program IDs with no strictly profitable unilateral
deviation to another admitted program. Deviating changes the source ID seen by
the opponent, as required by source-reading semantics.

Only pure equilibria are in scope.

## Games

Use three frozen symmetric 2x2 games, with row-player payoffs listed first:

- Prisoner's Dilemma: `CC=(3,3)`, `CD=(0,5)`, `DC=(5,0)`, `DD=(1,1)`;
- Stag Hunt: `CC=(4,4)`, `CD=(0,3)`, `DC=(3,0)`, `DD=(2,2)`;
- Chicken: `CC=(3,3)`, `CD=(1,4)`, `DC=(4,1)`, `DD=(0,0)`.

## Primary observables

For every catalog, game, and budget:

1. the pure equilibrium profiles;
2. the realized equilibrium payoff set;
3. cooperative-equilibrium births and deaths between adjacent budgets; and
4. payoff-vector births and deaths between adjacent budgets.

A cooperative death is `syntax_equivalence_exploited` when the newly admitted
profitable deviator has the same complete response row as an older admitted
program, while the incumbent opponent responds differently to those two
source IDs.

## Extensionality and null controls

A catalog is `extensional_on_duplicates` when, whenever two program rows are
identical, every program gives those two source IDs the same response. This is
a finite decidable proxy for robustness to logically equivalent opponent
implementations.

A catalog is `source_blind` when every program row is constant. Such a catalog
cannot distinguish opponent source IDs.

The registered canonical witness is:

```text
p0 = DDD
p1 = DCC
p2 = DDD
```

At budget 2, `(p1,p1)` is a cooperative equilibrium. At budget 3, `p2` can
exploit `p1`, even though `p2` and `p0` have identical response rows, because
`p1` defects against source ID 0 but cooperates with source ID 2.

The matched repaired catalog changes `p1` to `DCD`; its self-cooperative
equilibrium must survive the duplicate-program extension.

## Encoding control

The padded encoding assigns costs `(3,4,5)`, adding exactly two units to every
program. For every catalog and game, the complete equilibrium record at raw
budget `B+2` under the padded encoding must equal the record at budget `B`
under the primary encoding. This establishes only additive encoding shift, not
general compiler invariance.

## Frozen gates

- **U0 universe:** exactly 512 catalogs and 1,536 catalog-game cases are
  enumerated.
- **W0 witness:** the canonical catalog has the registered cooperative
  equilibrium at budget 2, loses it at budget 3 through the specified
  extensionally equivalent exploiter, and loses the cooperative payoff.
- **L0 liveness:** the Prisoner's-Dilemma census contains at least one
  cooperative-equilibrium death and at least one payoff-set death.
- **E0 extensional control:** no death classified
  `syntax_equivalence_exploited` occurs in a catalog satisfying
  `extensional_on_duplicates`; the matched repaired catalog survives.
- **N0 source-blind null:** no source-blind catalog has a syntax-equivalence
  death.
- **P0 padding:** all primary/padded equilibrium records agree after the
  registered additive budget shift.

All gates are conjunctive. A pass returns
`finite_pure_frontier_nonmonotonicity_demonstrated`; otherwise the instrument
returns `instrument_failed`.

## Claim boundary

A pass establishes a minimal counterexample to monotonic pure cooperative
payoff frontiers in this frozen source-table language and locates a
syntax-sensitive mechanism. It does not characterize mixed or unrestricted
program equilibria, robust bounded-Löbian agents, simulation-based folk
theorems, proof resources, negotiation dynamics, or real AI cooperation.

