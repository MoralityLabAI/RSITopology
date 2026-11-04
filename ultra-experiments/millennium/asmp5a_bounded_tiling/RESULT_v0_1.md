# ASMP-5A finite bounded-tiling result v0.1

## Verdict

`finite_multi_resource_tiling_tradeoff_established`

The registered census enumerated all full binary certificate shapes through
twelve independent safety obligations. The largest rung contained 58,786
shapes. All eight frozen gates passed in 3.179 seconds with peak process RSS of
41,230,336 bytes, and all fourteen independent verification checks passed.

## Exact finite result

Inside the registered explicit-conjunction grammar:

- every complete certificate over `k` obligations has exactly `2k-1` nodes;
- minimum critical-path depth is exactly `ceil(log2(k))`;
- a left-associated chain has depth `k-1` and Horton-Strahler memory two for
  every `k>=2`; and
- balancing can minimize depth but increases peak register demand on the
  larger registered instances.

The work statement is not empirical: every admitted proof is a full binary
tree with one leaf per obligation, so its node count is forced. The census
checks the complete finite shape universe and independently matches a dynamic
program over reachable `(depth,memory)` pairs.

## Resource-ranking reversal

Maximum certifiable obligations within the registered range were:

| Budget | Work | Depth | Memory | Chain | Balanced | Best shape |
|---|---:|---:|---:|---:|---:|---:|
| `shallow_parallel` | 23 | 4 | 4 | 5 | 12 | 12 |
| `memory_tight_serial` | 23 | 11 | 2 | 12 | 3 | 12 |
| `balanced_middle` | 15 | 3 | 3 | 4 | 7 | 7 |

Thus balanced tiling more than doubled capacity relative to the chain under
the shallow-depth budget, while the chain quadrupled capacity relative to the
balanced architecture under the memory-two budget. Both used the same
semantic leaf obligations and the same total-work accounting.

This is the main instrument finding: "proof-strength margin" is not one scalar
until work, latency, and memory have a frozen scalarization. Two sound
certificate layouts can reverse order under two legitimate bounded-resource
regimes.

## Semantic controls

Every accepted certificate had to expose each independent obligation as one
unique leaf. A constant-size unexpanded summary was rejected, as was a tree
duplicating one obligation while omitting another. Reversing all obligation
labels preserved validity and all structural metrics.

These controls prevent the apparent tiling improvement from being purchased by
silently weakening the safety consequence.

## Prior-art and novelty boundary

The node count, binary-tree depth bound, Horton-Strahler register measure, and
work-depth tradeoff are classical. This result is a registered consolidation
and executable theorem-generator, not new tree combinatorics. Its contribution
to ASMP-5A is to make the proof-budget metric explicit and to exhibit a finite
ranking reversal before a richer reflective logic is attempted.

Nothing here proves bounded Lob, composes arithmetic reflection principles,
models learned verifiers, or establishes open-ended safe self-modification.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `artifacts_v0_1/result_v0_1.json` | `a221d2e57d22ff8480fb5f6c27d1b3eba4edce26092d73c1db3003bb1cc2ff3b` |
| `artifacts_v0_1/receipt_v0_1.json` | `b6701e4a5ef4508ed606e19bbb98219638d0eccd3bc264f21358c243dbbdd997` |
| `artifacts_v0_1/verification_v0_1.json` | `e41e03b4337e33d8823c6acb54980d635f28e0daa12760b24ebd2349f732ee07` |

The prospective registration commit is
`77da25f5328f4cb7ffa29e3532c5949c13fa7d9c`.
