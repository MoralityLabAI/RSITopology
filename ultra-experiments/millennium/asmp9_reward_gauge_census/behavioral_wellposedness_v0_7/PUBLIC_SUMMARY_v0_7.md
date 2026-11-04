# Behavioral access separates scalar reconstruction from model checking

## Result

Take a finite directed comparison graph `G=(V,E)`. For each registered edge
`(i,j)`, suppose a population response law supplies the exact reciprocal
log-odds:

```text
l_(i,j) = log(P(j preferred to i) / P(i preferred to j)).
```

A coherent scalar Bradley-Terry model has:

```text
l_(i,j) = theta_j - theta_i.
```

The exact access requirements split into three different tasks:

```text
reconstruct theta, coherence promised: |V|-c(G) edges;
certify coherence only:                every non-bridge edge;
reconstruct and certify the full law:  every edge.
```

After a spanning forest reconstructs a candidate scalar, the number of
remaining independent fundamental-cycle checks is:

```text
beta_1(G) = |E|-|V|+c(G).
```

This exposes a common oversight error: a scalar can be reconstructed from a
tree only because its existence was assumed. The cycle queries are the exact
additional tests of whether the demonstrator admits that scalar at all.

## Inconsistent demonstrators

The response field is coherent if and only if every cycle sum vanishes. Its
closest unweighted scalar model is the graph-Hodge projection:

```text
theta_hat = argmin_theta ||l-B theta||_2^2,
r = l-B theta_hat.
```

The residual is orthogonal to every scalar-gradient field and is zero exactly
when a scalar response model exists. For a cycle `C` of length `k`:

```text
||r_C||_2^2 >= circulation(C)^2/k,
||r_C||_infinity >= |circulation(C)|/k.
```

The planted rock-paper-scissors response cycle has edge scores `(1,1,1)`,
fundamental-cycle residual `3`, and Hodge residual `(1,1,1)`. This is not a
different reward gauge: no scalar value assignment produces those response
laws.

## Deterministic policy observations

The second arm uses a minimal environment-intervention model. The reward
quotient is `theta in [0,1]`; an intervention selects a threshold `t`; and the
demonstrator reveals only its deterministic optimal action:

```text
Y_t(theta) = 1{theta > t}.
```

The sharp minimax ambiguity interval after `k` observations is:

```text
adaptive interventions:    2^-k;
nonadaptive interventions: 1/(k+1).
```

Binary search and equally spaced thresholds attain the respective bounds.
Therefore no finite set of deterministic policy outputs exactly identifies an
arbitrary continuous reward quotient. Adaptive environment interventions
provide exponential rather than linear resolution, but finite access still
identifies only an interval.

## Prospective verification

The protocol and implementation were committed before the fresh cells ran.
The CPU-only execution checked:

- 32,768 fresh oriented simple graphs on six vertices;
- 8,192 fresh seven-vertex directed multigraphs with loops, parallel edges,
  and opposite directions;
- exact forest reconstruction and access counts on every graph;
- 32,635 simple-graph and 6,750 multigraph non-bridge corruptions;
- 6,763 simple-graph and 5,156 multigraph bridge changes;
- 4,096 exact Hodge projections, 3,391 with nonzero residual;
- 1,024 rational cycle fields, 1,022 with nonzero circulation;
- adaptive depths `0..24`;
- optimal nonadaptive designs with `0..1024` thresholds;
- 4,096 random nonadaptive designs; and
- 60 prereveal mathematical tests.

There were zero access-ledger, reconstruction, corruption-detection,
bridge-false-alarm, Hodge-orthogonality, cycle-bound, or policy-width
mismatches. All nine registered gates and the independent artifact verifier
passed.

## Correction before registration

The first development draft incorrectly said that pure coherence certification
required every edge. A skeptical pass caught the bridge exception: bridges
participate in no cycle, so their scores cannot falsify coherence. The theorem,
code, tests, and prospective protocol were corrected before registration.

## ASMP-9 contribution and remaining gap

This supplies one exact behavioral-access theorem and one explicit no-go for a
cycle-inconsistent demonstrator. It does not resolve ASMP-9.

Remaining obligations include:

1. finite-sample estimation when log-odds are not population-oracle values;
2. unknown inverse temperature and response parameters;
3. dependent, contextual, and history-sensitive choice laws;
4. policy observations in general finite MDPs and across transition
   interventions;
5. invariance classes larger than discounted potential shaping; and
6. no-go results for broader non-expected-utility demonstrator classes.

The Hodge decomposition, Bradley-Terry model, and comparison-search bounds are
classical. Novelty is not claimed.
