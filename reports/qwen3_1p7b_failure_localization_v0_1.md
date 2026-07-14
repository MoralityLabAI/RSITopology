# Qwen3-1.7B functional-lineage failure localization v0.1.1

## Result

The sealed, target-blind diagnostic completed without reading behavioral
outcomes. It leaves the registered `noise_floor_only` decision unchanged and
does not authorize signed interventions.

The failure is primarily **prompt-conditioned**, not checkpoint-conditioned or
replica-seed-conditioned. In each of the three spectrally admissible rank-1
families, prompt identity explains more than 95% of the balanced main-effect
sum of squares in held-out retention:

| Layer | Prompt | Replica | Checkpoint | Residual/interactions |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 95.163% | 0.542% | 0.00014% | 4.295% |
| 22 | 98.152% | 0.054% | 0.00188% | 1.792% |
| 27 | 98.593% | 0.121% | 0.0205% | 1.265% |

This decomposition is descriptive. The cross-fit is a held-out anchor-response
test, not prompt-training independence, because every VPD replica was trained
on all eight prompt groups.

## Certification-fragility boundary

The original gate takes the minimum over all 96 held-out cells. The diagnostic
keeps its familywise null threshold fixed at 0.0148365065 and asks how many of
the worst cells would have to be excluded before the remaining minimum crosses
that threshold. Exclusion is diagnostic only; it cannot revise the registered
decision.

| Layer | Registered minimum | Cells at/below null | Exclusions to cross | Remaining cells at crossing | Frozen classification |
| ---: | ---: | ---: | ---: | ---: | --- |
| 16 | 0.0001042252 | 15/96 (15.63%) | 15 | 81/96 (84.38%) | diffuse |
| 22 | 0.0066954482 | 8/96 (8.33%) | 8 | 88/96 (91.67%) | sparse |
| 27 | 0.0000097917 | 18/96 (18.75%) | 18 | 78/96 (81.25%) | diffuse |

Layer 22 is the only family rescued by excluding one complete registered axis
level: excluding `arc-group-05` raises its remaining floor to 0.0280626980, a
margin of +0.0132261915. No single prompt, replica, or checkpoint exclusion
rescues layers 16 or 27.

The worst cells are:

- layer 16: `arc-group-06 / b1 / checkpoint 8`, retention 0.0001042252;
- layer 22: `arc-group-05 / a0 / checkpoint 1`, retention 0.0066954482; and
- layer 27: `arc-group-03 / a1 / checkpoint 1`, retention 0.0000097917.

## Average energy versus uniform identity

The gauge-invariant average/median signal remains substantial while the
worst-direction certificate collapses:

| Layer | Mean cell energy retention | Median | Mean/minimum ratio |
| ---: | ---: | ---: | ---: |
| 16 | 0.4330 | 0.4862 | 4,154x |
| 22 | 0.1953 | 0.1413 | 29x |
| 27 | 0.4131 | 0.4602 | 42,184x |

Thus the negative is not "there is no response energy." It is that a single
global coordinate lacks a uniform lower bound across contexts. Average energy
could support a separately registered, gauge-invariant allocation signal, but
it cannot support the signed global edit rejected by v2.

## Spectral boundary

Across 9,216 module x rank x cell checks, every local spectral failure was an
unresolved band boundary; none was below the relative singular-value floor.
At rank 1 there were 79 unresolved boundaries and 1,073 local passes. The
highest prompt-conditioned rank-1 failure rates were:

- `arc-group-06`: 21/144 (14.58%);
- `arc-group-03`: 17/144 (11.81%); and
- `arc-group-01`: 12/144 (8.33%).

Checkpoint rates were nearly flat: 27/384 at steps 1 and 4, and 25/384 at step
8. Replica variation was smaller than prompt variation, although `b1` was the
weakest replica with 29/288 unresolved boundaries.

This supports a precise mathematical reading: the response operator carries
energy, but its hard dimensional cut is frequently gauge-ambiguous because
neighboring singular directions do not separate by the frozen 1.25 gap. A
future soft or complete-band projector would be a new estimator and needs a
new null; it is not a reinterpretation of this result.

## Frozen protocol and reproducibility

The diagnostic protocol was frozen before localization output under SHA-256
`21e57498a5826c1f46f669b3d7449b2e805b942b44da04da50c744d0785dd14a`.
The first launch stopped before reading source artifacts because direct script
execution lacked the repository import root. The prereveal engineering-only
amendment, with no scientific changes and no outcomes present, is SHA-256
`9f446678ba6a9d5f80452ab0925efb0f4855dc9ddf61c748a3fbab587da9b066`.

The canonical run reconciled:

- the exact 1,152-signature and spectrum universe;
- all 96 module/rank family decisions against the registered summary;
- reconstructed and sealed projectors to maximum absolute error below
  1e-15; and
- registered retention, mean-retention, and threshold fields within the
  frozen 1e-10 tolerance.

A fresh second execution produced six byte-identical output files. The full
RSITopology suite passes 57 tests.

## Claim boundary and v3 implication

This audit localizes identity-certificate failure. It does not measure
behavioral control loss or self-improvement risk directly, and its quantile or
exclusion curves cannot replace the registered minimum.

The evidence points to one next construction, not a threshold change:

1. train genuinely prompt-disjoint VPD replicas rather than reusing all eight
   prompt groups in every estimator;
2. evaluate on a new untouched outer prompt corpus;
3. compare a prompt-conditioned patch plan and a frozen gauge-invariant soft or
   complete-band projector against the current global-coordinate baseline; and
4. collect finite-norm causal outcomes only if that separately registered
   construction clears its target-blind gates.

Canonical artifacts are under
`artifacts/qwen_functional_lineage_v2/failure_localization_v0_1/`.
