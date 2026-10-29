# ASMP-12 constructible survival correspondence result v0.3.1

## Final disposition

`finite_constructible_survival_correspondence_built`

The source-bound v0.3.1 run reproduced the v0.3 finite graph correspondence
and closed the registry and payload-verification gaps found by peer review. All
seven primary gates and all ten import-independent checks passed. The synthesis
receipt binds the source checkpoint, exact manifest, compact result,
independent verification, and a root over every evidence family.

This is a finite exact result for the registered three-program source-table
universe. It is not an ordinary bifiltration, a homology or barcode result, or
a claim about mixed strategies, unrestricted programs, language models, or
equilibrium-selection dynamics.

## Task result

The exact object contains:

| object | count |
|---|---:|
| weighted profitable-deviation cell graphs | 24,576 |
| gain-preserving adjacent budget inclusions | 16,384 |
| typed adjacent-union temptation zigzags | 21,504 |
| nonmonotone temptation steps | 1,576 |
| cooperative-sink events | 21,312 |

The temptation relations remain:

| relation | count |
|---|---:|
| equal underlying graphs | 17,720 |
| left strict subgraph of right | 2,208 |
| right strict subgraph of left | 1,576 |
| incomparable | 0 |

The event counts remain 18,080 budget births, 1,632 budget deaths, 1,600
temptation deaths, and zero temptation births. The canonical exact certificates
remain margin `2 -> -1` for the budget-2-to-3 death at `T=4`, and margin
`0 -> -1` for the temptation-3-to-4 death at budget 3, with the two gain-`1`
outgoing deviations reproduced exactly.

## Measurement reliability

Peer review demonstrated that v0.3 could retain its counts while replacing a
frozen temptation, duplicating a catalog, omitting and duplicating an
adjacency, forging an event margin or gain, or relabeling a graph relation.
Those mutations are now explicit rejection tests.

The v0.3.1 verifier independently constructs and checks:

- the exact machine manifest and ordered 512-catalog binary product;
- the exact payoff families, costs, budgets, and temptation values;
- all 24,576 Cartesian graph keys, without duplicates or omissions;
- all 16,384 ordered budget adjacencies;
- all 21,504 ordered temptation adjacencies;
- every cell graph, rational gain, margin, sink, and cooperative sink;
- every union edge, endpoint decoration, relation, and direct-inclusion label;
  and
- all 21,312 complete event records, including multiplicity, exact endpoint
  margins, statuses, edge identities, and gains.

All ten independent checks passed. The scoped suite passed 10 tests, including
the four concrete stale-green mutation families. The five original robustness
probes also passed: cost padding, program-label equivariance, the source-blind
column null, the exact boundary microgrid, and positive-margin perturbation.

## Claim support

The result supports only the registered finite constructible correspondence:
exact budget inclusions, underlying-graph temptation zigzags with endpoint gain
decorations, and a separate cooperative-sink event process. It does not turn
the nonnested equilibrium sets into an ordinary two-parameter persistence
object. Any algebraic successor must separately freeze its category, maps,
coefficients, and stability claim.

## Operation and provenance

- Source checkpoint:
  `fc7310a5061ad0843d01c8fbea7f67c5d5657810`.
- Execution: deterministic exact CPU arithmetic; no GPU or network.
- Machine manifest: `protocol_v0_3_1.json`.
- Manifest/catalog SHA-256:
  `8b3e2a44c4cddca770554dada7b89ebdd41f835a6a59c85b8647a458c61358c1`
  for the canonical catalog sequence and
  `2ece67ceedd13163c4b4891eb306568d99fe8599838edeac19d74ab278c510f7`
  for the manifest bytes.
- Cell-graph root:
  `eeaa4fa8bafddfcd77b2ef81562add01ca9768b6939bee0488d63b204430dfe0`.
- Evidence root-of-roots:
  `59a86eea88f48acbaf089cc7561626c292d8f9faf703000c0ce847cc6eb342a7`.

The root-of-roots separately binds the manifest, ordered catalogs, graph-key
registry, all cell graphs, budget maps, temptation zigzags, cooperative-sink
events, and robustness probes.

## Artifact hashes

| artifact | SHA-256 |
|---|---|
| `artifacts_v0_3_1/result.json` | `f82970f0969b700960db13c12147fa3173f5ad5010833974dcbb86c3fe889cc0` |
| `artifacts_v0_3_1/independent_verification.json` | `d66182331b2885cc12d99ffaa18ccdd1ca045a412b609f7da46f19269d4ed5ef` |
| `artifacts_v0_3_1/synthesis_receipt.json` | `2c2415d9a80ffc538152281d458b4b3b07bad8a48aa76df5357a885d3e535f6f` |

## Replay

The evidence directory is write-once. Replay against the bound source into a
fresh directory:

```powershell
python build_artifacts.py --source-commit fc7310a5061ad0843d01c8fbea7f67c5d5657810 --output-dir artifacts_v0_3_1_replay
python -m pytest test_constructible_survival.py -q
```

The prior `artifacts_v0_3/` bundle remains in Git only as a superseded
historical record. Its mathematical counts were reproduced, but its verifier
is not accepted as final reliability evidence.
