# ASMP-8 guarded GPU batch scaling v0.2

## Outcome

Guarded CUDA scaling completed through four parallel 128-token prompts. Both
claim-eligible guard runs passed their frozen completion conditions:

- maximum observed temperature: 67 C;
- maximum observed power: 23.11 W;
- final GPU-memory delta: 0 MiB;
- wrapper cleanup: passed; and
- new display, WHEA, or kernel-power errors during either run: zero.

The warm two-prompt and four-prompt measurements were 33.06 and 32.71 audit
proxies per second, respectively, a 1.07% spread. Four-way batching therefore
did not materially improve throughput over the warm two-way result on this
prompt-only kernel.

## Measurements

| Rung | Time | Throughput | Guard result | Max temperature |
| --- | ---: | ---: | --- | ---: |
| 2 prompts, v0.1 | 0.392871 s | 5.09/s | instrumentation failure; model run completed | 66 C |
| 2 prompts, v0.2 | 0.060489 s | 33.06/s | pass | 67 C |
| 4 prompts, v0.1 | 0.122280 s | 32.71/s | pass | 67 C |

The first two-prompt timing is retained because it shows a substantial cold or
unboosted-path penalty. It is not pooled with the warm measurements. Its model
process exited 0 and cleanup passed, but the outer guard originally received a
null child exit-code field. The guard was amended to recover that field from
the independently written wrapper receipt, and the same two-prompt rung was
repeated before escalation.

## Planning ETA

Using the four-prompt point measurement:

| Audit proxies | ETA |
| ---: | ---: |
| 8,192 | 4.17 minutes |
| 500,000 | 4.25 hours |
| 524,288 | 4.45 hours |

These are steady prompt-kernel estimates, not end-to-end audit estimates.
Tokenization, persistent-server behavior, generation, feature extraction,
scoring, serialization, and queueing are outside the measurement.

## Resource boundary

The two successful completion-gated runs stayed far below the 78 C hard abort.
The four-prompt run observed at most 565 MiB of VRAM at the 500 ms sampling
cadence and 322.8 MiB peak host RAM through the job-object wrapper. These are
sampled observations, not certified continuous-time peaks; Windows WDDM does
not expose a reliable per-process VRAM maximum through the existing wrapper.

No eight-prompt rung was attempted. A ten-repetition four-prompt spec was
frozen to estimate variance without increasing width, but a separately owned
`llama-server` process then occupied the GPU. During that external job the GPU
reached 81 C with about 519 MiB resident. The repeated sample was therefore
recorded as `not_run_shared_gpu_occupied`; the external process was not
terminated or modified.

## External receipts

Canonical run directories:

- `D:\Research_Engine\runs\asmp8_qwen08_cuda_throughput_npl2_guarded_v0_1`
- `D:\Research_Engine\runs\asmp8_qwen08_cuda_throughput_npl2_guarded_v0_2`
- `D:\Research_Engine\runs\asmp8_qwen08_cuda_throughput_npl4_guarded_v0_1`

Selected SHA-256 receipts:

- amended guard script used by the two-prompt v0.2 and four-prompt v0.1 runs:
  `a41158e48a45f412af1fcce472ec32808636deb1f103a61d765f0602d525d8e6`
- two-prompt v0.2 guard summary:
  `e6b82a61d8a13dba77c6905e7105a67bcc2f306a720ebdad9c04e446a57d46a3`
- two-prompt v0.2 raw benchmark:
  `f1d9fc1cabbe3b00d5fc68939c76158820ebddb4dc2a947a0a0896e9a08018ef`
- four-prompt v0.1 guard summary:
  `b765853ca62a6734234c43539c84dc705d13e4adc03316dc0a7747bd1e5ba617`
- four-prompt v0.1 raw benchmark:
  `68c9fcd415a415f86a78104c16ec71d17f834ed0a7835271c60a5cabf4d64002`

The pre-amendment guard source used for the two-prompt v0.1 run was not hashed
before its nullable exit-code defect was repaired. That timing is descriptive
only. Its model output, wrapper receipt, cleanup receipt, and guard output
remain separately hashable in the external run directory.

## Claim boundary

This is descriptive Q4_K_M CUDA prompt-processing throughput on one local
RTX 3050 Laptop GPU. It is not a persistent-server benchmark, a generation
benchmark, an NF4 comparison, a human-audit rate, or evidence about ASMP-8.
The sealed finite-registry ASMP-8 experiment itself does not require one model
forward pass per audit.
