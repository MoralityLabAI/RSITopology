# Finite-scheduler periodic-completeness theorem

## 1. Registered scheduler

Let `G=(S,E)` be a finite directed multigraph with a nonempty public initial
set. Each edge is a registered safe block choice and carries a nonnegative
cost vector `c(e)=(c_r(e),c_w(e))`, the additive logarithmic read/write
transcript cost of that block. An admissible causal public schedule is an
infinite enabled walk. Its rate is the coordinatewise limsup of average edge
cost.

This is the finite-additive public-state subclass of v0.24. It includes public
reset schedules and finite scheduler memory; it does not assert that an
arbitrary nonlinear controller admits finite sufficient state or additive
costs.

## 2. Cycle-mean polytope

For a directed cycle `gamma`, let

`m(gamma)=sum_(e in gamma)c(e)/|gamma|`.

For each reachable cyclic strongly connected component `C`, define

`P_C=conv{m(gamma):gamma is a simple directed cycle in C}`

and `R_C=upward_closure(P_C)`.

**Theorem 1.** The complete finite-scheduler capacity region is

`R = union_C R_C`,

where the union ranges over reachable cyclic SCCs.

**Proof.** The condensation graph of a finite directed graph is acyclic, so an
infinite walk changes SCC only finitely many times and eventually remains in
one reachable cyclic component. Its finite prefix has zero asymptotic cost.
Inside that component, delete directed cycles successively from a long finite
walk. The remaining simple path has bounded length, while the deleted edge
multiset is a nonnegative combination of simple cycles. Every accumulation
point of average costs therefore lies in `P_C`; the coordinatewise limsup rate
lies in its upward closure.

Conversely, repeat any simple cycle to realize its mean periodically. To
realize a rational convex combination of cycle means inside one SCC, repeat
the cycles in the desired proportions and join them by fixed directed paths.
The number and length of connectors are bounded per superperiod, so making
each repeated cycle block long sends connector overhead to zero. Arbitrary
convex combinations follow by rational approximation and closure. This proves
both inclusions.

## 3. Component support formula and periodic completeness

For `0<=lambda<=1`, define

`h_C(lambda)=min_gamma [lambda m_r(gamma)+(1-lambda)m_w(gamma)]`.

This is the classical minimum-cycle-mean value for the scalarized edge cost
`lambda c_r+(1-lambda)c_w`. It is a finite concave piecewise-linear lower
envelope. By v0.24 and Theorem 1,

`R_C=intersection_lambda
     {(r,w):lambda r+(1-lambda)w>=h_C(lambda)}`.

If the reachable recurrent graph is one SCC, this single support family is
the full region and periodic closed walks are dense in its Pareto boundary.
Strong connectivity, or a bounded registered reset hub connecting all
scheduler states, is therefore a sufficient periodic block-completeness
condition.

## 4. Positive connector fixture

Two scheduler states have self-loop means `(1,3)` and `(3,1)`. Both connector
edges have cost `(5,5)`, making the graph strongly connected. Its three simple
cycle means are

`(1,3)`, `(3,1)`, and `(5,5)`.

The last is dominated. The exact polytope has segment boundary joining the
first two points. A periodic closed walk with `k` left loops, both connectors,
and `k` right loops has length `2k+2` and rate

`((4k+10)/(2k+2),(4k+10)/(2k+2))
 = (2+3/(k+1),2+3/(k+1))`.

It converges to `(2,2)`, explicitly showing bounded connector overhead vanish.

## 5. Irreversible-fork boundary

From a transient initial state, choose irreversibly between two absorbing
loop components with corners `(1,3)` and `(3,1)`. The true region is the union
of their two upward quadrants. The point `(2,2)` is in neither quadrant.

If the component index is discarded, the global lower support value is the
minimum of the two component support values. Its supporting half-spaces
describe the convex hull and falsely include `(2,2)`. Hence the correct general
formula is a **component-indexed disjunction of support families**, not one
support family after minimizing across irreversible components.

This does not contradict v0.24: the fork lacks reset concatenability between
its two recurrent choices. It locates exactly where that hypothesis is
load-bearing.

## 6. Scope

The cycle decomposition is classical finite graph/mean-payoff structure. The
ASMP-4 contribution is the precise mapping to two charged transcript costs and
the distinction between within-component convexification and across-component
disjunction. The theorem does not cover infinite belief state, nonadditive
transcript-tree costs, hidden scheduler state, unsafe connectors, or general
nonstationary nonlinear control without a finite public abstraction.
