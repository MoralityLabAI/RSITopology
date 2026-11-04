# ASMP-9 v0.40 theorem draft: risk-polytopes characterize finite access

## Setup

Let `Theta`, every observation set, and every registered action set be finite.
For decision problem `d` with bounded loss matrix `L_d`, let

```text
R_d(E) subset R^Theta
```

be the set of target-wise risk vectors achieved by all randomized decision
rules after experiment `E`. It is the convex hull of the risk vectors of
deterministic rules.

Define its coordinate-wise upper closure:

```text
U_d(E) = R_d(E) + R_+^Theta.
```

For a finite registered decision type `D`, use the rule-by-rule deficiency
from v0.38.

## Theorem 1: directed risk-polytope characterization

For finite experiments `E,F`,

```text
delta_D(E,F)
  = inf {epsilon >= 0:
         R_d(F) subset U_d(E) + epsilon*1
         for every d in D}.
```

In particular:

```text
delta_D(E,F)=0
  iff R_d(F) subset U_d(E) for every d in D.
```

### Proof

For each reference rule, its risk vector `r` lies in `R_d(F)`. The definition
of relative deficiency asks for a source rule with risk vector `s in R_d(E)`
such that `s <= r+epsilon*1` coordinatewise. This is exactly membership of
`r` in `U_d(E)+epsilon*1`.

Randomized reference rules add no stronger condition. Their risk vectors are
convex combinations of deterministic-rule risk vectors. If each deterministic
vector has a source witness at tolerance `epsilon`, the corresponding convex
combination of source witnesses certifies the randomized vector at the same
tolerance. Thus it is enough to check the finitely many deterministic
reference rules, which is what the exact compiler does.

## Corollary 1: necessary and sufficient finite query access

For any finite registry of conditionally independent query channels and any
query subset `A`, form the product experiment `E_A`. Given full registered
access `E_Q`, subset `A` is sufficient at tolerance `epsilon` exactly when

```text
R_d(E_Q) subset U_d(E_A)+epsilon*1
```

for every registered decision problem. The inclusion-minimal sufficient
access families are therefore an exact antichain in the query-subset lattice.

This is a complete finite characterization, although exhaustive enumeration
is not generally efficient.

## Theorem 2: deterministic identification is Test Cover

Assume:

- each query is a deterministic binary test on `Theta`;
- full access separates every target; and
- the decision problem is zero-one target classification.

Then a query subset has zero relative deficiency against full access if and
only if its joint query signature is injective on `Theta`. Hence its
inclusion-minimal sufficient families are exactly the test covers of the
target set.

### Proof

If signatures are injective, the subset reveals the target and can implement
every full-access rule.

If targets `theta != theta'` share a signature, full access can use the rule
that selects action `theta` at `theta` and action `theta'` at `theta'`,
achieving zero risk on both. A source rule must use one action distribution
for their shared observation. Its two correct-action probabilities sum to at
most one, so at least one target has positive risk. Zero deficiency is
impossible.

Minimum-cardinality exact access selection in this special case is therefore
the classical NP-hard Minimum Test Cover problem.

Moreover, if the largest unresolved signature block has size `k`, then

```text
delta_D(E_A,E_full) = 1 - 1/k.
```

The lower bound assigns the correct target action separately within that
block under full access. The source must use one distribution over those `k`
actions, so one target receives probability at most `1/k`. Uniform
randomization within every source block gives the matching upper bound.

For a two-action group decision with false-positive cost `c_+` and
false-negative cost `c_-`, the corresponding deterministic-partition value is
zero when every block is label-pure and otherwise exactly

```text
c_+ c_- / (c_+ + c_-).
```

This is the minimax intersection of the two linear risks in any mixed block.

## Consequence for ASMP-9

The finite access object is not a scalar information score or a reward
quotient. It is an upper risk polytope indexed by the declared decision type.
Changing the loss type changes the containment test and can change the
minimal access antichain without changing the query channels.

## Claim boundary

The risk-set characterization is a direct finite unpacking of classical
Blackwell/Le Cam/Torgersen comparison. The Test Cover boundary is classical
combinatorial optimization. The ASMP-9 contribution is the exact compiler,
decision-type ledger, and explicit placement of finite reward/value access
inside those classical objects. This does not resolve continuous, adaptive,
unknown-link, strategic, or real-model ASMP-9.
