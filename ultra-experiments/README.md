# Ultra Experiments

Ultra Experiments is the repository's CPU-first discovery lab for mathematical
objects that could improve mechanistic interpretability or scalable oversight.
It deliberately ranges beyond holonomy. Holonomy may appear as a comparator,
but it is not the default explanation and no new invariant level is assumed.

The lab has two outputs:

1. reusable instruments with an explicit consumer in the VPD edit program,
   the HRMmmm control harness, or an oversight audit; and
2. claims that have survived a proposer/prover/challenger/referee workflow.

## Initial research tracks

| Track | Mathematical object | Question | Intended consumer |
|---|---|---|---|
| Transient amplification | finite-horizon operator gain and pseudospectral sensitivity | Can an asymptotically stable edit/response map cross a control boundary before it decays? | HRMmmm control gates; recursive-edit risk audits |
| Oversight blind cones | generalized eigenvectors of behavior and monitor Gramians | Which directions produce large behavioral change while remaining weakly observed? | monitor placement; scalable-oversight red teaming |
| Interaction structure | product-poset Möbius coefficients and sparse interaction hypergraphs | Are behaviors encoded by irreducible combinations rather than single sites? | VPD multi-site edit families |
| Causal redundancy | intervention rank functions, circuits, and approximate submodularity | Which edit sites are substitutes, complements, or self-repairing circuits? | VPD edit planning; Hydra-effect diagnosis |
| Sample thresholds | spiked random-matrix separation and finite-size scaling | Is a superstructure absent, or merely below the sample-support threshold? | capture planning; negative-result interpretation |
| Audit coding | distinguishability and rate/sample-complexity bounds | How many audited bits or probes are required to detect evaluator-relative risk? | scalable oversight; Confinement Width |

The existing `experiments/mobius_synergy_identity_v0_1` experiment is the first
interaction-structure artifact. Ultra does not duplicate or silently amend it.

## Evidence labels

Every claim terminates as one of:

`theorem`, `conditional_theorem`, `computer_assisted_theorem`,
`computational_conjecture`, `empirical_finding`, `heuristic`, `analogy_only`,
`forced_or_vacuous`, `refuted`, or `unresolved`.

Synthetic fixtures validate instruments; they are not transformer evidence.
Linearized transformer results are not global recursive-improvement evidence.
No mathematical score authorizes a model edit by itself.

## Workflow

Each experiment directory contains a frozen claim packet, protocol, source,
tests, and receipts. The collaboration rules are in
[`COLLABORATION_PROTOCOL.md`](COLLABORATION_PROTOCOL.md). New work starts by
copying [`CLAIM_PACKET_TEMPLATE.md`](CLAIM_PACKET_TEMPLATE.md), demonstrating
that the claim is live rather than forced, and naming a kill test before the
primary outcome is read.

The first executed track is `01_transient_amplification`: an exact
finite-horizon control-boundary test that holds the eigenvalues fixed while
varying non-normal coupling. Its deterministic calibration passed; the
transformer application remains untested. See
[`01_transient_amplification/REPORT.md`](01_transient_amplification/REPORT.md).

The first theorem draft for the oversight track is
[`theory/OVERSIGHT_BLIND_CONES.md`](theory/OVERSIGHT_BLIND_CONES.md). It includes
the coordinate-covariant edit metric and the nonlinear remainder term that a
deployable gate would require.
