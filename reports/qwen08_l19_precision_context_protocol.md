# Qwen0.8B L19 precision/context replication

## Question

Stage B localized its common-rank failure to context rather than checkpoint transport. At L19, the four-bit `naive_qlora / shard-02` node failed rank one while the corresponding unquantized-float16 node passed. This fresh experiment asks whether that crossing replicates on new graph instances and whether it is unusually localized, rather than merely one cell on top of a broad float16 uplift.

The sentinel was selected from revealed Stage-B geometry, so the old contrast is retrospective. The prompt corpus in this protocol is fresh and the sentinel, sites, ranks, states, null, and interaction statistic are frozen before capture.

## Measurement

For precision arm `p`, state `s`, and context shard `c`, the rank-one Stage-B support margin is

```text
M[p,s,c] = Q0.05(real-label split retention)
           - Q0.95(matched random-label split retention)
           - 0.02.
```

`M > 0` is exactly the inherited strict support gate. The analysis stores all three terms so a larger margin can be separated into real-retention gain versus a lower random-label boundary.

The paired precision effect is

```text
Delta[s,c] = M[float16,s,c] - M[4bit,s,c].
```

Its 1,024 outer bootstrap draws jointly resample prompt IDs inside each frozen `half × subcondition` stratum. Each outer draw recomputes the complete `M` functional from 64 inner real-label and matched-permutation draws. Resampling indices and label permutations are identical across precision arms.

The preregistered localization contrast is

```text
I = Delta[naive_qlora, shard-02]
    - median(Delta for the other L19 state × shard cells).
```

The sentinel is called precision-specific only if float16 passes its own matched-null gate, four-bit fails its own gate, and the one-sided 95% lower bound for `I` is strictly positive. The paired analysis never substitutes for either arm's support gate.

## Fixed capture

- Model: locally content-addressed `Qwen/Qwen3.5-0.8B-Base`.
- States: `base`, `naive_qlora` (engineering checkpoint axis only).
- Sites: residual-block outputs at `model.layers.19` and `model.layers.23`.
- Precisions: four-bit NF4 with float16 compute; unquantized float16 weights. Activations are stored float32 in both arms.
- Prompt position: final non-padding prompt token.
- Corpus: 2,304 fresh graph-reachability prompts per state, 32 examples per subcondition × half × shard.
- Freshness: zero byte-identical overlap with the completed Stage-B manifest.
- Outcomes, generation, gradients, and weight mutation: absent.

Four-bit and float16 use the same prompt bytes, order, tokenizer source, shard assignments, and token-position rule. They remain separate `CaptureStore` instances because the established store keys state but not quantization.

## Holonomy boundary

Holonomy is downstream and diagnostic. It is evaluated only when an entire site supports rank one in both precisions and its lineage graph has `beta_1 > 0`. At rank one the only loop invariant reported is `det(H) ∈ {+1,-1}`. A negative determinant is an orientation-reversal error; canonical angles are suppressed. No result from this experiment adds an attestation level or authorizes causal edits or VPD work.

## Resource and provenance discipline

Each arm is a separate hard-capped, resumable capture. Authorizations bind the protocol, causal model lock, fresh manifest, prompt-separation receipt, precision-pair receipt, state, precision, source hashes, environment, model/adapter hashes, wrapper validation, cleanup script, command, output path, and resource caps. Capture summaries record Torch's peak CUDA allocation because process-level GPU monitoring does not reliably observe it.

## Commands

Generate or verify the frozen prompt artifacts:

```powershell
python scripts/prepare_qwen08_l19_precision_context.py generate-manifest `
  --manifest-output protocols/qwen08_l19_precision_context_prompt_manifest_v0_1.json `
  --separation-output protocols/qwen08_l19_precision_context_prompt_separation_v0_1.json `
  --pair-output protocols/qwen08_l19_precision_context_manifest_pair_v0_1.json

python scripts/prepare_qwen08_l19_precision_context.py verify-manifest `
  --manifest protocols/qwen08_l19_precision_context_prompt_manifest_v0_1.json `
  --separation-receipt protocols/qwen08_l19_precision_context_prompt_separation_v0_1.json `
  --pair-receipt protocols/qwen08_l19_precision_context_manifest_pair_v0_1.json
```

Run the deterministic controls:

```powershell
python -m pytest tests/test_qwen_precision_context.py -q
```

The authorization commands are intentionally not abbreviated here: use `--help` and provide every cap, reserve, input index, output path, wrapper, cleanup script, and validation receipt explicitly. Captures and analysis must run only through `scripts/run_qwen_holonomy_jobobject.ps1`.

## Claim boundary

This experiment can establish or falsify a precision-conditioned, rank-one representation-support effect on one frozen model pair and fresh prompt design. It cannot establish causal edit value, VPD efficacy, capability preservation, compactification, recursive self-improvement, or RSI.
