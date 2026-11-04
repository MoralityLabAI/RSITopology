# ASMP-12 inertial equilibrium-selector result v0.4

## Disposition

The registered finite selector experiment completed and passed its
import-independent replay:

```text
task_result: finite_initialized_inertial_selector_threshold_computed
measurement_reliability: independent_exact_graph_trace_and_source_replay_passed
claim_support: finite_registered_selector_claim_supported
operational_decision: no_deployment_authorization
```

This is a genuine equilibrium-selection-dynamic attempt in the registered
three-program source-table language.  It does not characterize general
selection dynamics or resolve ASMP-12.

## Frozen evidence chain

- Source commit:
  `37e25f725325c4b0d9949fd32a86408fa85e9af4`.
- Primary-artifact commit:
  `e7a963e340e399f06f5901cdbf039b2e66590183`.
- Independent-verification commit:
  `99dd0f89456337478a093ae65c0208f28d9bff23`.
- Primary artifact: `result_v0_4.json`, 306,272 canonical JSON bytes,
  SHA-256
  `1da70cd580b7c03c2c43339ec908f3b1e8d577e912a125a65f4965305d931b41`.
- Verification artifact: `verification_v0_4.json`, 7,374 canonical JSON
  bytes, SHA-256
  `863d079a88504d8b98fbd383a52b69b239e13ded1e24b93433ed609222cb7d2a`.

The source directory contains exactly eight committed regular files.  The
manifest passed the experiment-contract validator with zero errors and zero
warnings.  Before execution, 19 source-only tests passed and one postcommit
binding test skipped as designed; after the source commit all 20 tests passed.
Ruff and ASCII-only checks passed.

## Registered selector

The canonical catalog and attached costs are

```text
p0 = DDD, cost 1
p1 = DCC, cost 2
p2 = DDD, cost 3
```

The initial profile is `(p1,p1)`.  Each mover stays when its incumbent program
is an exact best response; otherwise it chooses the best response with minimum
attached cost.  Row-first and column-first schedules then alternate forever.
The declared fair scheduler places exact weight `1/2` on each first mover.

The two payoff families both use `R=3`; `pd_threshold` has `(S,P)=(0,1)` and
`chicken_threshold` has `(S,P)=(1,0)`.  The exact temptation values are
`299/100`, `3`, and `301/100`, at budgets two and three.

For each of the 12 `(family,T,budget)` cells, the primary constructed the
complete deterministic functional graph on all augmented
`(row_program,column_program,next_player)` states.  The registry contains 156
states in total, 35 exact attractors with basin certificates, 24 initialized
traces, and 12 fair-schedule distributions.

## Selection result

Exactly 20 of 24 initialized traces selected cooperation and four selected
noncooperation.

- Every budget-two trace stays at `(p1,p1)`.
- Every budget-three trace with `T<=R` also stays at `(p1,p1)`.  Equality is
  retained by the frozen inertia rule.
- At budget three with `T=301/100`, admitting `p2` changes the selected
  equilibrium:

| family | row first | column first | fair-schedule distribution |
|---|---|---|---|
| `pd_threshold` | `(p2,p0)` | `(p0,p2)` | half on each, payoff `(1,1)` |
| `chicken_threshold` | `(p2,p1)` | `(p1,p2)` | half on each mirror exploitation outcome |

Thus existence and selection are separate even in this tiny language.  The
complete graph contains other available equilibria; the initialized mover
order selects the two displayed mirror outcomes.  Every selected terminal
profile was independently confirmed to be a pure equilibrium and to belong
to the independently reconstructed attractor reached by its initial state.

## Controls and scope breakers

- Repairing the catalog to `DDD/DCD/DDD` retained cooperation in all 24
  matched trajectories.
- Source-blind `DDD/CCC/DDD` retained only 16 cooperative trajectories: above
  the threshold it is vulnerable already at budget two.  Budget-two and
  budget-three outcomes nevertheless match, so this control separates early
  ordinary exploitation from the canonical late-admission effect.
- Adding two to every attached cost and budget preserved all 72 mapped traces,
  36 complete graph relations, and 36 selected distributions.
- All six simultaneous program/source/cost relabelings preserved 432 mapped
  traces, 216 graph relations, and 216 selected distributions.
- A real six-state augmented cycle in catalog `CCD/DCC/CDC` exercised the same
  graph and trace machinery used by the primary selector.
- Removing incumbent inertia changed the registered tie outcome, making the
  tie rule live.
- Maximum-attached-cost tie-breaking changed the above-threshold PD selection.
  Simultaneous updates selected `(p2,p2)` in PD and produced the exact
  `(p1,p1) <-> (p2,p2)` Chicken cycle.  These are scope breakers, not claims
  about a preferred alternative dynamic.

All five registered robustness families passed: encoding invariance,
threshold sensitivity, registered monotonicity, anti-gaming, and clean
controls.

## Independent replay and resources

The verifier imported no primary implementation.  It independently rebuilt
all 12 augmented graphs, 24 traces, 12 schedule distributions, controls,
scope breakers, source and predecessor bindings, and resource observations.
All 11 verifier gates passed and every graph, row, aggregate, control, and
metric mismatch list was empty.

The primary scientific core used 4.625 seconds of measured wall time and
2,202,309 bytes of peak traced Python allocation.  Independent replay used
11.766 seconds and 2,670,725 traced bytes.  Both stayed below the frozen
15-second and 64-MiB limits.  Native allocations and process RSS were not
measured; this limitation is explicit in both artifacts.

## Claim boundary

The supported claim is only for the declared catalog, two payoff families,
three temptation values, two budgets, one initialized profile, alternating
inertial minimum-cost best response, and an exact fair distribution over the
two first movers.  Complete basins are reported only for those 12 finite
graphs.  The result says nothing general about other catalogs, other dynamics,
mixed or correlated equilibria, stochastic learning, unrestricted programs,
proof agents, language-model cooperation, deployment, or resolution of
ASMP-12.
