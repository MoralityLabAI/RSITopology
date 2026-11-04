# ASMP-10 transition-liveness pilot v0.4 result

## Verdict

**Transition liveness passed; predictor evidence remains absent.** Three of six
prospectively registered cells met the frozen delayed-transition definition.
The registered branch rule therefore authorizes drafting, but not executing, a
disjoint-seed predictor protocol.

This is a construction-pilot result. Seed 7, its dataset permutation, all six
factorial cells, and every observable derived from them are permanently
ineligible for the later predictor evaluation.

## Frozen-gate result

All cells memorized at step 100 under the registered five-evaluation rule.

| train fraction | weight decay | first held-out transition | delay | delayed candidate | final test accuracy |
|---:|---:|---:|---:|---|---:|
| 0.40 | 1.0 | none by 15,000 | — | no | 0.4125 |
| 0.40 | 2.0 | none by 15,000 | — | no | 0.3640 |
| 0.55 | 1.0 | 1,900 | 1,800 | **yes** | 1.0000 |
| 0.55 | 2.0 | 1,300 | 1,200 | **yes** | 1.0000 |
| 0.70 | 1.0 | 900 | 800 | **yes** | 1.0000 |
| 0.70 | 2.0 | 400 | 300 | no: too early | 1.0000 |

The pilot therefore locates a usable transition regime near train fractions
0.55–0.70. More training data shortened the first-passage delay in this single
construction seed. That pattern is a pilot-selection fact, not a cross-seed
scaling law.

## Important post-gate diagnostic: transitions can revert

The registered liveness rule asks for five consecutive qualifying evaluations;
it does not require the capability state to remain qualified forever. An
independent replay found later failures after the first crossing:

| cell | failures after first crossing | last failure | earliest qualifying terminal tail of at least 20 evaluations |
|---|---:|---:|---:|
| 0.55 / 1.0 | 4 | 14,800 | none |
| 0.55 / 2.0 | 0 | — | 1,300 |
| 0.70 / 1.0 | 2 | 7,000 | 7,100 |
| 0.70 / 2.0 | 1 | 13,200 | none |

This table is a post-hoc diagnostic and does not change the registered pilot
pass. It does change the successor design: the prediction target must separate
first passage, reversion, and terminal stability rather than treating the first
five-point streak as an irreversible phase transition.

## Resource and resume audit

The full factorial required three bounded training segments plus two safe
engineering aborts:

- v0.4 stopped at its wall timeout after two complete cells and a checkpointed
  third cell;
- v0.4a stopped before training because an old heartbeat timestamp looked
  stale;
- v0.4b refreshed the heartbeat but stopped before training when CUDA
  `map_location` moved the saved CPU RNG tensor to the wrong device;
- v0.4c restored the exact RNG bytes on CPU, completed two more cells, and
  stopped at its wall timeout; and
- v0.4d resumed the same scientific state, completed all six cells, and exited
  normally.

Every wrapper cleanup receipt passed. Peak host RAM was 1,662.02 MB, peak I/O
was 10.013 MB/s, and event-derived attributable CUDA peaks were below 100 MB;
all stayed well inside the registered caps. WDDM's process-local
`nvidia-smi` field remained unavailable, so the PyTorch allocator was the
attributable GPU hard cap and global GPU readings were descriptive only.

## Interpretation

The pilot repairs the liveness gap in the ASMP-10 program: this model family can
produce delayed held-out transitions inside local resource limits. It also
finds that first-passage transitions can reverse, which sharpens the target for
the claim-eligible experiment.

It does **not** show that early geometry predicts transition time, that spectral
features beat a loss prefix, that the observed boundary generalizes across
seeds, or that capability transitions in larger models are predictable. It is
unrelated to evidence for recursive self-improvement.

Canonical machine-readable analysis and hashes are in
`pilot_artifacts_v0_4/analysis_v0_4.json` and
`pilot_artifacts_v0_4/receipt_v0_4.json`.
