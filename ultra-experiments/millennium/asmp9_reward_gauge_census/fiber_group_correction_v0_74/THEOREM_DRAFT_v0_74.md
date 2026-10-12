# ASMP-9 fiber-group correction v0.74

Status: **unregistered classical finite-set development**.

## Why the canonical wording needs a correction

The ASMP-9 draft asks for a “maximal invariance group” and an observation map
whose equal-output fibers are exactly the licensed reward-gauge orbits. The
first phrase is mathematically well-defined but scientifically insufficient.

Let `X` be a finite parameter registry and let

```text
O : X -> Y
```

be the complete registered observation. Define

```text
Aut(O) = {g in Sym(X) : O(gx)=O(x) for every x}.
```

## Theorem 1: the maximal observation group is tautological

`Aut(O)` is the direct product of the symmetric groups on the nonempty fibers
of `O`:

```text
Aut(O) = product over y of Sym(O^-1(y)).
```

Its orbits are exactly the observation fibers. One inclusion is immediate
because every member preserves each fiber. Conversely, two points in one fiber
can be swapped while fixing every other point, and that transposition belongs
to `Aut(O)`.

Thus every finite observational-equivalence relation is the orbit relation of
a maximal group. This group may contain arbitrary permutations with no
interpretation as potential shaping, affine reward change, or any other
licensed decision symmetry. Computing it does not identify the physical gauge.

## Theorem 2: exact quotient identification is equality of partitions

Let `Gamma` be a **separately licensed** group of decision-invariant reward
transformations. A query family `Q` identifies `X/Gamma` exactly iff:

1. **gauge invariance:** every query is constant on every `Gamma` orbit; and
2. **non-gauge separation:** every pair in different `Gamma` orbits is
   separated by at least one query.

Equivalently:

```text
fibers(O_Q) = orbits(Gamma).
```

Group equality `Aut(O_Q)=Gamma` is neither required nor generally true. A
proper subgroup can have the same orbit partition. The exact object identified
by data is a quotient partition; the interpretation of that partition as a
reward gauge comes from the independently registered decision problem.

Three outcomes are therefore exhaustive:

```text
some licensed orbit is split       -> overdiscriminates_licensed_gauge
some non-gauge pair remains joined -> underidentified
neither                            -> exact_quotient_identification
```

## Theorem 3: finite minimum access is set cover

Assume every candidate query is gauge-invariant. Let the universe contain all
unordered pairs from different `Gamma` orbits. A query covers precisely the
pairs on which it returns different outputs. A query family identifies the
quotient iff its covered-pair union is the universe.

Hence minimum exact access in a finite deterministic registry is exactly a
set-cover instance. This is a reduction to a classical problem, not a new
complexity theorem.

## Exact controls

The verifier includes:

1. an observation with fibers of sizes three and two, whose full fiber group
   has order `3!*2!=12`;
2. a cyclic group of order three acting transitively on three points, while
   the full constant-observation fiber group has order six—different groups,
   identical orbit partition;
3. a constant observation over two licensed orbits, correctly reported as
   underidentified;
4. a query that splits a licensed orbit, correctly rejected;
5. one exact two-orbit observation; and
6. a two-query minimum set cover over four singleton gauge orbits.

## Correction to the ASMP-9 resolution obligation

Replace:

```text
find the maximal invariance group of a data source
```

with:

```text
freeze the transformations licensed by the declared decision problem;
compute the observation-fiber partition under the declared access;
test equality of that partition with the licensed orbit partition.
```

In the linear v0.69 setting this is exactly the condition
`A^-1(N+A(G))=G`. Version v0.74 gives the underlying set-theoretic statement.

## Claim boundary

The theorem is finite group-action and set-cover bookkeeping. It does not show
that any proposed shaping transformation is behaviorally valid, that a query
channel is physically available, that a response model is correct, or that a
human/model reward exists. ASMP-9 remains unresolved.
