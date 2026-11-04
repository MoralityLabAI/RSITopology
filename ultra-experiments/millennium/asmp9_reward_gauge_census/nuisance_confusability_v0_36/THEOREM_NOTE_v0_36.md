# Nuisance confusability is not always a reward-gauge quotient

## Setup

Let `Theta` be a finite target set, `H` an unknown nuisance set, `A` a
registered set of queries, and

```text
f_q : Theta x H -> Y_q
```

a deterministic observation map. A stochastic population law can itself be
treated as one element of `Y_q`; the finite theorem does not require
single-sample observations.

When one nuisance value is shared across all queries, define

```text
S_A(theta) = {(f_q(theta,h))_(q in A) : h in H}.
```

Two parameters are confusable when their signature sets intersect.

## Theorem 1: exact decision criterion

For a declared decision `d : Theta -> D`, the following are equivalent:

1. there is a decoder `delta` satisfying
   `delta((f_q(theta,h))_q)=d(theta)` for every `theta,h`;
2. whenever `d(theta) != d(theta')`,
   `S_A(theta) intersect S_A(theta')` is empty.

### Proof

If an observation lies in both sets but the decisions differ, any decoder
must return two different values on the same input, which is impossible.
Conversely, if no cross-decision intersection exists, assign each realized
observation the unique decision shared by every parameter that can emit it.
Extend the decoder arbitrarily off the realized support. QED.

This is the decision-relative analogue of one-shot zero-error decoding. It
also gives the exact access test: every decision-changing confusability edge
must be removed.

## Theorem 2: the orbit obstruction

Confusability is always reflexive and symmetric, but it need not be
transitive. Orbit relations of group actions are equivalence relations.
Therefore a nontransitive nuisance-confusability relation cannot be the orbit
relation of any reward-symmetry group.

The smallest witness uses three targets, two nuisance values, and two
observation symbols. Let

```text
Theta = {0,1,2}
H = {1,2}
f(theta,h) = 1{theta >= h}.
```

Then

```text
S(0) = {0}
S(1) = {0,1}
S(2) = {1}.
```

Thus `0~1` and `1~2`, while `0` is not confusable with `2`. With at most two
targets every reflexive symmetric relation is transitive; with one nuisance
every signature is a singleton; with one observation symbol the relation is
complete. The witness is cardinality-minimal in all three coordinates.

The point is not that gauge language is wrong. It is exact when observational
fibers are orbits. The point is that adversarial or misspecified nuisance
classes can create overlap relations that are not fibers of any quotient.

## Theorem 3: stable nuisance can be an information resource

Add a mirrored query

```text
q0(theta,h) = 1{theta >= h}
q1(theta,h) = 1{theta >= 3-h}.
```

Each query alone has the same path confusability. If `h` is shared, the joint
signatures are

```text
S(0) = {(0,0)}
S(1) = {(1,0),(0,1)}
S(2) = {(1,1)},
```

which are pairwise disjoint. Two individually insufficient interventions
therefore identify the target jointly.

If the nuisance resets independently between queries, the signature becomes
the Cartesian product of the marginal signatures. The middle target can then
emit all four bit pairs and remains confusable with both endpoints.

More generally,

```text
S_A_shared(theta) subseteq S_A_reset(theta),
```

so every shared-nuisance confusability edge is also present in the reset
model. Nuisance stability across interventions is not merely an assumption to
survive; it can be the calibration resource that makes identification
possible.

## Consequence for ASMP-9

The first frozen obligation asks for a maximal invariance group for each data
source. This finite theorem shows the necessary refinement:

1. compute the observation signature sets under the declared nuisance class;
2. compute their confusability graph for the declared query family;
3. require the graph to respect the downstream decision partition;
4. use a gauge quotient only when the confusability relation is actually an
   equivalence induced by a scientifically meaningful transformation action.

The broader problem remains open for stochastic finite-sample laws, adaptive
queries, continuous target classes, and misspecification neighborhoods.
