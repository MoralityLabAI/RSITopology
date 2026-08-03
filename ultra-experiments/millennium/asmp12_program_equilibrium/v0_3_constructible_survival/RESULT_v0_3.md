# ASMP-12 constructible survival correspondence result v0.3

## Verdict

`finite_constructible_survival_correspondence_built`

The deterministic report from source checkpoint
`487f2cde89289bee9d7e6989304cc8ab66feae0e` passed every registered gate. A
separate invocation of the independent implementation reconstructed every cell
graph, map, adjacent union, and cooperative-sink event signature.

## Exact constructible object

The run built the complete finite object over 512 source-table catalogs, two
payoff families, eight exact temptation values, and three budgets.

| object | exact count |
|---|---:|
| weighted profitable-deviation cell graphs | 24,576 |
| verified gain-preserving adjacent budget inclusions | 16,384 |
| typed adjacent-union temptation zigzags | 21,504 |
| nonmonotone temptation steps | 1,576 |
| cooperative-sink events | 21,312 |

Every cell graph passed incidence and signed-margin typing. Every old budget
edge retained its exact rational gain, and the `budget 1 -> 2 -> 3` composites
verified.

The temptation relations partitioned exactly as follows:

| adjacent underlying-graph relation | count |
|---|---:|
| equal | 17,720 |
| left strict subgraph of right | 2,208 |
| right strict subgraph of left | 1,576 |
| incomparable | 0 |

All 21,504 spans were nevertheless represented uniformly as

`G_T -> (G_T union G_T') <- G_T'`.

The union maps are maps of underlying finite directed graphs. Exact gains stay
as endpoint decorations; no weight-preserving temptation-axis map is claimed.

## Cooperative-sink events and exact margins

Sink events were derived after graph construction and stored separately from
graph maps.

| axis and event | count |
|---|---:|
| budget cooperative-sink birth | 18,080 |
| budget cooperative-sink death | 1,632 |
| temptation cooperative-sink death | 1,600 |
| temptation cooperative-sink birth | 0 |

For the canonical catalog 24 and profile `(1,1)`:

- at `T=4`, increasing budget from 2 to 3 changes the exact signed margin from
  `+2` to `-1`; two newly live unilateral deviations each have gain `1`;
- at budget 3, increasing temptation from `T=3` to `T=4` changes the margin
  from the exact tie `0` to `-1`, with the same two gain-`1` outgoing edges.

These are event certificates, not graph-map definitions. The first endpoint is
a cooperative sink and the second is not.

## Reliability gates

All six conjunctive gates passed:

| gate | result |
|---|---|
| every cell graph defined and margin typed | pass |
| budget inclusions and composition verified | pass |
| adjacent-union zigzags typed | pass |
| cooperative-sink events separate and certified | pass |
| independent reconstruction | pass |
| five robustness probes | pass |

The independent verifier reproduced all 24,576 graphs and all 21,312 event
signatures. Its five checks passed: exact cell reconstruction, budget-map
reverification, adjacent-union reverification, sink-event signature
reverification, and registered graph-count reproduction.

## Five robustness probes

| probe | exact evidence | result |
|---|---|---|
| cost-padding replay | 24,576 graph comparisons | pass |
| program-label equivariance | 24,576 comparisons under permutation `(2,0,1)` | pass |
| source-blind column-permutation null | 384 comparisons | pass |
| exact boundary microgrid | margins `+1/100,0,-1/100` at `T=2.99,3,3.01` | pass |
| positive-margin payoff perturbation | 12,384 positive certificates and 19,680 zero-margin controls | pass |

For each positive margin `m`, the perturbation probe used `epsilon=m/4`, so
the certified residual comparison margin is `m-2epsilon=m/2>0`. Zero-margin
cells deliberately receive no positive robustness certificate.

## Four conclusion layers

### Task result

The registered finite graph correspondence was built, including verified
budget inclusions, explicit adjacent-union temptation zigzags, and separate
cooperative-sink events. The deterministic cell-graph digest root is
`eeaa4fa8bafddfcd77b2ef81562add01ca9768b6939bee0488d63b204430dfe0`.

### Reliability

Exact `Fraction` arithmetic, complete finite enumeration, typed-map checks,
exact event witnesses, five robustness probes, the scoped tests, and a
structurally separate verifier support the computation in the frozen class.

### Claim support

The result supports only the registered finite constructible correspondence.
It does not support an ordinary bifiltration of equilibrium sets,
weight-preserving temptation maps, homology or barcode claims, mixed or
unrestricted equilibria, language-model cooperation, or an equilibrium
selection dynamic.

### Operation

The report and verification were deterministic CPU-exact operations. They used
no GPU or network and made no repository writes during computation. The compact
JSON files in `artifacts_v0_3/` are post-run records of those outputs.

## Artifact and source binding

- source checkpoint:
  `487f2cde89289bee9d7e6989304cc8ab66feae0e`;
- compact result: `artifacts_v0_3/result.json`;
- compact result SHA-256:
  `4edfb7f86f98dc69aea465c3e40103c3e36d7ddcf1be1637daedf47b823ca58e`;
- independent verification: `artifacts_v0_3/independent_verification.json`;
- independent verification SHA-256:
  `32e8a6e625c1dd5c66c2b35a4e1478df7e6ad993620747f2b5ffe092f85f0918`;
- schema: `asmp12_constructible_survival_v0_3_result_v1`.

## Reproducibility

From the repository root, rebuild the four-layer report with:

```powershell
python ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival/run_constructible_survival.py
```

Replay the independent verifier separately with:

```powershell
python -c "import json,sys; sys.path.insert(0,r'ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival'); import constructible_survival as p, verify_constructible_survival as v; print(json.dumps(v.verify_surface(p.build_surface()),indent=2,sort_keys=True))"
```

Run the complete scoped software and scientific checks with:

```powershell
python -m pytest ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival/test_constructible_survival.py -q
git diff --check -- ultra-experiments/millennium/asmp12_program_equilibrium/v0_3_constructible_survival
```

## Claim boundary

This result realizes an explicit finite graph correspondence and derived
cooperative-sink survival process for the inherited three-program source-table
catalog and exact payoff grid. It does not turn the nonnested equilibrium sets
into an ordinary two-parameter persistence object. Any later algebraic functor
must separately freeze its category, maps, coefficients, and stability claim.
