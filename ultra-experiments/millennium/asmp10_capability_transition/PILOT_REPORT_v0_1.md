# ASMP-10 transition-liveness pilot report

## Verdict

The frozen modular-addition capability transition was **not live within the
completed 4,000-step pilot**. Extending the horizon did not produce a valid
longer scientific result: the first extension exposed a Windows/WDDM GPU
accounting gap, and the fail-closed retry stopped when aggregate GPU memory
exceeded the registered 3,072 MB allowance. No held-out prediction experiment
is authorized from these pilots.

This is a pilot-selection result, not evidence that grokking, capability
transitions, or useful early predictors do not exist.

## Completed pilot

Four registered chunks completed: two seeds at weight decays 0.1 and 1.0. All
four reached perfect training accuracy but none met the frozen transition rule
(held-out accuracy at least 0.90 and loss at most 0.50 for five consecutive
evaluation points).

| run | final train accuracy | final test accuracy | final test loss | transition |
|---|---:|---:|---:|---|
| seed 0, decay 0.1 | 1.000000 | 0.391681 | 7.293956 | none by step 4,000 |
| seed 1, decay 0.1 | 1.000000 | 0.403813 | 6.861681 | none by step 4,000 |
| seed 0, decay 1.0 | 1.000000 | 0.407279 | 4.561127 | none by step 4,000 |
| seed 1, decay 1.0 | 1.000000 | 0.419411 | 3.394084 | none by step 4,000 |

The Job Object wrapper completed with its RAM, CPU, and I/O caps active;
reported peak host RAM for the job was 1,610 MB and cleanup passed. Windows
WDDM did not expose reliable per-process GPU memory to the wrapper.

## Extension diagnostics

### v0.2: invalid resource run

The unguarded 20,000-step extension was stopped after global GPU use reached
approximately 3.9 GB while the wrapper still reported zero per-process GPU
memory. This demonstrated that the wrapper's WDDM query could not enforce the
registered GPU allowance. The partial metrics are retained only as engineering
evidence; they are not a scientific extension of the pilot.

### v0.3: valid fail-closed abort

An additive in-process guard sampled aggregate `nvidia-smi` memory once per
second and converted a breach into the trainer's normal abort/cleanup path. It
stopped the run at step 8,200 when aggregate use reached 3,950 MB. At the last
completed evaluation, training accuracy was 1.0, test accuracy was 0.410745,
and test loss was 3.622534. The wrapper recorded exit code 2, cleanup passed,
and no owned PID remained.

Because another Qwen process was using the same physical GPU, the aggregate
breach cannot be attributed solely to this pilot. The conservative guard is
doing admission control, not per-process attribution. The aborted run therefore
does not update the scientific transition estimate.

## Branch decision

Do not freeze the positive held-out predictor comparison from this model family
yet. The next ASMP-10 work item should be CPU-exact and address the registered
negative branch: characterize when a finite prefix of local training
observables admits indistinguishable polynomial-loss continuations with
different future capability outcomes. A new GPU pilot may be considered only
after the shared GPU is idle and a smaller-footprint or longer-horizon family
has been separately authorized.

## Artifact hashes

| artifact | SHA-256 |
|---|---|
| `pilot_artifacts_v0_1/summary.json` | `17def2031d57b011dfdc37b4aeae57d89e778b807ed34de83943c91720a45e65` |
| `pilot_artifacts_v0_1/events.jsonl` | `eae9187dff7f3f33fd6c6a0b3b1ea5160cb5d15fe89e9b198db941e1b7d94811` |
| `pilot_wrapper_v0_1/wrapper_summary.json` | `0762d506b1907241c0ee801f252a222f046c736d5867e4a6fa0762d12682762a` |
| `pilot_artifacts_v0_2/events.jsonl` | `94d4e831dfa02727d35968142f5650f7cb5a8cfef863c1618fb33d2a571da343` |
| `pilot_wrapper_v0_2/wrapper_summary.json` | `3540cbec54e0a0f1500f9c7c5153f46f2d4c03a9a51f7a9d235636d80bd0fefa` |
| `pilot_artifacts_v0_3/summary.json` | `4e00bbb9a2ea712eb4b677733d160b773ccaac19c99786e3e5c880786b4ba2b1` |
| `pilot_artifacts_v0_3/events.jsonl` | `c93a6918ec5092767c564d676b5c0774426610b69737305f6ebf9c8cd7e6956d` |
| `pilot_artifacts_v0_3/gpu_guard_summary.json` | `2b5135c0c8abb103469ff654ab6e7292825fcc1183f2b2732d319e25c745c67c` |
| `pilot_wrapper_v0_3/wrapper_summary.json` | `02bdebf8e995ed956a2ae3c2508ba9e0d31349a32d792d270e2ccb528156a91a` |

The wrapper validation receipt is
`artifacts/hard_cap_validation/asmp10_grokking_v0_1/hard_cap_validation_receipt.json`
with SHA-256
`233486f7dfa43badee804118b0667c0edc632ca247b1113dc7e53d5e844905a3`.

## Claim boundary

These pilots establish only that this registered configuration did not show a
transition by step 4,000 and that the hard-cap machinery stopped unsafe or
ambiguous extensions. They do not establish an impossibility theorem, a
cross-seed predictor result, a capability forecast, or evidence about recursive
self-improvement.

