# ASMP-9 finite access Set Cover reduction v0.78

Status: **unregistered classical NP-hardness specialization**.

## Question

Versions v0.74-v0.77 characterize when a declared query family recovers a
finite target. Can the minimum exact query family be computed efficiently for
an arbitrary finite deterministic registry?

In general, no: the problem contains Set Cover exactly.

## Construction

Take a Set Cover instance:

```text
universe U = {u_1,...,u_m};
candidate sets S_1,...,S_k.
```

Build a target registry with two parameters `a_u,b_u` for every universe
element and two special parameters `c,d`. Give every parameter a distinct
target label.

Create one **anchor query** `q_0`:

```text
q_0(a_u) = q_0(b_u) = the label u;
q_0(c) and q_0(d) are distinct fresh labels.
```

For every candidate set `S_j`, create a binary query:

```text
q_j(a_u)=0;
q_j(b_u)=1 if u in S_j, otherwise 0;
q_j(c)=q_j(d)=0.
```

## Theorem: optimum shifts by exactly one

The minimum exact target-separating query-family size is:

```text
1 + minimum Set Cover size,
```

and no exact family exists iff the Set Cover instance is infeasible.

### Proof

The parameters `c,d` agree on every set query and differ only on `q_0`, so
every exact query family must contain the anchor.

Once `q_0` is included:

- parameters belonging to different element-pairs already have distinct
  anchor labels;
- `c,d` and every element-pair are separated by the anchor; and
- within pair `a_u,b_u`, the anchor agrees and a selected set query separates
  them exactly when its set contains `u`.

Therefore the selected non-anchor queries separate every within-element pair
iff their corresponding sets cover `U`. Removing the mandatory anchor from
any exact family gives a set cover, and adjoining it to any set cover gives an
exact family.

The construction has `2|U|+2` parameters and `k+1` queries and is polynomial.
Thus arbitrary finite deterministic minimum-access design is NP-hard by the
classical NP-hardness of Set Cover.

## Exact controls

The frozen fixture uses:

```text
U={0,1,2,3}
S_0={0,1}
S_1={2,3}
S_2={0,2}
S_3={1,3}.
```

Its minimum cover is `(S_0,S_1)`, of size two. The constructed access optimum
is `(q_0,q_1,q_2)`, of size three. All non-anchor queries together still fail
because `c,d` remain indistinguishable.

The verifier additionally checks 48 seeded five-element, six-set registries.
Every feasible instance has access optimum exactly one larger than its cover
optimum; infeasible instances remain infeasible.

## ASMP-9 consequence

There is no general polynomial exact minimum-query algorithm for arbitrary
finite response/query registries unless `P=NP`. A sharp ASMP-9 access theorem
therefore needs one of:

1. a structured query family with exploitable algebra or geometry;
2. approximation guarantees;
3. parameterized complexity in a declared structural width; or
4. a certificate for a fixed query design rather than global optimization.

This result explains why query-count thresholds derived in structured graph,
linear, or stochastic cells do not extend automatically to arbitrary access
grammars.

## Claim boundary

The reduction uses deterministic lookup queries with an unrestricted finite
output alphabet for the anchor. It establishes only worst-case finite-registry
NP-hardness. It does not prove hardness for a natural behavioral response
model, binary-only query grammar, adaptive approximation, or physical
interventions. It does not resolve ASMP-9.
