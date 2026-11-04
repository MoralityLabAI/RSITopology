# ASMP-8 Audit-Throughput Sample v0.1

## Result

A bounded CPU sample estimates **1.0504 model-forward audit proxies per
second** for the current prompt distribution. The estimated steady-state time
for 500,000 such audits is **5.51 days**; the corresponding estimate for the
registered Hoeffding crossing at 524,288 audits is **5.78 days**.

This is a capacity-planning result, not an ASMP-8 scientific gate.

## Measurement

- Model kernel: Qwen3.5 0.8B, Q4_K_M, 752,393,024 parameters.
- Runtime: llama.cpp build 10064, CPU backend.
- Hardware: Intel i5-11400H, six benchmark threads.
- Work unit: one 128-token prompt evaluation, no generation.
- Trials: 10 after the benchmark's internal warmup.
- Mean prompt length in the frozen 576-prompt controller manifest:
  127.1684 tokens.
- Mean 128-token trial time: 0.958233 seconds.
- Trial-time standard deviation: 0.070264 seconds.
- Prompt-processing throughput: 134.237 tokens/second.
- Length-adjusted time per audit proxy: 0.952008 seconds.
- Length-adjusted throughput: 1.050412 audits/second.
- Descriptive 95% Student-t interval for mean time per audit:
  [0.902071, 1.001945] seconds.

The interval describes timing variation across ten repeated kernel trials. It
does not cover workload drift, contention, model changes, or the difference
between this Q4_K_M CPU path and the intended NF4 GPU path.

## ETA

| Audit count | Point ETA | Timing-sample interval |
| ---: | ---: | ---: |
| 31 | 29.5 seconds | — |
| 64 | 60.9 seconds | — |
| 8,192 | 2.17 hours | 2.05–2.28 hours |
| 500,000 | 5.51 days | 5.22–5.80 days |
| 524,288 | 5.78 days | 5.47–6.08 days |

The completed ASMP-8 v0.5 experiment does **not** require an LLM forward pass
per audit: its finite-registry audits are exact table operations. These ETAs
apply only to a future model-bearing audit loop in which every audit invokes a
full Qwen forward evaluation.

## Resource and cleanup receipt

The Windows Job Object enforced a 2,048 MiB aggregate host-memory cap and 50%
hard CPU cap. The wrapper observed:

- peak RAM: 609.402 MiB;
- average RAM: 465.130 MiB;
- peak I/O: 10.267 MiB/s;
- average machine CPU share attributed to the process: 24.695%;
- peak GPU allocation: 0 MiB;
- elapsed cold-wrapper time, including load, trials, and cleanup: 27.638
  seconds; and
- cleanup: passed, with no lingering owned process and zero GPU memory after
  cleanup.

## Provenance

- Run specification SHA-256:
  `80d93c616dc422518711e102c55f25bd23672d23ea2b2e084ef2156c16431451`
- Raw benchmark JSON SHA-256:
  `27ccc0ef954f04d973ef58a075970ba2cc83860fbe908f82fa9aef707c2b7f88`
- Wrapper summary SHA-256:
  `9348f7ead1d39fecb6762bac72b6df346cd681f63e07cec2c67c1a1850e5d605`
- Cleanup summary SHA-256:
  `b88a30c494a7a4c3a863d984fb1c377f4a2bdabbc0438b93739a4eb103c54d99`

Canonical external run directory:
`D:\Research_Engine\runs\asmp8_qwen08_audit_throughput_sample_v0_5`.

## Loader boundary

Before this fallback, bounded Hugging Face attempts failed before inference:
the 2 GiB NF4 path raised Windows error 1455 while mapping the checkpoint, and
the 4 GiB NF4/FP16 paths exited during model loading. No throughput estimate
was taken from those failed runs. The successful Q4_K_M CPU result is therefore
an empirical fallback estimate, not a claim about the failed NF4 GPU runtime.
