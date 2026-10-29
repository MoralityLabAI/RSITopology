# ASMP-12 budget-by-temptation survival protocol v0.2

## Status and attribution

This exact CPU successor was scoped only after the v0.1 result. It binds the
additive prior-art audit and does not claim a new persistence or equilibrium
theorem. The equilibrium correspondence is not assumed to be an ordinary
bifiltration.

## Frozen universe

Reuse the complete v0.1 universe of 512 ordered catalogs of three total
source-table programs. Primary costs are `(1,2,3)` and budgets are `{1,2,3}`.
Only pure program equilibria are in scope.

Use two symmetric payoff families with `R=3`:

- `pd_order`: `S=0`, `P=1`;
- `chicken_order`: `S=1`, `P=0`.

Sweep temptation exactly over

`T in {0, 1/2, 1, 2, 3, 4, 5, 6}`.

All calculations use rational arithmetic.

## Primary object

For every catalog, family, temptation, and budget, construct the directed
profitable-deviation graph on admitted program profiles. A pure equilibrium is
a profile with no outgoing profitable-deviation edge. Track cooperative
equilibrium and payoff-vector births/deaths between adjacent budgets.

For each cooperative equilibrium, define its deviation margin as the minimum,
over all nontrivial unilateral deviations, of current payoff minus deviating
payoff. Positive margin means strict robustness, zero means a boundary tie.

## Frozen hypotheses and gates

- **U0 universe:** exactly `512*2*8=8192` catalog-family-temptation cells.
- **F0 temptation phase:** cooperative deaths are absent for every `T<=R`,
  present for every `T>R`, and constant within each family over all registered
  `T>R` cells, because only the ordinal comparison `T>R` changes there.
- **B0 boundary liveness:** in the canonical `DDD/DCC/DDD` catalog,
  `(p1,p1)` survives budget 3 at `T=R` with zero margin, survives at
  `T=R-1/100`, and dies at `T=R+1/100`.
- **E0 decomposition:** syntax-equivalence deaths occur only for `T>R`; none
  occur in duplicate-extensional catalogs; and general cooperative deaths
  remain present in duplicate-extensional catalogs for `T>R`.
- **M0 margin certificate:** equilibrium status agrees exactly with nonnegative
  deviation margin wherever a nontrivial deviation exists. Every positive
  margin `m` yields the registered sup-norm payoff-perturbation certificate
  `epsilon=m/4`, whose worst-case residual margin is at least `m/2>0`.
- **P0 encoding:** adding two to every program cost reproduces every surface
  cell after shifting the raw budget by two.
- **N0 source-blind null:** source-blind catalogs have no
  syntax-equivalence-labelled deaths.

All gates are conjunctive. A pass returns
`equilibrium_survival_phase_established_for_registered_finite_class`; otherwise
the verdict is `instrument_failed`.

## Interpretation

A pass establishes a finite survival phase controlled by the temptation versus
cooperation payoff ordering and validates deviation margin as a local stability
certificate. It does not supply an ordinary persistence module, a bottleneck
stability theorem, a mixed-equilibrium characterization, or evidence about
language-model cooperation.

