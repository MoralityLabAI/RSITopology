# Robust contextual scalar gluing and query conditioning

## Theorem 1: orthogonal inconsistency decomposition

Let `Y` be a finite-dimensional Euclidean observation space and let:

```text
G subseteq L subseteq Y
```

be the shared-scalar and context-local-scalar subspaces. Write `P_G` and `P_L`
for their orthogonal projectors. Every observation has the unique orthogonal
decomposition:

```text
y = P_G y + (P_L-P_G)y + (I-P_L)y.
```

The terms lie in:

```text
G,
Q = L intersect G^perp,
L^perp,
```

respectively. Therefore:

```text
dist(y,G)^2
  = ||(P_L-P_G)y||_2^2 + ||(I-P_L)y||_2^2.
```

The first term is the cross-context gluing defect after the best local scalar
fit. The second is within-context non-scalarity.

### Proof

Because `G subseteq L`, the projectors satisfy:

```text
P_G P_L = P_L P_G = P_G.
```

Hence `P_L-P_G` is the orthogonal projector onto
`L intersect G^perp`, while `I-P_L` projects onto `L^perp`. The three projector
ranges are mutually orthogonal and their sum is the identity. Pythagoras gives
the squared-distance identity. Orthogonal projection uniquely minimizes
Euclidean distance to a closed finite-dimensional subspace. QED.

For the v0.11 context-labelled incidence operators:

```text
G = im(D_shared),
L = im(D_local).
```

Thus:

```text
dim(Q)
  = rank(D_local)-rank(D_shared),
```

which is exactly the v0.11 mixed-cycle obstruction dimension.

## Corollary 1: exact repair radius

For a declared error budget `epsilon`, a shared-scalar flow exists within the
budget if and only if:

```text
dist(y,G) <= epsilon.
```

This follows directly from the metric-projection characterization. The
distance is the exact minimum correction in the declared Euclidean norm, not
only a score correlated with compatibility.

## Theorem 2: count and conditioning of linear gluing queries

Let `d=dim(Q)` and let a query design be a linear map:

```text
A : Q -> R^k.
```

The gluing coordinate is identifiable exactly when `rank(A)=d`, so `k>=d` is
necessary.

If observed query outputs have additive error of Euclidean norm at most
`eta`, the Moore-Penrose reconstruction has worst-case error:

```text
eta / sigma_min(A).
```

No left inverse has a smaller worst-case operator norm.

### Proof

An injective linear map from a `d`-dimensional space needs rank `d`, hence at
least `d` rows. For full column rank, the Moore-Penrose inverse has spectral
norm `1/sigma_min(A)`. If `B A=I`, choose a right singular vector `v` for
`sigma_min`. Then:

```text
1 = ||v|| = ||BAv|| <= ||B|| sigma_min(A),
```

so every left inverse has norm at least `1/sigma_min(A)`. QED.

## Corollary 2: optimal square normalized queries

Take `k=d` and constrain every query row to norm at most one. Then:

```text
sigma_min(A) <= 1.
```

Equality holds exactly for an orthonormal query basis.

### Proof

The sum of squared singular values equals the squared Frobenius norm:

```text
sum_i sigma_i(A)^2 = ||A||_F^2 <= d.
```

The smallest squared singular value cannot exceed their mean, one. Equality
forces every singular value to equal one, so the square matrix is orthogonal.
The converse is immediate. QED.

## Theorem 3: minimum-support simple cycles can be condition-suboptimal

Consider four common items and two contexts:

```text
context 0: (0,3), (1,2)
context 1: (0,1), (0,2), (1,3), (2,3).
```

The shared incidence rank is three, the local incidence rank is five, and the
mixed obstruction dimension is two.

A minimum-total-support spanning pair of simple mixed cycles uses six edge
incidences. After normalizing each cycle by its full edge-noise norm, its
restricted Gram matrix on `Q` is exactly:

```text
diag(2/3, 2/3).
```

Its worst-case amplification is `sqrt(3/2)`.

Another spanning pair uses eight incidences and has exact restricted Gram
matrix:

```text
I_2.
```

It attains the arbitrary-linear-query optimum with amplification one.
Therefore minimum query count and minimum total cycle support do not imply
robust optimality.

The rational projector and Gram calculations are emitted by
`exact_certificate.py`.

## Claim boundary

These are finite Euclidean nested-subspace and singular-value statements.
The first two are standard linear algebra; novelty is not claimed. The
six-edge example is an exact finite counterexample in the registered
context-labelled query grammar, not a claim about human preferences or a
general cycle-basis optimization theorem.

The results do not choose the observation norm application-independently,
infer latent contexts, provide finite-sample stochastic coverage, establish
that a demonstrator has scalar preferences, or resolve ASMP-9.
