# ASMP-9 decision-licensed linear quotient v0.75

Status: **unregistered synthesis of classical finite linear results**.

## Purpose

Version v0.74 showed that a gauge cannot be inferred merely by taking the
largest abstract symmetry group of an observation map. This version derives a
licensed additive gauge from one explicit downstream decision target and then
composes it with the v0.69 physical-access quotient.

## Declared decision target

Let a registered finite policy family have feature-occupancy rows

```text
mu_0, ..., mu_(k-1) in R^p.
```

The target retained by this theorem is the complete vector of **cardinal policy
value differences**. With policy zero as a reference, define

```text
D = rows(mu_i - mu_0),  i=1,...,k-1.
```

For reward `r`, the target is `D r`.

## Theorem 1: maximal additive decision gauge

The unique maximal linear subspace of additive reward changes preserving every
registered policy-value difference is

```text
G_dec = ker(D).
```

Indeed, an additive change `g` preserves all differences iff

```text
(mu_i-mu_j)^T g = 0
```

for all policy pairs. The reference differences span all pairwise differences,
so this is equivalent to `Dg=0`.

Thus, within this declared all-margin target, the gauge is derived from the
decision family rather than postulated.

## Theorem 2: joint physical-access criterion

Let:

- `A : R^p -> Y` be a registered linear measurement channel; and
- `N <= Y` be an additive physical nuisance subspace.

Representative-independent analysis must quotient the output by

```text
J = N + A(G_dec).
```

The observation identifies every registered policy-value difference exactly
iff the induced map

```text
R^p/G_dec -> Y/J
```

is injective. Equivalently:

```text
A^-1(J) = G_dec
```

or, in executable coordinates,

```text
rank(P_(J-perp) A U) = rank(D),
```

where the columns of `U` span the row space of `D`.

If the equality fails, the joint kernel contains a constructive witness `h`
such that:

```text
D h != 0
```

but `h` has no representative-independent measurement effect. The two rewards
therefore disagree on at least one registered policy margin while remaining
observationally indistinguishable.

This is the v0.69 theorem with its gauge supplied by the v0.29 decision object.

## Theorem 3: finite-class resolution cell

For the declared class

```text
finite policy occupancies
+ all cardinal policy margins
+ additive linear reward changes
+ linear measurements
+ additive output nuisance,
```

the following are now explicit and necessary-and-sufficient:

1. the licensed gauge: `ker(D)`;
2. the maximal identifiable reward object:
   `R^p / A^-1(N+A(ker D))`;
3. the exact access condition: equality of that kernel with `ker(D)`;
4. a non-gauge indistinguishability witness when access fails; and
5. the quotient dimension `rank(D)`.

This resolves the algebraic identifiability question **inside this declared
finite class**. It is not a resolution of ASMP-9's broader behavioral,
misspecification, sample-complexity, or replacement-object obligations.

## Exact controls

The verifier checks:

1. two one-hot policy occupancies derive common-mode gauge `span(1,1)`;
2. their contrast measurement identifies the one-dimensional decision
   quotient;
3. full reward measurement modulo common output nuisance remains exact;
4. a common-mode-only measurement is rejected and emits a non-gauge witness;
5. three affinely spanning policies derive a zero additive gauge; and
6. duplicate registered policies do not change the quotient.

## Important scope fork

The all-margin target is stronger than policy identity. If only the argmax is
retained, positive reward scaling also preserves the decision, but scaling is
not an additive subspace direction. Reward-dependent policy cones can create
still coarser equivalences.

Therefore `G_dec=ker(D)` must not be advertised as the maximal invariance for
every possible downstream use. It is the maximal **additive** gauge for the
registered vector of cardinal policy margins.

## Claim boundary

The policy family, occupancy features, linear response channel, nuisance
subspace, and cardinal-margin target are assumed. The theorem does not show
that the family contains safe policies, that occupancy features exhaust
consequences, that cardinal regret is morally adequate, or that humans/models
obey the channel. ASMP-9 remains unresolved.
