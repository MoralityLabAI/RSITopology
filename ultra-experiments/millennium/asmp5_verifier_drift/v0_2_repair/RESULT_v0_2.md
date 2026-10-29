# ASMP-5 repaired bounded verifier-drift result v0.2

## Verdict

`exact_bounded_verifier_drift_counterexample`

The versioned repair completed all 36 registered cells in 3.559 seconds with
peak process RSS of 28,336,128 bytes. All eight runner gates passed. A separate
implementation then replayed every cell, candidate-universe receipt, unsafe
path, and safe-chain witness; all thirteen independent checks passed.

This supplies the scientific result that v0.1 could not produce inside its
resource cap. It does not rewrite the valid v0.1 status: that run remains
`unavailable_resource_cap_stop_sequence`.

## Finite separation

At behavior width six, adaptive activation of the installed successor checker
reached an analyst-labelled unsafe behavior at minimum depth two in all four
registered non-rooted primary cells:

| Mutation radius | Rule | Adaptive unsafe depth | Frozen-root unsafe through depth 8 |
|---:|---|---:|---|
| 1 | `self_endorsement` | 2 | none |
| 1 | `pairwise_agreement` | 2 | none |
| 2 | `self_endorsement` | 2 | none |
| 2 | `pairwise_agreement` | 2 | none |

Both arms stored the same proposed checker and traversed the same candidate
edge universe. The contrast changes only which checker becomes active on the
next step.

The finite mechanism is direct: a safe first update installs a checker with a
larger acceptance set; that successor checker then certifies a hazard-bit
update the frozen root rejects. The result is therefore a matched bounded
counterexample to unrestricted local successor-checker self-endorsement.

## Rooted positive control

`root_refinement` admitted no unsafe state through depth eight at radii one and
two. At radius one it also retained the preregistered liveness witness: eight
accepted steps through nine distinct safe behavior vectors. The safe chain
reached progress eight and the full set of 32 safe behavior vectors was
reachable somewhere in the census.

This is only a finite positive control. It shows that the registered rooted
rule did not obtain safety by making the toy system inert.

## Why the repair is exact

The v0.1 proof alphabet has four tokens but only two registered proof classes.
Tokens are not stored, consumed, or otherwise observed after certification.
The v0.2 engine therefore retains the least token in each class. Before
registration, its complete layer sets were compared against the unquotiented
v0.1 implementation on disjoint widths three and five, both regimes, all three
rules, and radii zero and one. Every layer matched exactly.

Version 0.2 also replaces enumeration of millions of universe-hash updates
with the registered closed-form candidate count and a hash of the sealed
generation specification. The independent verifier recomputes those counts
and specifications.

## Controls

- radius-zero adaptive and root arms were identical;
- proof-token renaming preserved reachability;
- swapping two non-hazard behavior coordinates preserved every layer;
- a permissive checker reached unsafety at depth one;
- width four was correctly marked unavailable for the nine-vector liveness
  requirement because it contains only eight semantically safe vectors;
- label permutation changed semantic analysis but not reachability.

## Claim boundary

This is one exact finite-state result. It demonstrates that local certificates
need not compose when their interpreter can be replaced, even with candidate
updates matched, and that a frozen-root acceptance-set refinement avoids the
planted failure without killing bounded progress.

It does not establish an open-ended reflective-safety frontier, infinite
progress, robustness for learned checkers, or recursive self-improvement. The
trusted-root lesson is consistent with proof-carrying-code and reflective-agent
prior art and is not claimed as a new theorem.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `artifacts_v0_2/result_v0_2.json` | `f4679c0100593141a263707a676c3fb3e83535d43d9c82b44826c11561c61941` |
| `artifacts_v0_2/receipt_v0_2.json` | `0e292bbc2a0da05483e77d991f65dbca0b0d8abcaf792b06a3fca140c41291b5` |
| `artifacts_v0_2/verification_v0_2.json` | `7cd89a52e015c43b5236ea1ca81fc1c111007088ad0436451dd4585eaa4965a2` |

The prospective registration commit is
`25be3ce1924bd9e0b94a7d838fadc9f33c4c85db`.
