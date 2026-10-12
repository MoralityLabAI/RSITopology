# ASMP-3 rational polyhedral transcript frontier v0.9

## Status and scope

```text
result_status = exact rational polyhedral subtheorem
parent_result = ASMP-3-FINITE-TV-FRONTIER-v0.8
interface_mode = WV-FIX
input_representation = rational H-polytopes of terminal laws
changes_parent_problem = false
```

The v0.8 theorem characterizes the optimal finite terminal gap as the total
variation distance between truthful and false transcript-law hulls.  This
successor removes explicit law enumeration when those two convex law sets have
polynomial-size rational inequality descriptions.

It does not prove that the law sets induced by every interactive ASMP-3 game
have such descriptions.

## 1. Rational law polytopes

Let `Omega` have `m` terminal observations.  Suppose the complete robust
truthful and false law sets are nonempty rational polytopes contained in the
probability simplex:

```text
P = {p in R^m : A_P p <= b_P, E_P p = e_P},
Q = {q in R^m : A_Q q <= b_Q, E_Q q = e_Q}.
```

Nonnegativity and normalization are included among these constraints.  The
sets may already incorporate convex mixtures of:

- semantic worlds;
- legal adversarial strategies;
- history-conditional noise processes; and
- registered randomized choices.

No vertex list is required.

## 2. Distance linear program

### Theorem 1 (polyhedral terminal frontier)

The optimal uniform randomized terminal-verifier gap is the optimum of the
rational linear program

```text
minimize    (1/2) sum_w t_w

subject to  A_P p <= b_P,   E_P p = e_P,
            A_Q q <= b_Q,   E_Q q = e_Q,
            p_w - q_w <= t_w       for every w,
            q_w - p_w <= t_w       for every w,
            t_w >= 0               for every w.
```

It equals `distance_TV(P,Q)`.  Therefore, with rational input of polynomial
bit length and polynomially many rows, the terminal gap is computable by a
polynomial-size rational LP.

### Proof

For fixed feasible `p,q`, the least feasible `t_w` is `|p_w-q_w|`, so the
objective is `TV(p,q)`.  Minimization over the remaining constraints gives
`distance_TV(P,Q)`.

The polytopes are already convex.  The v0.8 finite minimax theorem—equivalently
its compact-polytope extension—identifies this distance with

```text
max_(0<=a<=1) [min_(p in P)<p,a> - max_(q in Q)<q,a>].
```

This is exactly the optimal uniform terminal-verifier gap.  QED.

The compact extension uses the same bilinear minimax proof as v0.8; finite
vertex sets are not needed because rational polytopes are compact convex sets.

## 3. Constructive verifier LP

The separating verifier can be obtained without converting the H-polytopes to
vertices.  Introduce:

```text
a in [0,1]^m,
L, U in R,
y_P >= 0, z_P free,
y_Q >= 0, z_Q free.
```

Maximize `L-U` subject to

```text
A_P^T y_P + E_P^T z_P = -a,
b_P^T y_P + e_P^T z_P <= -L,

A_Q^T y_Q + E_Q^T z_Q =  a,
b_Q^T y_Q + e_Q^T z_Q <=  U.
```

The first pair is a Farkas/LP-dual certificate that

```text
min_(p in P) <p,a> >= L;
```

the second certifies

```text
max_(q in Q) <q,a> <= U.
```

Thus `a` is an executable terminal acceptance rule with gap at least `L-U`.
Strong LP duality and Theorem 1 imply that the optimum is the same as the
distance LP.

## 4. Short exact certificates

An exact result can be checked using only rational linear algebra:

1. provide a feasible verifier/Farkas tuple with lower gap `gamma`;
2. provide `p* in P` and `q* in Q` with `TV(p*,q*)=gamma`.

The first proves the optimal gap is at least `gamma`; the second proves it is
at most `gamma`.  No floating-point LP output is trusted by the release.

The v0.9 artifact certifies three H-polytope fixtures.

### Interval noise bands

On a two-outcome alphabet,

```text
P: p(0) in [4/5, 9/10],
Q: q(0) in [1/10, 1/5].
```

Accept on outcome zero.  The Farkas bounds are `L=4/5`, `U=1/5`; the closest
laws have zero-probabilities `4/5` and `1/5`.  The exact gap is `3/5` despite
each class containing a continuum of legal laws.

### Polyhedral hull collision

Let `P` be the full binary probability simplex and `Q` the singleton uniform
law.  Since `Q subset P`, the exact gap is zero.  This is the H-representation
version of the v0.8 convex-hull warning.

### Joint-event robust bands

On observations `00,01,10,11`, let

```text
P: probability[observed parity is even] >= 4/5,
Q: probability[observed parity is even] <= 1/5.
```

The even-event verifier has exact gap `3/5`.  Both polytopes contain respective
laws—uniform on `{00,11}` and uniform on `{01,10}`—whose two one-coordinate
marginals are identical.  The separating constraint is genuinely joint.

## 5. What “polynomial-size” does and does not mean

The LP is polynomial-size in the supplied H-representations.  This is an
algorithmic theorem conditional on representation, not a claim that arbitrary
interaction trees compile to such polytopes without blowup.

In particular:

- an exponentially large transcript alphabet still produces a large LP;
- hidden-state or imperfect-recall strategy sets may require extended
  formulations or separation oracles;
- correlated adaptive noise may fail to have a compact polyhedral registry;
- computing the polytopes from source code can itself be intractable; and
- protocol construction and honest-prover computation are upstream of this
  terminal decision problem.

## 6. Next bridge: realization-plan polytopes

For a finite perfect-recall extensive-form interface, behavior strategies have
sequence-form realization-plan descriptions.  The next target is to identify
conditions under which the induced truthful and false terminal-law sets are
linear images of polynomial-size realization/noise polytopes.  Under those
conditions, the present LP applies through an extended formulation without
enumerating pure strategies.

That bridge requires a frozen interaction tree, explicit observation maps, and
a convex registered noise process.  It cannot be asserted for the ambiguous
v0.1 interface in the abstract.

## 7. Claim and novelty boundary

Linear programming, Farkas certificates, total variation, and rational
polytope separation are standard.  The contribution here is the explicit
ASMP-3 typing, the paired verifier/closest-law certificate format, robust joint
law fixtures, and a precise representation boundary for the efficient finite
lane.  This package is not a resolution of `WV-ADM` or of ASMP-3 v0.1.
