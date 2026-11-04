# ASMP-12 inertial selector protocol v0.4

## Status

This directory is source-only until exactly the eight files named by the
manifest are reviewed and committed together. The 12 registered graph cells,
24 initialized trajectories, robustness replays, and both artifacts are
forbidden before that commit. Source tests may exercise isolated fixtures but
must not call `compile_result` or enumerate the registered grid.

The benefit is a model-only robustness/theory test. V0.1 established finite
pure-equilibrium nonmonotonicity; v0.2 established the exact `T>R` cooperative
survival boundary; v0.3.1 built and independently verified the finite
constructible profitable-deviation correspondence. None selected an available
equilibrium. This successor supplies one explicit selector, not a general
theory of equilibrium selection.

## Frozen game and selector

Programs are total three-bit source tables with `1=C` and `0=D`. The primary
catalog and attached costs are

```text
p0=DDD, cost 1
p1=DCC, cost 2
p2=DDD, cost 3
```

The inherited initial profile is `(p1,p1)`. Budgets two and three admit the
programs whose attached cost is at most the budget. Both payoff families use
`R=3`; `pd_threshold` uses `(S,P)=(0,1)` and `chicken_threshold` uses
`(S,P)=(1,0)`. Temptation is exactly `299/100`, `3`, or `301/100`.

A state is `(row_program,column_program,next_player)`. The first player is
frozen as row or column and movers then alternate. At an update, the mover
computes every admitted pure best response with exact rational payoffs. If the
incumbent is a best response it stays. Otherwise the mover chooses the best
response with minimum attached cost; registered costs are distinct, so the
choice is unique. A complete no-change round identifies a fixed pure profile.
Otherwise the first repeated augmented state identifies the attractor cycle.
There are at most `2*|P_B|^2` augmented states and at most one additional
transition is needed to expose a repeat.

For each of the 12 `(family,T,budget)` cells, construct the complete functional
graph over all augmented states, every transition, canonical attractor cycles,
and exact basin sizes. The two initialized schedule states are bound to their
reported attractor. This is a genuine finite dynamic object, but no statement
is made about another catalog or another update rule.

## Frozen predictions

The 24 initialized trajectories contain exactly 20 cooperative and four
noncooperative selections. Budget two always leaves `(p1,p1)`. At budget three,
`T<=R` also leaves `(p1,p1)`. At `T>R`:

| family | row first | column first |
|---|---|---|
| `pd_threshold` | `(p2,p0)` | `(p0,p2)` |
| `chicken_threshold` | `(p2,p1)` | `(p1,p2)` |

Every terminal initialized profile must be a pure equilibrium of that cell.
The fair scheduler is the exact distribution placing weight `1/2` on each
first-mover trace. Schedules select distinct equilibrium profiles only in the
two budget-three, above-threshold family cells; their cooperation status still
agrees.

## Controls and causal scope breakers

- `DDD/DCD/DDD` repairs the duplicate treatment and must keep `(p1,p1)` in all
  24 matched trajectories.
- Source-blind `DDD/CCC/DDD` is an early-vulnerability control, not an
  all-cooperative control. At `T<=R` it stays cooperative; at `T>R` it is already
  vulnerable at budget two. Its matched budget-two and budget-three outcome
  must therefore agree for every family and schedule.
- Adding two to every attached cost and raw budget must reproduce every
  semantic trace, complete graph relation with attractor basins, and fair
  selected distribution.
- All six simultaneous permutations of program rows, opponent-source columns,
  attached costs, and initial profile must map every trace, complete graph
  relation with attractor basins, and fair selected distribution back exactly.
- An incumbent-best-response fixture distinguishes inertia from a
  non-inertial tie rule; an explicit repeated-state fixture proves cycle
  detection.
- Maximum-attached-cost tie-breaking and simultaneous updates are frozen scope
  breakers. The former changes the selected PD profile above threshold.
  Simultaneous updates select `(p2,p2)` in PD and create the exact
  `(p1,p1)<->(p2,p2)` cycle in Chicken above threshold.

Metric robustness is reported in five separate probe families: encoding
invariance, threshold sensitivity, registered-grid monotonicity, anti-gaming,
and clean controls. Probe rows are repeated checks, not new experimental units.

## Evidence and resources

The primary and independent paths use `Fraction`, deterministic lexicographic
registries, no RNG, and no determinant, root solver, or mixed-equilibrium
algorithm. The verifier imports no primary module and reconstructs the payoff
law, best-response choices, all graph edges, attractors, basins, initialized
traces, controls, predecessor bytes, and source commit.

Ceilings are 15 wall seconds, 64 MiB peak traced Python allocation, 19 scheduled
updates per trajectory, and one MiB per canonical JSON artifact. Execution is
sequential. Resource stops and any missing, duplicate, reordered, or inexact
cell downgrade every conclusion layer. Both artifacts are exclusive-create in
the sibling artifact directory.

## Claim boundary

A passing independent verification supports only the finite initialized
deterministic/fair-two-schedule selector and the 12 complete canonical graphs
defined above. It does not support a basin-general statement outside those
graphs, mixed or correlated equilibria, stochastic learning, unrestricted
programs, proof agents, language-model cooperation, deployment, or resolution
of ASMP-12.
