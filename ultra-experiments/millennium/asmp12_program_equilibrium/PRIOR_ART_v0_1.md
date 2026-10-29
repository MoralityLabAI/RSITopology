# ASMP-12 prior-art audit v0.1

## Frozen proposed novelty sentence

> No theorem novelty is proposed for the finite census. The intended
> contribution is a preregistered diagnostic showing when a nested program
> budget has equilibrium-payoff births and deaths, and whether observed deaths
> depend on treating extensionally equivalent opponent programs differently by
> source label.

## Search record

- date: 2026-07-20;
- queries:
  - `Moshe Tennenholtz program equilibrium payoff feasible individually rational`;
  - `program equilibria discounted computation time Fortnow`;
  - `bounded Lob robust cooperation bounded agents Critch`;
  - `simulation-based program equilibria characterization`;
  - `program equilibrium bounded complexity finite programs`; and
  - `Nash equilibrium expanding strategy sets nonmonotone`.
- sources: publisher pages, author-hosted papers, arXiv, ACM, and related
  primary papers returned by those searches.

This is a bounded scoping audit, not an exhaustive literature review.

## Primary-source map

### Unrestricted program-equilibrium payoff sets

Moshe Tennenholtz, [“Program
equilibrium”](https://doi.org/10.1016/j.geb.2004.02.002), *Games and Economic
Behavior* 49(2), 2004, proves that the program-equilibrium payoff set coincides
with the feasible individually rational payoff set in the declared model. Any
unqualified claim that this payoff set lacks a characterization is subsumed.

### Computational costs

Lance Fortnow, [“Program Equilibria and Discounted Computation
Time”](https://doi.org/10.1145/1562814.1562833), TARK 2009, introduces general
computational models with payoffs discounted by runtime. A finite resource
study must distinguish hard admission budgets from payoff discounting rather
than presenting computation cost as new.

### Proof-bounded robust cooperation

Andrew Critch, [“Parametric Bounded Löb's Theorem and Robust Cooperation of
Bounded Agents”](https://arxiv.org/abs/1602.04184), constructs robust
cooperation results for bounded proof-searching agents. A single finite
cooperative program pair would be strictly weaker than this prior result.

### Simulation-based characterizations

Emery Cooper, Caspar Oesterheld, and Vincent Conitzer,
[“Characterising Simulation-Based Program
Equilibria”](https://arxiv.org/abs/2412.14570), characterize broad
simulation-based constructions, including positive folk-theorem-style regions
and limits without shared randomness. The ASMP-12 frontier must not imply that
simulation-based achievable sets are wholly uncharted.

## Disposition

`partial_extension` as an instrument, not a theorem claim.

The open/scoped object is a resource-indexed sequence for one fully declared
finite program language, together with robustness to encoding and logically
equivalent implementations. The planned census does not compete with the
unrestricted folk theorem, bounded Löb cooperation, or recent simulation-based
characterizations.

## Proposed bounded instrument

Freeze a maximal catalog of total deterministic source-reading programs. Each
program is a Boolean response table over the public source IDs of every program
in the catalog. A nested length budget admits a prefix of that catalog. For a
fixed 2x2 base game, enumerate pure program equilibria exactly at every budget
and record payoff births and deaths.

The specific red-team target is a cooperative equilibrium that is stable at
budget `B` but destroyed at `B+1` by a newly admitted program extensionally
equivalent to an older program. Such a death is possible only because an
incumbent treats two behaviorally identical opponent implementations
differently by source label. A matched extensionality control filters catalogs
so identical response rows must receive identical responses from every
program.

## Hostile-referee pass

1. **“The lookup tables hard-code the effect.”** Correct. A positive census is
   a minimal counterexample and validator for a resource-frontier diagnostic,
   not evidence that natural agents exhibit the pathology.
2. **“Nash equilibria can change when strategies are added.”** Correct and
   elementary. The point is to prevent ASMP-12 from assuming a monotone
   frontier and to identify a source-semantic mechanism for one class of
   deaths, not to claim a new equilibrium theorem.
3. **“Extensional equivalence is undecidable for general programs.”** Correct.
   It is decidable only because the registered language is a finite total
   lookup-table language. Generalization requires a different equivalence
   instrument or a labelled approximation.
4. **“Pure equilibria omit mixed program equilibria.”** Correct. The seed is a
   pure-frontier diagnostic. It may not claim the full `P_B(G)` of the ASMP-12
   statement.
5. **“Encoding can move the budget.”** The protocol must include a padding
   control and report raw thresholds only relative to the frozen encoding.

## Conservative external description

> An exact finite census tests whether a source-sensitive pure
> program-equilibrium frontier is monotone under a nested code budget and
> distinguishes syntax-only cooperative-equilibrium deaths from deaths that
> survive an extensionality restriction.

## Claim boundary

The audit and proposed census do not characterize unrestricted program
equilibria, bounded-proof cooperation, mixed equilibria, negotiation dynamics,
or real AI-agent cooperation. They define a small falsification instrument for
resource-frontier assumptions.
