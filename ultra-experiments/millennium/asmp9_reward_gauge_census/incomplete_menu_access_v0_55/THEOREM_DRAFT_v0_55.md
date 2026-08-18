# Incomplete-menu object-identification theorem

## Setup

Let:

```text
X = {a,b,c}
M = {ab, ac, bc, abc}.
```

Let `D` be a nonempty observed subfamily of `M`, and let `p_D` assign a
strictly positive normalized choice law to every menu in `D`.

A complete extension is a strictly positive stochastic choice kernel on all
of `M` that agrees with `p_D`. Its full-kernel tier is one of:

```text
L = scalar_luce
R = random_utility_non_luce
N = no_random_utility_representation.
```

Write `T_D(p_D)` for the set of tiers attained by complete positive
extensions.

## Classical existential tests

### Luce compatibility

For every observed co-occurring pair `(x,y)`, label the comparison graph by

```text
r_xy = p(x | S) / p(y | S).
```

A Luce completion exists iff:

1. repeated observations of `(x,y)` have the same ratio; and
2. the product of oriented ratios around every comparison-graph cycle is one.

When this holds, positive weights exist. They are unique up to one
multiplicative constant per connected component. This is the multiplicative
graph-potential form of Luce/Bradley-Terry coherence.

### Random-utility compatibility

For each strict ranking `rho` of `X`, let `A_D(rho)` be its deterministic
choice signature on the observed menus. A random-utility completion exists
iff:

```text
p_D is in conv{A_D(rho): rho a strict ranking of X}.
```

Equivalently, the exact system

```text
A_D lambda = p_D,
lambda >= 0,
sum lambda = 1
```

is feasible. This is the classical ARSP/convex-hull characterization.

## Tier-identification theorem

For a proper domain `D != M`:

### Case 1: no RUM completion

If the ARSP system is infeasible, then

```text
T_D(p_D) = {N}.
```

### Case 2: RUM-compatible but not Luce-compatible

If a RUM completion exists but no Luce completion exists, then

```text
T_D(p_D) = {R,N}.
```

### Case 3: Luce-compatible

If a Luce completion exists, then

```text
T_D(p_D) = {L,R,N}.
```

Thus a proper menu domain can refute RUM, but it cannot certify that the
unobserved full response kernel belongs to RUM. Full-domain tier
identification requires observing all four nontrivial menus in this declared
unrestricted-completion grammar.

## Proof sketch

### A non-RUM completion always exists when a menu is missing

If `abc` is missing, choose a pair containing `a` and complete the ternary law
with:

```text
p(a | abc) > p(a | pair).
```

If `abc` is observed but a pair `{x,y}` is missing, complete that pair with:

```text
p(x | {x,y}) < p(x | abc).
```

Either construction is strictly positive and violates random-utility
regularity, while leaving all observed menus unchanged.

### A non-Luce RUM completion exists from any partial Luce law

The six deterministic ranking signatures are affinely independent in the
five-dimensional complete normalized choice space. A positive
Plackett-Luce ranking law lies in the interior of this RUM simplex.

Any proper menu domain leaves at least one independent choice coordinate
unobserved. The fiber through the interior Plackett-Luce point therefore
contains a nontrivial segment of RUM completions. For the 15 nonempty domains:

- if `abc` is observed, its probabilities fix the Luce weights and a missing
  pair can vary;
- if `abc` is missing and at least two pairs are observed, the pair odds fix
  the weights and the ternary menu can vary; and
- if at most one pair is observed, the RUM fiber has dimension at least four
  while compatible Luce completions have dimension at most one.

Hence the fiber contains a RUM completion outside the Luce manifold.

## Full-domain control

When `D=M`, the complete kernel is observed. Version v0.54's classical
criteria return the singleton tier set `{L}`, `{R}`, or `{N}`.

## Claim boundary

The existential tests are classical. The completion-ambiguity statement is an
elementary finite access result for one unrestricted completion grammar. It
does not establish approximate, finite-sample, continuous, endogenous,
strategic, dynamic, welfare-relevant, or physical preference identification.

