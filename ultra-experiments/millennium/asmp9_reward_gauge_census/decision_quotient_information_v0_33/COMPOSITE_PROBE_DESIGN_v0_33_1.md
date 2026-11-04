# Factorized acquisition design for the ASMP-9 coupling quotient

## Status

**Unregistered development result. Not claim-eligible.**

The v0.33 coupling theorem gives an 18-dimensional decision quotient inside
a 48-dimensional raw coupling space. This note asks whether the quotient can
be acquired through a structured candidate grammar rather than arbitrary
linear functionals.

```text
focused v0.33 tests                    22 passed
v0.28-v0.33 predecessor/current tests 104 passed
development JSON SHA-256               4ab72bb7f60c4cfd9b6d000514c00de61d968f862d5f4682af41ef09de97f20b
```

The JSON is
[`COMPOSITE_PROBE_DEVELOPMENT_v0_33_1.json`](COMPOSITE_PROBE_DEVELOPMENT_v0_33_1.json).

## Candidate grammar

Let:

```text
A = Q L
```

be the policy-difference analysis matrix and let `C` be the behavioral
cross-difference operator. Choose:

- independent rows `A_I` spanning the row space of `A`; and
- independent columns `C_J` spanning the column space of `C`.

For every pair `(i,j)`, query the scalar composite effect:

```text
(row i of A) K (column j of C).
```

Operationally, this is the candidate grammar “apply one selected behavioral
cell perturbation and read one selected analyzed policy contrast.” Whether
the current model harness can implement those operations with controlled
linearization error is deliberately left open.

## Factorized-basis theorem

The Cartesian product of the selected policy contrasts and behavioral cells
contains exactly:

```text
rank(A) rank(C)
```

scalar probes. Its query matrix is:

```text
transpose(C_J) kron A_I.
```

Because `row(A_I)=row(A)` and
`row(transpose(C_J))=row(transpose(C))`, its row space equals the row space
of:

```text
transpose(C) kron A.
```

It therefore identifies the entire decision effect `A K C` and is
minimum-cardinality among scalar linear query grammars over an unrestricted
coupling space.

## Exact specialization

Greedy exact-rational basis extraction on the sealed matrices selects:

```text
policy-contrast rows  0, 1, 2
behavioral-cell cols  0, 1, 2, 4, 5, 6
```

Their Cartesian product gives 18 probes. The resulting `18 x 48` operator
has exact rank 18 and the same row space as the full `60 x 48` canonical
policy-effect operator.

## Entrywise-tomography control

Every one of the 48 raw coordinates of `K` has a nonzero column in the
canonical policy-effect operator. Therefore a grammar restricted to querying
individual entries of `K` must query all 48 coordinates: leaving any one
unmeasured admits a one-coordinate perturbation with a different policy
effect along the all-zero transcript.

Thus the exact access comparison on these matrices is:

```text
entrywise coupling tomography     48 scalar queries
factorized composite acquisition  18 scalar queries
ratio                              8/3
```

This is an access-grammar result, not a sample-complexity result. Composite
queries are stronger operations than entrywise coordinate reads.

## Prospective gate

A claim-eligible successor should freeze a concrete implementation of the 18
composite probes, then require:

1. exact construction rank 18 before outcomes;
2. held-out secant/Jacobian agreement at every admitted intervention norm;
3. a simultaneous reconstruction bound for the 18 quotient coordinates;
4. an entrywise 48-probe comparator under matched scalar-observation cost;
5. explicit `not_evaluated` when the physical probe operator loses rank or
   linearity; and
6. a decision-changing null witness whenever the admitted query row space
   has rank below 18.

## Claim boundary

No model intervention was run. No physical probe has been demonstrated.
The 18-query design assumes exact scalar composite access, while the
entrywise comparator assumes exact coordinate access. Noise, dependence,
query cost, nonlinear remainder, and behavioral validity remain unregistered.
ASMP-9 remains unresolved.
