# ASMP-9 v0.50 reference-law robustness theorem draft

## Setup

Let `X` be a finite outcome set. For each declared decision objective `d`, let
`B_d(S)` be its direct-Buehler subset-bound table. An ordering `pi` assigns to
each outcome `x` the bound at the prefix where `x` appears. Write this feature
vector as

```text
b_d^pi(x) = B_d(S_pi(x)).
```

For reference law `w` in the strictly positive probability simplex,

```text
C_d(pi;w) = <w,b_d^pi>.
```

Let the registered reference-law family be the rational polytope

```text
W = conv{v_1,...,v_k},
```

with every generator `v_i` strictly positive.

## Theorem 1: ordering region

For a fixed ordering `pi`, define

```text
R_pi(D)
  = {
      w in simplex :
      <w,b_d^pi-b_d^sigma> <= 0
      for every d in D and every ordering sigma
    }.
```

Then `R_pi(D)` is a rational polytope. It is exactly the set of reference laws
for which `pi` is optimal for every declared objective.

*Proof.* Every ordering cost is linear in `w`. Joint optimality is precisely
the displayed finite family of linear inequalities. QED.

The reference-weight space therefore carries an exact finite atlas of
possibly overlapping ordering regions. The union need not be represented by
one chain.

## Theorem 2: vertex and robust-chain characterization

An ordering `pi` is jointly optimal for every `d in D` and every `w in W` if
and only if it is jointly optimal for every pair `(d,v_i)`.

Equivalently, compute the tight-predecessor DAG for each objective/vertex
scenario. A robust common ordering exists if and only if the intersection of
all those DAGs has an `empty`-to-`X` path. Path count is the exact number of
robust orderings. If no path exists, the reachable-set boundary labelled by
the blocking `(objective,vertex)` scenarios is a finite obstruction.

*Proof.* The forward direction includes the vertices. Conversely, for every
competitor `sigma`, the difference

```text
C_d(pi;w)-C_d(sigma;w)
```

is linear in `w`. If it is nonpositive at every generator, it is nonpositive
on their convex hull. The tight-path statement then follows from the v0.49
common-chain theorem applied to all finite scenarios at once. QED.

## Corollary: exact worst-case regret

Define

```text
Reg(pi;D,W)
  = max_(d,w in W) [
      C_d(pi;w) - min_sigma C_d(sigma;w)
    ].
```

Then

```text
Reg(pi;D,W)
  = max_(d,i,sigma)
      <v_i,b_d^pi-b_d^sigma>.
```

Hence a robust common ordering exists exactly when

```text
min_pi Reg(pi;D,W) = 0.
```

*Proof.* Regret is the maximum of finitely many linear functions of `w`, so
its maximum over a polytope is attained at a generator extreme point. QED.

The exact minimax-regret value grades failure when the robust common-order set
is empty. It does not turn a positive-regret order into a valid common
certificate.

## Theorem 3: minimal reference-sensitivity witness

Two outcomes, one decision objective, and two reference laws suffice for
there to be no ordering optimal throughout their convex hull. Each count is
minimal for reference-law sensitivity.

Take

```text
B(empty,x,y,X) = (0,0,0,1)
```

and reference vertices

```text
v_L = (3/4,1/4),
v_R = (1/4,3/4).
```

The ordering costs are

```text
               v_L    v_R
(x,y)          1/4    3/4
(y,x)          3/4    1/4.
```

Thus the endpoint optima are unique and opposite. There is no robust common
ordering, and the minimum worst-case regret is `1/2`.

This table is statistically realizable: one parameter of risk one with
outcome law `(1/2,1/2)` at `alpha=3/5` gives zero on both singletons and one
on the full set. One outcome has no ordering choice. With only one reference
law, a finite objective always has an optimum.

The witness does not claim that `alpha=3/5` is a practically desirable
confidence level; it certifies the smallest unrestricted finite grammar.

## Relation to v0.48-v0.49

A singleton family containing the v0.48 uniform reference law recovers all
`1,451,520` common optima. Version v0.50 asks the stronger question: how far
can that reference law move before the common set disappears?

The theorem converts that sensitivity into a polyhedral object and a finite
scenario certificate. It does not yet provide an efficient representation
of all ordering regions at large outcome width.

## Claim boundary

This is finite parametric and robust shortest-path mathematics. Linearity at
polytope vertices, scenario-wise regret, and tight-DAG intersection are
classical operations-research ideas. The ASMP-9 contribution is a transparent
specialization identifying reference-law choice as part of a
decision-relative confidence certificate. It does not establish novelty,
randomized-procedure optimality, continuous or strategic robustness, a
physical preference channel, or an ASMP-9 resolution.
