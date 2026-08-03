# ASMP-12 constructible survival correspondence protocol v0.3

## Objective and inherited universe

This additive CPU-exact successor builds the explicit constructible object left
open by v0.2. It reuses without modification:

- all 512 ordered catalogs of three total source-table programs;
- program costs `(1,2,3)` and budgets `{1,2,3}`;
- the `pd_order` and `chicken_order` payoff families with `R=3`; and
- the exact temptation grid `{0,1/2,1,2,3,4,5,6}`.

Only pure equilibria and strict profitable deviations are in scope. All payoff,
gain, and margin calculations use `fractions.Fraction`.

## Weighted cell graph

At every `(catalog,family,T,budget)` cell, admit all program profiles allowed by
the budget. A typed directed edge

`(profile -> unilateral-deviation profile, player)`

exists exactly when that player receives a strictly positive payoff gain. The
gain is retained as an exact rational cell decoration. A pure equilibrium is a
vertex with no outgoing profitable edge. Cooperative sinks are equilibria whose
source-table actions are `(1,1)`.

For every vertex with a nontrivial deviation, its signed margin is the minimum
of `current payoff - deviating payoff`. Thus a vertex is a sink exactly when its
margin is nonnegative. Zero is a reported tie, not a strict edge.

## Budget-axis maps

For each adjacent budget pair, the primary code proposes the identity inclusion
on old profiles. It records a graph map only after verifying all of the
following exactly:

1. old vertices are a subset of new vertices;
2. old profitable edges are a subset of new profitable edges; and
3. the rational gain on every old edge is unchanged.

The `budget=1 -> 2 -> 3` composite is checked independently. Cooperative sink
births and deaths are not graph maps; they are stored in a separate event
layer.

## Temptation-axis zigzag

Payoff changes can add and remove profitable edges, so no unverified forward
inclusion is asserted. For every adjacent temptation pair and fixed budget the
object is

`G_T -> (G_T union G_T') <- G_T'`.

The union and both arrows are taken in the category of finite underlying
directed graphs. Endpoint-specific exact gains are retained as a pair of
decorations on every union edge. The relation is classified as equal, verified
forward inclusion, verified reverse inclusion, or incomparable. Direct maps
are reported only in the verified comparable cases.

Concatenating adjacent spans gives an explicit finite constructible zigzag over
the registered temptation grid. No weight-preserving temptation map is claimed.

## Separate sink-event and margin certificates

For every adjacent budget or temptation cell pair, cooperative sink births and
deaths are derived after graph construction and stored separately from maps.
Each event binds:

- the endpoint cells and profile;
- exact left and right signed margins;
- endpoint cooperative-sink status; and
- every exact positive-gain edge witnessing the nonsink endpoint.

Deaths require a nonnegative/undefined sink margin on the left and a negative
margin plus an outgoing profitable edge on the right. Births satisfy the
reverse condition, except that a budget birth may introduce a genuinely new
vertex.

## Independent verifier

The independent implementation imports no v0.3 primary code. From the passed
catalogs and frozen parameters it reconstructs every cell graph, gain, margin,
sink set, and cooperative sink set. It then independently checks every budget
inclusion, every adjacent union and endpoint decoration, and the complete sink
event signature set.

## Five robustness probes

1. **Cost padding:** adding two to every cost and raw budget reproduces every
   graph exactly.
2. **Program-label equivariance:** a nontrivial simultaneous relabeling of
   program rows, source columns, costs, vertices, and edges gives isomorphic
   weighted graphs at every cell.
3. **Source-blind column null:** permuting source columns in every source-blind
   catalog leaves every graph unchanged.
4. **Exact boundary microgrid:** the canonical `(1,1)` profile has margins
   `+1/100,0,-1/100` at `T=2.99,3,3.01`, with sink status `yes,yes,no`.
5. **Positive-margin perturbation:** each positive cooperative-sink margin `m`
   carries `epsilon=m/4`, leaving residual comparison margin
   `m-2epsilon=m/2>0`; zero-margin cells remain explicit controls.

## Conjunctive gates

- every one of `512*2*8*3=24,576` cell graphs is typed and margin-consistent;
- all `512*2*8*2=16,384` budget inclusions and composites verify;
- all `512*2*7*3=21,504` adjacent-union zigzags verify, including live
  nonmonotone steps;
- sink events remain separate and all event certificates verify;
- the independent reconstruction passes; and
- exactly five robustness probes pass.

A complete pass yields
`finite_constructible_survival_correspondence_built`; any failure yields
`instrument_failed`.

## Four conclusion layers

The report separates `task_result`, `reliability`, `claim_support`, and
`operation`. Graph construction is not conflated with reliability evidence;
reliability is not conflated with broader equilibrium claims; and operational
facts do not imply scientific support.
