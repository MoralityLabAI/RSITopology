# ASMP-9 v0.19 prior-art gate

Status: development-only; must be complete before v0.19 registration.

## Binding decision

Do not claim novelty for:

- series-system reliability as a product of subsystem reliabilities;
- redundancy or test-resource allocation under an integer budget;
- dynamic programming for separable integer resource allocation;
- greedy optimality under diminishing marginal returns;
- failure of greedy outside its concavity conditions; or
- pseudo-polynomial dependence on an integer resource budget.

## Primary anchors

### Reliability and redundancy allocation

- P. M. Ghare and R. E. Taylor, "Optimal Redundancy for Reliability in
  Series Systems," *Operations Research* 17(5), 1969, 838-847:
  <https://doi.org/10.1287/opre.17.5.838>.
  This is direct classical ancestry for maximizing a series-system
  reliability objective under resource restrictions.

- K. B. Misra and C. E. Carter, "Redundancy allocations in a system with many
  stages," *Microelectronics Reliability* 12(3), 1973, 223-228:
  <https://doi.org/10.1016/0026-2714(73)90588-X>.
  This work explicitly treats exact versus approximate allocation in
  multistage systems.

- Chunghun Ha and Way Kuo, "Reliability redundancy allocation: An improved
  realization for nonconvex nonlinear programming problems," *European
  Journal of Operational Research* 171(1), 2006, 24-38:
  <https://doi.org/10.1016/j.ejor.2004.06.006>.
  This locates general coherent-system redundancy allocation as a classical
  nonconvex integer optimization problem and develops exact branch-and-bound
  machinery.

### Greedy resource allocation

- Awi Federgruen and Henri Groenevelt, "The Greedy Procedure for Resource
  Allocation Problems: Necessary and Sufficient Conditions for Optimality,"
  *Operations Research* 34(6), 1986, 909-918:
  <https://doi.org/10.1287/opre.34.6.909>.
  This is the controlling reference for greedy allocation under separable or
  weakly concave objectives. The v0.19 cycle response fails the required
  diminishing-returns shape on exact finite cells, so the repository must not
  present the failed greedy rule as a new algorithmic surprise.

## Surviving contribution

The candidate contribution is the ASMP-9-specific reduction:

```text
conditional comparison fiber
  -> residual liveness on a cactus cyclic core
  -> independent cycle events
  -> exact product of v0.16 cycle availabilities
  -> classical separable integer resource allocation.
```

The exact Bellman recurrence is classical. Its role is to close the
finite-budget cactus subclass left open by v0.18, preserve exact rational
certificates, and exhibit why the asymptotically uniform allocation cannot be
promoted to an every-budget rule.

## Permitted language after a passing registration

Permitted:

> In the frozen ASMP-9 comparison model, exact finite-budget design on a
> cactus cyclic core reduces to a series-product resource-allocation problem.
> Within-cycle counts balance, while per-cycle totals require exact dynamic
> programming because marginal returns are not discretely concave.

Not permitted:

> We introduce dynamic programming for redundancy allocation.

Not permitted:

> We solve finite-budget reliability allocation in general.

Not permitted:

> This identifies human values or resolves ASMP-9.

