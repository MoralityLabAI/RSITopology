# Shortest mixed cycles need not minimize gluing-query noise

## Status

Unregistered development finding with an exact rational certificate.

## Smallest observed witness

Use four items and two contexts:

```text
context 0: (0,3), (1,2)
context 1: (0,1), (0,2), (1,3), (2,3).
```

There are six context-labelled edges. The context-local image has rank five,
the shared-scalar image has rank three, and the gluing-obstruction dimension
is two.

The shortest spanning mixed-cycle design uses two triangles and total support
six. After normalizing each query by its full edge-noise norm, its exact
restricted Gram matrix is:

```text
[2/3   0 ]
[ 0   2/3].
```

Therefore:

```text
sigma_min = sqrt(2/3)
worst-case amplification = sqrt(3/2) = 1.224744871...
```

Two four-edge mixed cycles use total support eight but have exact Gram matrix:

```text
[1  0]
[0  1].
```

They form an orthonormal basis of the gluing quotient and attain the arbitrary
linear-query optimum:

```text
sigma_min = 1
worst-case amplification = 1.
```

Thus minimum query count and minimum total cycle support do not imply minimum
worst-case error. On this witness, insisting on the shortest basis costs
`22.47%` in worst-case amplification.

## Development census

The unregistered ordered two-context census found:

- no counterexample with two or three items;
- among the 3,819 live four-item graph pairs, 574 had a
  conditioning-suboptimal shortest basis;
- none of the 864 rank-one quotients were suboptimal;
- 18 of 1,511 rank-two quotients were suboptimal; and
- 556 of 1,444 rank-three quotients were suboptimal.

The largest observed shortest-versus-E-optimal amplification ratio was
`1.8228756555`.

These counts are development evidence, not registered results. The exact
claim currently supported is only the explicit six-edge counterexample and
its rational Gram matrices.

## Why it matters

Version v0.11 proved that `q` independent checks are necessary and sufficient
in exact arithmetic. This example proves that the choice among those
`q`-element bases matters under noise. A robust access theorem must therefore
report at least:

- obstruction dimension;
- the admissible query grammar;
- `sigma_min` or an equivalent condition measure; and
- the resulting worst-case reconstruction amplification.

Counting loops or selecting the shortest basis is insufficient.
