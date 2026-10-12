# What transition interventions can and cannot calibrate

## Result

Version v0.28 connects the earlier finite-MDP access result to the strong
offset access used in v0.26-v0.27.

### 1. Environment design changes directions, not units

A reward-independent trajectory or environment intervention produces a known
occupancy-difference row `x` and a homogeneous comparison argument:

```text
x^T r.
```

If the unknown response-link class is closed under positive rescaling, then

```text
r' = alpha r,
F'(t) = F(t/alpha)
```

preserves every comparison probability for every `alpha>0`. The obstruction
survives deterministic adaptive querying: equal past laws select the same next
row, whose conditional response law is again equal.

Transition interventions can still remove non-scale reward ambiguity by
enriching the span of the occupancy rows. They cannot create a cardinal reward
unit from a homogeneous interface alone.

### 2. An unknown-valued side feature does not fix scale

If a query adds `c` units of a feature with unknown reward coefficient `nu`,
the argument becomes:

```text
x^T r + c nu.
```

Scaling both `r` and `nu` preserves every law after rescaling the link. A
quantity is not a numeraire merely because it is called money, tokens, or
reward points.

### 3. A known numeraire is qualitatively different

If `c` is externally calibrated in the same declared units as the target,

```text
P(Y=1)=F(x^T r+c),
```

then the response crosses `1/2` exactly at `c=-x^T r`. Full-range offset
access therefore localizes the occupancy functional without knowing the
shape of the strictly increasing midpoint-zero link.

This is the scalar v0.26 threshold operation applied to a trajectory
functional.

### 4. The complete quotient criterion is linear

Let `X` stack all localized occupancy rows and let `G` be a declared linear
reward-gauge subspace. Provided every row annihilates the gauge:

```text
reward is identified modulo exactly G
  iff ker(X)=G
  iff rank(X)=p-dim(G).
```

Thus environment design controls which reward directions remain invisible.
At least `p-dim(G)` independent scalar functionals are necessary.

With an orthonormal quotient basis `U`, localization error obeys:

```text
||theta_hat-theta||_2
  <= ||e||_2 / sigma_min(XU).
```

Rank is the exact-identification threshold; the smallest quotient singular
value is the stability threshold.

## Why the finite-MDP bridge is genuine but limited

The registered implementation constructs one explicit deterministic finite
feature MDP for every fresh integer matrix. Each row is represented by a
query initial state with two actions entering disjoint feature-emission paths
at one common horizon. Positive-minus-negative feature occupancy equals the
requested row exactly.

This proves existence inside the declared finite-MDP access class. It does not
show that a natural environment can realize an arbitrary row without changing
the semantics of the reward-learning problem.

## Registered verification

The registered CPU run checked:

- exact scale coupling on two fresh population-law cells;
- 768 exact adaptive transcript probabilities;
- a matched unknown-numeraire control;
- two known-numeraire scale breaks;
- threshold localization with maximum error `1819/1720320`, below `5/2048`;
- four explicit MDP constructions with 19 query initial states and 144
  transitions;
- identifiable constant- and affine-gauge designs;
- a disconnected design with an exact non-gauge kernel witness; and
- a full-rank ill-conditioned design with `2896.309` times the error
  amplification of its control.

All ten gates and all eighteen import-independent verification checks passed.

## Access ledger

```text
environment design   -> row span and reward kernel
known numeraire      -> cardinal reward scale
response margin      -> finite-sample threshold cost
spectral floor       -> robust quotient recovery
```

## Prior-art and novelty boundary

Reward shaping, IRL identifiability, environment design, unknown-link
single-index models, linear inverse problems, and bisection are established
literatures. No novelty is claimed for those ingredients.

The contribution is a scoped ASMP-9 access ledger that states which ambiguity
each resource removes and supplies an explicit finite-MDP realization of the
registered linear queries.

## Claim boundary

The result does not establish that a practical consequence has stable known
cardinal utility, that real interventions preserve target semantics, that a
given environment exposes the required row span, that real demonstrators obey
the link model, or that ASMP-9 is resolved.
