# Finite-MDP environment access as intersection of shaping subspaces

## Status

Development theorem draft for ASMP-9 v0.10. The entropy-regularized
identifiability and two-environment/two-discount positive results are already
in Cao, Cohen, and Szpruch (2021). The contribution attempted here is a
transparent access-complexity specialization, exact finite census, and matched
deterministic-policy obstruction. Novelty is not claimed.

## Fixed-environment equivalence

Let a finite discounted MDP have `S` states, `A` actions, known transition
kernel `P`, discount `0<gamma<1`, known entropy temperature `tau`, and
state-action reward `r in R^(SA)`.

For a full-support soft-optimal policy `pi`, every reward producing that policy
has the form

```text
r(s,a) = tau log pi(a|s)
         + V(s)
         - gamma sum_t P(t|s,a)V(t).
```

Write

```text
G_(P,gamma) V = V(s)-gamma E[V(s')|s,a].
```

Then one exact policy identifies the affine class

```text
r + im G_(P,gamma).
```

The shaping operator is injective for `0<gamma<1`: if `G V=0`, a
maximum-norm state would satisfy `||V||_infinity <= gamma||V||_infinity`, so
`V=0`. A single environment therefore leaves exactly `S` reward dimensions
ambiguous.

## Multiple environments

Suppose the same reward is observed through exact soft-optimal policies in
environments `e=1,...,K`. Two rewards induce the same complete policy family
if and only if their difference lies in

```text
I_K = intersection_e im G_e.
```

The residual reward ambiguity dimension is `dim I_K`; the identified
dimension is `SA-dim I_K`. A block linear system with one potential per
environment computes `dim I_K` exactly.

Global reward constants always lie in every `im G_e`. Thus one-dimensional
ambiguity is the strongest possible identification in this access model.

## Sharp two-environment theorem for a structured intervention family

Take the reference environment `P_0` in which every action self-loops. Its
shaping image consists exactly of reward perturbations constant across actions
within each state.

For a second kernel `P`, define its action-difference matrix

```text
A_P[(s,a),t] = P(t|s,a)-P(t|s,a_0).
```

Then

```text
dim(im G_0 intersect im G_P)
  = dim ker A_P
  = S-rank(A_P).
```

For deterministic `P`, construct the undirected successor-difference graph
`H_P`: each state/action contributes an edge between the successor under
reference action `a_0` and the successor under action `a`. The action
difference matrix is an incidence matrix, so:

```text
dim(im G_0 intersect im G_P) = c(H_P),
```

the number of connected components, including isolated successor states.

Consequently:

- one environment leaves ambiguity dimension `S`;
- two environments are necessary to reduce it below `S`; and
- the reference plus one second environment identify reward up to a global
  constant if and only if `H_P` is connected.

This is a sharp access threshold for the registered intervention grammar, not
a new general IRL theorem.

## Two-discount theorem for the cyclic kernel

Let action zero self-loop and action one move from `s` to `s+1 mod S`. For the
same transition kernel observed at two distinct discounts
`gamma_1 != gamma_2`, the common shaping intersection consists only of global
reward constants.

Indeed, equality on the self-loop action makes the two potentials
statewise proportional. Equality on the moving action then forces adjacent
potential values to agree. Connectivity of the cycle makes the potential
constant.

Thus two distinct discounts are also necessary and sufficient in this
structured family.

## Deterministic-policy obstruction

The positive theorem depends on full stochastic soft-policy probabilities.
For any finite family of environments, if a deterministic policy is strictly
optimal at reward `r`, continuity leaves an open neighborhood of rewards with
the same observed policy. Exact continuous reward identification is therefore
impossible from finitely many strict deterministic policies.

The registered witness uses the reference and cyclic environments:

```text
r(s,a_0)=1, r(s,a_1)=0.
```

Action zero is strictly optimal with gap one everywhere. Changing only
`r(0,a_1)` from zero to `1/2` preserves the same strict policy in both
environments. The difference is not a global constant, even though the common
soft-policy shaping ambiguity for those environments is only one-dimensional.

This matched pair separates information in full stochastic policy
probabilities from information in action identities.

## Direct one-step trajectory comparator

If a controlled one-step trajectory query reveals an exact return difference
between two state-action coordinates, a query graph on the `SA` coordinates
has ambiguity dimension equal to its number of connected components. A
connected graph uses at least `SA-1` comparisons and identifies reward up to a
global constant.

This is a direct-return comparator, not a claim about passive trajectory
demonstrations.

## Claim boundary

The theorem assumes exact infinite-data policies, known entropy temperature,
known finite transition kernels and discounts, state-action rewards, and
registered interventions. It does not cover finite-sample policy estimation,
unknown temperature, constrained or non-entropy-regularized policies,
continuous MDPs, passive demonstrations, or behavioral misspecification.
