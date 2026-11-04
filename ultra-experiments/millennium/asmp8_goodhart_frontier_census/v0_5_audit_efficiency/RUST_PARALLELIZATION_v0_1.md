# ASMP-8 Rust parallelization v0.1

## Outcome

The synthetic audit sampling and moment-reduction path now has a deterministic
parallel Rust implementation. Six workers achieved a **4.953× speedup** over
one worker with identical moment estimates and an identical checksum.

This removes audit arithmetic as a practical bottleneck. It does not accelerate
the Qwen forward pass.

## Matched 8,192-audit-scale comparison

Both conditions processed 8,192 audits for each of 1,024 independent streams:
8,388,608 total synthetic audit samples.

| Workers | Inner runtime | Audit samples/second | Checksum |
| ---: | ---: | ---: | --- |
| 1 | 0.0316242 s | 265,259,137 | `298603a4f5f57250` |
| 6 | 0.0063848 s | 1,313,840,371 | `298603a4f5f57250` |

Parallel efficiency relative to six ideal workers was 82.55%.

## Full Hoeffding-scale stress sample

The instrumented run processed 524,288 audits for each of 1,024 streams:
536,870,912 total samples.

- Inner runtime: 0.3566858 seconds.
- Throughput: 1,505,164,803 samples/second.
- Peak working set: 4,186,112 bytes (3.992 MiB).
- Hard outer cap: 256 MiB RAM and 50% CPU.
- Cleanup: passed, with no lingering owned process.

The binary uses a counter-based SplitMix64 mapping. Each `(seed, stream,
audit-index)` determines its registry atom independently, so scheduling and
worker count cannot change the sample. Each stream accumulates only four
moments; samples are never retained. Memory is therefore
`O(streams + workers)`, not `O(total audits)`.

## Equivalence boundary

Three Rust tests pass:

1. all three error populations match the registered v0.3 formulas;
2. one-worker and four-worker results are bit-identical; and
3. both empirical-Bernstein bounds remain finite and inside `[0,1]`.

The Rust RNG is intentionally worker-count invariant, but it is not NumPy's
registered multinomial stream. The tool therefore does not replace or rewrite
the sealed ASMP-8 v0.5 result. It is an implementation and throughput
instrument.

## Model-forward boundary

The Qwen sample remains approximately 0.952 seconds per 127-token audit on the
available CPU Q4_K_M kernel, or about 2.17 hours for 8,192 model-bearing
audits. That time is spent in native model inference. Rewriting the outer loop
in Rust cannot make the matrix multiply faster.

The next meaningful model-side optimization is a persistent GPU-enabled
inference server with native prompt batching. Rust can feed and reduce those
batches, but the speedup will come from GPU batching rather than the language
of the scheduler.

## Provenance

- Rust source SHA-256:
  `e07e487f3da7b0044aafbd623fd37ac6939896f989d639c1f32533ceb77e6a45`
- Cargo manifest SHA-256:
  `fa11af3477390ce54daef26be933e1a2e137e3861a5d2e8db386dc60c4ae3ed4`
- Cargo lock SHA-256:
  `4224358fc7adbe8d0d5d21df96e18eb40c4b11a2f62fc457dc6deeb9c8347f15`
- Serial 8K raw receipt SHA-256:
  `258e7764bac0443b573d979cee67253ba06d84b8605a39c28036b39ead180238`
- Parallel 8K raw receipt SHA-256:
  `fada841cf9b31813b386f48c4d3d3fa2b737dae6c81d44968b2df509bdeabb44`
- Instrumented 524K raw receipt SHA-256:
  `fa1e6383f7a1fce7167230b48403526ccfca75cd0d4d0d0321d0325686ab5883`

Canonical external runs are under
`D:\Research_Engine\runs\asmp8_rust_audit_throughput_*`.
