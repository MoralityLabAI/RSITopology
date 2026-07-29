# ASMP-9 v0.49 common-ordering theorem draft

## 1. Setup

Let `X` be a finite outcome set with positive reference weights `w_x`. For a
finite decision risk `d`, experiment `P_theta`, and confidence error `alpha`,
write

```text
B_d(S) = max {d(theta) : P_theta(S) > alpha}
```

for every subset `S` of `X`. An ordering
`pi=(x_1,...,x_m)` induces prefixes `S_j={x_1,...,x_j}` and cost

```text
C_d(pi) = sum_j w_(x_j) B_d(S_j).
```

The scientific question is whether two decision risks admit one ordering
minimizing both costs.

## 2. Tight-predecessor theorem

Define the exact subset value

```text
V_d(empty) = 0,

V_d(S) = min_(x in S) [
  V_d(S \ {x}) + w_x B_d(S)
].
```

Call the edge `S\{x} -> S` tight for `d` when equality holds.

**Theorem 1 (common-chain characterization).** Two decision risks `d_1,d_2`
have a common optimal ordering if and only if the intersection of their
tight-predecessor DAGs contains a directed path from `empty` to `X`.

The number of such paths equals the number of common optimal orderings.

*Proof.* An ordering is optimal for one objective exactly when every prefix
transition realizes equality in the Bellman recurrence. If a prefix
transition is not tight, replacing its prefix by an optimal ordering of the
same subset strictly reduces total cost while leaving the suffix unchanged.
Thus an ordering is optimal for both objectives exactly when all of its
prefix edges lie in both tight DAGs. Such orderings are precisely the
`empty`-to-`X` paths in their intersection. Counting paths counts common
orderings. QED.

**Corollary 1 (finite obstruction).** Let `R` be the subsets reachable from
`empty` in the tight-edge intersection. If `X` is not in `R`, every edge from
`R` to its complement is non-tight for at least one objective. The reachable
set together with the labelled boundary edges is a finite certificate that
the optimizer sets are disjoint.

Because the ordering universe is finite, disjoint optimizer sets imply both
registered cross-regrets are strictly positive.

This theorem is an exact instance characterization. It is not yet a
structural classification that avoids solving the two subset programs.

## 3. Ordering gauge

The v0.48 confirmation suggests a stronger positive question: when must two
apparently different set-bound objectives have identical optimizers?

Let `B_1,B_2` be two subset-bound tables, let `a>0`, and define

```text
h(S) = B_2(S) - a B_1(S).
```

Associate to every subset edge `S\{x} -> S` the one-form

```text
omega_h(S\{x},S) = w_x h(S).
```

For `A` not containing distinct `x,y`, its square curl is

```text
curl_h(A;x,y)
  = w_x h(A+x) + w_y h(A+x+y)
    - w_y h(A+y) - w_x h(A+x+y).
```

**Theorem 2 (ordering-gauge equivalence).** The following are equivalent:

1. `curl_h(A;x,y)=0` on every square of the Boolean lattice;
2. there is a subset potential `Phi` such that

   ```text
   w_x h(S) = Phi(S) - Phi(S\{x})
   ```

   for every `x in S`; and
3. the path sum `sum_j w_(x_j) h(S_j)` is independent of the ordering.

Under these conditions,

```text
C_2(pi)
  = a C_1(pi) + Phi(X) - Phi(empty)
```

for every ordering `pi`. Therefore the two objectives have exactly the same
optimizer set.

*Proof.* Path independence implies zero curl by comparing the two routes
around each square. Zero curl makes the integral from `empty` to `S`
independent of the chosen ordering because adjacent transpositions generate
all permutations. This integral defines `Phi`; the potential identity then
telescopes along every maximal chain. Substituting
`B_2=aB_1+h` gives the cost identity. Since `a>0`, argmin sets agree. QED.

Positive rescaling `B_2=aB_1` and positive affine shifts
`B_2=aB_1+c` are immediate special cases when the shift is defined on every
nonempty subset. More general exact one-form perturbations are also invisible
to ordering choice.

The zero-curl condition is sufficient for common optimality and necessary for
full affine equality of ordering costs. It is not necessary merely for the
existence of one shared optimum.

## 4. Relation to the v0.48 null

The v0.48 confirmation has 1,451,520 paths in the tight-DAG intersection.
The burned development fixture has none. An exact square audit also finds no
positive scale that puts the confirmation pair in the zero-curl ordering
gauge: its square equations demand 17 distinct scale ratios. Thus
ordering-gauge equivalence is genuinely sufficient rather than necessary for
a shared optimum on the measured fixture. The tight-chain theorem
distinguishes these outcomes without treating different lexicographic
representatives as evidence of incompatibility.

The next prospective step should test a structural condition stronger than
the instance-wise path algorithm. Candidate restricted classes include:

- zero-curl ordering-gauge equivalence;
- common nested level sets with a declared magnitude condition; and
- comonotone tight-predecessor margins.

Any successor must include both v0.48 fixtures as deterministic controls.

## Claim boundary

The tight-DAG result is Bellman optimality on a finite Boolean lattice. The
zero-curl result is the elementary exact-one-form/path-independence theorem.
Their contribution here is to replace an unsupported universal ordering claim
with a precise ASMP-9 access object and finite certificates. No novelty,
continuous-channel, physical preference, or ASMP-9 resolution claim is made.
