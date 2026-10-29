# Joint reward-gauge and measurement-nuisance quotient

Status: **proved finite linear theorem; development-only and unregistered**.

## 1. Why this theorem is needed

The ASMP-9 chain currently contains two exact but separate objects:

1. reward gauges, such as potential-based shaping directions; and
2. physical measurement nuisances, such as blockwise common score offsets.

A physical instrument identifies a reward quotient only when these objects
compose correctly. It is not enough that the instrument is invariant to its
measurement nuisance, and it is not enough that a reward transformation is
decision-preserving. The measurement channel can erase an additional
non-gauge direction or expose the choice of reward representative.

The theorem below gives the exact finite-dimensional linear criterion.

## 2. Registered mathematical object

Let:

- `R` be a finite-dimensional real reward-parameter space;
- `G <= R` be the linear subspace of licensed reward-gauge directions;
- `Y` be a finite-dimensional raw measurement space;
- `N <= Y` be the additive physical measurement-nuisance subspace; and
- `A : R -> Y` be a linear measurement channel induced by the declared
  query/intervention design.

The scientific target is the reward orbit `[r]_G`, not the selected
representative `r`.

A gauge change may itself be visible in raw measurement coordinates. The
smallest output subspace that must be discarded by a
representative-insensitive analysis is therefore

```text
J = N + A(G).
```

Write `pi_J : Y -> Y/J` for the quotient map and define

```text
B = pi_J o A.
```

Because `A(G) <= J`, `B` descends to a unique linear map

```text
B_bar : R/G -> Y/J.
```

## 3. The joint-quotient theorem

### Theorem 1: maximal identifiable quotient

Define

```text
K = A^(-1)(J) = ker(B).
```

Then:

1. `G <= K`;
2. two rewards have the same representative-insensitive measurement exactly
   when their difference lies in `K`; and
3. the maximal linearly identifiable reward object is `R/K`.

Equivalently, the set of identifiable linear reward estimands is the
annihilator `K^perp`.

#### Proof

Every `g in G` satisfies `A g in A(G) <= J`, so `G <= K`.
Furthermore,

```text
pi_J A r = pi_J A r'
iff A(r-r') in J
iff r-r' in K.
```

Thus the observational fibers are exactly the affine cosets of `K`, and any
function identified from the observation must be constant on those cosets.
The quotient map `R -> R/K` is therefore maximal. A linear functional `c`
is constant on every `K`-coset exactly when `c(k)=0` for every `k in K`.

### Theorem 2: exact reward-quotient identification

The following are equivalent:

1. the physical channel identifies `R/G`;
2. `B_bar` is injective;
3. `K = G`;
4. `rank(B_bar) = dim(R) - dim(G)`; and
5. every gauge-invariant linear estimand is identifiable:
   `K^perp = G^perp`.

If these conditions fail, every `h in K \ G` is an exact non-gauge
indistinguishability witness:

```text
[r]_G != [r+h]_G
```

but the two targets have identical admitted measurements.

#### Proof

The kernel of the induced map `B_bar` is `K/G`. Hence `B_bar` is injective
exactly when `K/G` is zero, which is exactly `K=G`. Rank-nullity gives the
rank statement. In finite dimensions, `G <= K` and
`K^perp = G^perp` are equivalent to `K=G`.

### Theorem 3: gauge leakage

The raw nuisance-quotiented channel `pi_N A` is already
representative-independent exactly when

```text
A(G) <= N.
```

The number of linearly independent gauge directions visible beyond the
physical nuisance is

```text
ell = dim(N + A(G)) - dim(N).
```

If `ell > 0`, raw measurements reveal which licensed representative was
selected. Such information may be retained only by enlarging the target to
include the representative-selection law. It may not be used while claiming
to identify the reward orbit alone. Quotienting by `J` removes it.

#### Proof

`pi_N A(r+g) = pi_N A r` for all `r,g` exactly when `A g in N` for every
`g in G`. The dimension formula is the rank of the image of `A(G)` in `Y/N`.

## 4. Sharp noiseless access bound

Let

```text
d = dim(R/G),
m = dim(Y/J).
```

Then

```text
rank(B_bar) <= min(d,m).
```

Consequently `m >= d` is necessary for exact quotient identification. This
dimension bound is sharp: an injective linear map from a `d`-dimensional
quotient into `R^d` attains equality.

For a fixed dictionary of scalar query/intervention contrasts, a selected
family is sufficient exactly when its induced invariant rows span
`G^perp`. Equivalently, its joint kernel is exactly `G`. Thus minimum access
is the smallest allowed row family of rank `d` after the joint output
quotient. A scalar query can add at most one such rank.

This is a noiseless linear access result, not a stochastic sample-complexity
theorem.

## 5. Sharp deterministic stability

Choose Euclidean structures and use orthonormal complements `G^perp` and
`J^perp`. Let

```text
B_eff = P_(J^perp) A |_(G^perp).
```

When Theorem 2 holds, let `sigma_min > 0` be the smallest singular value of
`B_eff`. For admitted observation

```text
z = B_eff x + e,   ||e||_2 <= epsilon,
```

gauge-fixed least-squares recovery satisfies

```text
||x_hat - x||_2 <= epsilon / sigma_min.
```

The inverse Lipschitz constant `1/sigma_min` is sharp. Take unit singular
vectors `v,u` with `B_eff v = sigma_min u`; the two targets

```text
x_+ = +(epsilon/sigma_min) v,
x_- = -(epsilon/sigma_min) v
```

can both produce observation zero under disturbances `-epsilon u` and
`+epsilon u`. No estimator can have worst-case error below
`epsilon/sigma_min` on this two-point set.

If `sigma_min=0`, exact identification already fails and Theorem 2 supplies
a non-gauge kernel witness. Disturbance caused by an unmodelled nuisance
component enters through its projection onto `J^perp`; the same bound applies
to that residual, but the theorem does not bound its physical size.

## 6. Exact fixtures

The development verifier includes four rational fixtures:

1. **full common mode:** three reward scores modulo their common constant;
   two contrasts identify the two-dimensional reward quotient;
2. **partial common mode:** two observed scores supply only one contrast, so a
   non-gauge ambiguity remains;
3. **gauge leaking but complete:** raw measurements reveal a gauge coordinate,
   but the forced output quotient removes it and retains all substantive
   coordinates; and
4. **non-gauge confounded:** the substantive direction
   `(-1,-1,1,0)` lies in the joint kernel and is emitted as an exact witness.

A seeded registry of 128 small integer channels independently checks the
kernel-rank equivalence.

## 7. ASMP-9 consequence

This theorem closes one missing compositional step in the finite linear lane:

```text
licensed reward gauge
  + physical measurement nuisance
  + declared linear access
  -> exact maximal quotient, access criterion, witness, and condition number.
```

It prevents two invalid inferences:

- a nuisance-invariant instrument need not identify the intended reward
  quotient if `K` strictly contains `G`; and
- a channel that reveals the chosen gauge representative does not thereby
  learn more about the representative-independent reward target.

## 8. Claim boundary

This is a consolidation of quotient-space linear algebra, rank-nullity, and
linear inverse-problem conditioning. No novelty is claimed for those
mathematical ingredients.

The theorem does **not** establish:

- that a declared reward transformation is behaviorally or morally licensed;
- that a real response channel is linear;
- that the physical nuisance is exhausted by `N`;
- a minimax finite-sample rate;
- nonlinear, strategic, history-dependent, or non-scalar identification;
- value identification in a human or model; or
- resolution of ASMP-9.
