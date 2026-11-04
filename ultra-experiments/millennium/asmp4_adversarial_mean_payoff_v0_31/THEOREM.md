# ASMP-4 finite adversarial mean-payoff region v0.31

## 1. Registered finite public game

Let `G` be a finite turn-based public game obtained from a supplied exact
v0.26 quotient. Controller states select registered safe public actions;
adversary states select registered successors. Every edge has a nonnegative
rational two-port cost

`c(e)=(c_r(e),c_w(e)).`

The action/successor presentation in v0.26 becomes this standard bipartite
form by inserting an adversary state after each controller action. This changes
no play, cost word, or strategy.

For a play `pi=e_0 e_1 ...`, define

`J_i(pi)=limsup_(n->infinity) (1/n) sum_(t<n) c_i(e_t)`.

A budget `R=(R_r,R_w)` is achievable when one controller strategy ensures
`J_i(pi)<=R_i` in both coordinates on every consistent adversarial play.
Strategies may use arbitrary public-history memory unless stated otherwise.

## 2. Fixed-policy cycle polytopes

Let `Tau` be the finite set of memoryless adversary policies. Fixing
`tau in Tau` leaves a one-player directed graph `G_tau` in which controller
choices remain.

For each reachable cyclic strongly connected component `C` of `G_tau`, let

`P_(tau,C)=conv{mean_c(gamma): gamma is a simple cycle in C}`.

Write `up(P)` for its coordinatewise upward closure. Define

`Q_tau = union_C up(P_(tau,C)).`

The component union is deliberately not convexified across irreversible SCCs.

## 3. Exact adversarial region theorem

The complete arbitrary-memory budget region is

`R(G) = intersection_(tau in Tau) Q_tau`

or, with all quantifiers displayed,

`R(G) = intersection_tau union_C
        up(conv{mean_c(gamma): gamma simple in C of G_tau}).`

### Proof

Fix a candidate budget `R` and transform every cost edge into the reward

`w_R(e)=R-c(e)`.

For every play and coordinate,

`liminf average(w_R) = R - limsup average(c)`.

Thus the cost objective is exactly the conjunction of two
mean-payoff-`inf` reward objectives at threshold zero.
In the plain-text terminology used by the classical literature, this is the
conjunctive mean-payoff-inf objective, and winning it may require infinite memory.

Classical multi-mean-payoff determinacy gives a memoryless adversary strategy
whenever the controller loses this conjunctive objective. Consequently, the
controller wins in `G` exactly when no memoryless `tau` spoils, equivalently
when the controller wins the one-player objective in every `G_tau`.

In a one-player finite graph, the conjunctive mean-payoff-`inf` objective is
winnable exactly when some reachable SCC has a nonnegative reward multicycle.
A multicycle is a nonnegative combination of simple cycles. After normalizing
by total length, its reward condition is

`sum_gamma alpha_gamma mean_w(gamma) >= (0,0)`,

which under `w_R=R-c` is precisely

`sum_gamma alpha_gamma mean_c(gamma) <= R`.

That says the cost cycle polytope intersects the lower orthant below `R`, or
`R in up(P_(tau,C))`. Substituting this one-player criterion for every
memoryless adversary policy proves the formula. QED.

The proof's quantifier bridge is load-bearing. The winning one-player strategy
may depend on `tau`; the classical memoryless-spoiler theorem plus determinacy,
not an illicit exchange of controller and adversary quantifiers, yields one
winning controller strategy in the original game.

## 4. Geometry and decidability

There are finitely many memoryless adversary policies, SCCs, and simple cycles.
Each `P_(tau,C)` is a rational polytope. Hence `R(G)` is a closed upward finite
Boolean combination of rational polyhedra: a finite intersection of finite
component unions. It may be nonconvex.

For the two ASMP-4 coordinates, membership can be checked exactly with rational
arithmetic: enumerate memoryless adversary policies, reachable SCCs, and simple
cycle means, then test whether each fixed-policy cycle hull intersects the
budget's lower orthant. The implementation emits a feasible component and
convex point for each nonspoiling policy, or one concrete memoryless spoiler.

This is a finite exact characterization, not a claim of a polynomial-time
algorithm for all dimensions or a new complexity bound. The classical
threshold problem is coNP-complete.

## 5. Finite-memory closure

Exact boundary play may require infinite controller memory. Nevertheless, if
`R in R(G)`, then for every rational `epsilon>0` a finite-memory strategy
ensures `R+(epsilon,epsilon)`. Conversely every finite-memory strategy is an
arbitrary-memory strategy. Because the formula above is closed,

`closure(R_finite_memory(G)) = R(G).`

This distinction matches the canonical conjecture's use of a closed capacity
region: finite-state implementations are dense in the arbitrary-memory region,
but a particular closed boundary point need not itself have a finite-memory
realizer.

## 6. Infinite-memory connector boundary

Consider a one-player two-state graph. The self-loop costs are `(0,2)` and
`(2,0)`, and both connector edges cost `(2,2)`. The two self-loop means have
convex midpoint `(1,1)`, so the theorem includes budget `(1,1)`.

No simple cycle lies below `(1,1)`. More strongly, every finite-memory strategy
has an ultimately periodic outcome. A period confined to one state violates
one coordinate with rate two; a period visiting both states pays positive
connector density and has coordinate sum strictly above two. Hence no
finite-memory strategy attains `(1,1)`.

A period with `k` loops at each state and both connectors has equal coordinate
rate

`(2k+4)/(2k+2) = 1 + 1/(k+1).`

This gives the exact finite-memory approximation slack. To attain the boundary,
run successively longer balanced loop blocks; connector density and the
within-block imbalance both tend to zero. This is the cost-sign translation of
the classical infinite-memory multi-mean-payoff example.

## 7. Quantifier and nonconvex boundaries

- **Adversarial fork.** An adversary irreversibly chooses an absorbing loop of
  cost `(1,3)` or `(3,1)`. The robust region is the intersection of the two
  quadrants, with corner `(3,3)`. Existential policy choice is false.
- **Controller fork.** A controller irreversibly chooses the same two loops.
  The region is their union. The midpoint `(2,2)` lies in the global convex
  hull but in neither true component region, reproducing v0.25's component
  disjunction inside the new formula.
- **Cost polarity.** Alternating increasingly dominant `(0,2)` and `(2,0)`
  bursts gives coordinatewise cost liminf zero and cost limsup two. Replacing
  the registered cost limsup by liminf changes the objective.

## 8. Relation to v0.25 and v0.26

If there are no adversary states, `Tau` contains the empty policy and the
formula reduces exactly to v0.25's union of reachable SCC cycle-polytopes. If
an exact finite alternating quotient is supplied, v0.26 transfers the raw
public-history region to that quotient and this theorem computes its complete
additive two-port region. This closes the nondeterministic finite-quotient seam
explicitly left open in v0.26.

## 9. Scope

The theorem assumes a finite exact public quotient and additive rational edge
costs. It does not construct that quotient for arbitrary nonlinear or
continuous-belief plants, transfer nonadditive transcript-tree costs without
the v0.28-v0.30 factor hypotheses, or supply general exact finite-horizon
margin corrections. It also does not claim finite-memory attainment of every
closed boundary point.
