# ASMP-9 physical dynamic bridge v0.67.1: construction result

Status: **stopped after construction instrument failure**.

Confirmation inference was not run and is not authorized by this result.

## Registered outcome

The construction split completed all 240 deterministic next-token score
records. Hash checks, resource enforcement, post-run cleanup, and a second
analysis replay all passed. The analysis replay reproduced `records.jsonl`,
`analysis.json`, and `calibration.json` byte-for-byte.

The registered instrument preconditions did not pass:

| Check | Result | Registered comparison |
|---|---:|---:|
| Fresh-reset maximum difference | `0.0156250447` | numeric guard `0.0000050062` |
| Stable baseline scenarios | `0 / 10` | at least `8 / 10` |
| Construction transducer conflicts | `3` | exactly `0` required for a transducer claim |

The construction decision is therefore:

> The frozen forced-choice instrument is not stable enough to authorize
> confirmation or a global coarse response-state claim in this execution.

This is a failure of the registered measurement/abstraction, not evidence that
context effects, value structure, or recursive self-improvement do not exist.

## Descriptive observations behind the stop

These values are retained as engineering evidence only:

- substantive content exceeded the content-free label control in `20 / 20`
  scenario-by-target cells;
- median content-minus-label specificity was `0.9335937351`;
- the exact one-sided sign-test value was `9.5367431640625e-07`;
- all `20 / 20` washout cells fell inside the broad construction restoration
  envelope;
- no created-consensus cell was eligible because no baseline interval was
  stably opposed under that envelope; and
- the three-state construction transducer had conflicts for
  `repeat_same_advice` from state `-1`, `content_to_0` from state `0`, and
  `content_to_1` from state `0`.

The apparent restoration result is not independently strong: the restoration
envelope was `0.6640625`, set by the maximum display-order half-range. That
same large order envelope caused the baseline-stability gate to fail.

## What the result changes

The run falsifies this version's operational premise that one globally stable
three-state forced-choice observable can be calibrated from these prompts and
then used as the basis for a held-out response-transducer claim.

It does **not** falsify the narrower within-prompt difference-in-differences
observation that substantive content moved the model more than an unverified
label. A successor protocol would need to separate endpoint-specific validity:

1. score byte-identical reset probes in identical singleton tensor shapes, or
   register a numerical calibration independent of the scientific scenarios;
2. restrict display-order stability to endpoints that require an absolute
   baseline sign, rather than using it to invalidate every within-order
   contrast; and
3. replace the failed global three-state transducer with an explicitly
   context-conditioned or margin-resolved object.

Those are successor hypotheses. They are not post-hoc repairs to v0.67.1, and
the untouched confirmation split remains closed.

## Execution and integrity

- source commit: `29a9b707045a7510fea76b30b508ef9e0ffdc292`
- amended protocol SHA-256:
  `1cabf5da8df8165e20ec7ef09c8eccdee9c0d9873c9fafe7e77eeb8634689ac0`
- environment registration SHA-256:
  `c41812d43ccdb2999726352c0600738b6f17c174d91e95be699da6544bfe0ca9`
- records SHA-256:
  `207753cd2d047ca8f0ce02c593254cf2031eee960c070c3c837f39327f9886a9`
- analysis SHA-256:
  `dca8a14a7a50bc290bb5b4d66e4e828a7df3686a26fdf8b2773ff2ded1815306`
- calibration SHA-256:
  `25ebea1c930314c4557f8fab713a1ac66d572ae801eadcea656e835f08159895`
- completed pod: `ec7a1d8595a24c6d9d973f7fea958bc4`
  (non-spot A6000 48 GB)
- runtime: `86.6001` seconds
- peak CUDA allocation: `1955.03` MB
- wrapper peak GPU delta: `3385` MB
- peak GPU temperature: `31 C`
- cleanup: passed; no lingering GPU process
- repository tests on the execution host: `10 passed`
- compact receipt set:
  [`artifacts/construction_v0_67_1`](artifacts/construction_v0_67_1)
- full local bundle:
  `D:\Research_Engine\runs\asmp9_physical_dynamic_bridge_v0_67\prime_construction_v0_67_1_20260729`
- full local manifest audit: `508 / 508` hashes matched

## Attempt history

No score was opened before the v0.67.1 resource amendment.

- a filesystem-cap lookup defect was fixed before inference;
- a noncanonical model filename and missing Python development header each
  caused zero-record failures;
- the v0.67 batch-eight attempt was stopped by the hard GPU guard after
  `56 / 240` unrevealed work units, motivating the preregistered batch-four
  amendment;
- the provider terminated a spot A100 retry after `224 / 240` unrevealed work
  units, before its ephemeral artifacts could be copied; and
- the final non-spot A6000 execution started from a clean result directory and
  completed the registered v0.67.1 construction split.

## Claim boundary

This is a deterministic forced-choice context-state study in one
Qwen3.5-0.8B-Instruct model. It does not measure persistent weight change,
moral truth, human values, a general value state, evaluator-channel recursive
improvement, or resolve ASMP-9.
