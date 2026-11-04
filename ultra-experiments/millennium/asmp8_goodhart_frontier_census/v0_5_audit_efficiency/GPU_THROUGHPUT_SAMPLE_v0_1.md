# ASMP-8 provisional GPU-throughput sample v0.1

## Outcome

A completed single-stream CUDA sample estimates **23.985 model-forward audit
proxies per second** on the local Qwen3.5 0.8B Q4_K_M model. This is a
**22.83× speedup** over the matched CPU Q4_K_M estimate.

The result is useful for capacity planning but is not a scientific gate. The
planned multi-stream batch sweep is unavailable because the host restarted
unexpectedly during the surrounding batch-test window.

## Measurement

- Runtime: CUDA-enabled llama.cpp build 10064.
- GPU: NVIDIA RTX 3050 Laptop GPU.
- Model: Qwen3.5 0.8B Q4_K_M, 752,393,024 parameters.
- Work unit: one 128-token prompt evaluation, no generation.
- Frozen manifest mean: 127.1684 tokens per audit.
- Repetitions: 10 after internal warmup.
- Mean 128-token trial: 0.04196475 seconds.
- Trial standard deviation: 0.00778971 seconds.
- Length-adjusted mean: 0.04169211 seconds/audit.
- Throughput: 23.98535 audits/second.
- Descriptive 95% Student-t interval: 21.17–27.66 audits/second.

## ETA

| Audits | Point ETA | Timing-sample interval |
| ---: | ---: | ---: |
| 31 | 1.29 seconds | — |
| 64 | 2.67 seconds | — |
| 8,192 | **5.69 minutes** | 4.94–6.45 minutes |
| 500,000 | **5.79 hours** | 5.02–6.56 hours |
| 524,288 | **6.07 hours** | 5.27–6.88 hours |

These estimates assume one full prompt evaluation per audit. The sealed ASMP-8
finite-registry experiment does not require model inference per audit.

## Resources and instrumentation

The successful single-stream wrapper reported:

- peak host RAM: 1,317.469 MiB;
- average host RAM: 653.777 MiB;
- peak I/O: 7.030 MiB/s;
- average machine CPU share attributed to the process: 1.779%;
- cleanup: passed; and
- no lingering owned process.

Per-process VRAM telemetry returned zero under Windows WDDM even though the
benchmark identified and used the CUDA backend. The registered VRAM ceiling
therefore was not independently measured by this wrapper and must not be
reported as a verified peak.

## Stability stop

Windows records an unexpected restart (`Kernel-Power` event 41, followed by
event 6008) during the batch-test period. There were also earlier unexpected
restarts on the same day. This temporal overlap does not establish that the
benchmark caused the restart, but it is sufficient to stop further GPU stress
testing. The 1/2/4/8 parallel-prompt sweep remains `not_run_system_stability`.

## Provenance

- Run specification SHA-256:
  `918580772f022e1d509dd6f54e5a6750b529ce2effb189d000a75fe960e834ac`
- Raw CUDA benchmark SHA-256:
  `322587090c2378e90817b24fcefb1bdc854f3463b1368f69fe23e33ff03915fc`
- Wrapper summary SHA-256:
  `c7a50cca244b7ed35b18c96fc0d078472ec015c3fc57f91c528013e6b44b9665`
- Cleanup summary SHA-256:
  `1adb9dcd8bce0ed14faf7c2969d67dddd6475313ec134eadce3c60fe5e628c45`

Canonical external run:
`D:\Research_Engine\runs\asmp8_qwen08_cuda_throughput_single_v0_1`.

## Claim boundary

This is a Q4_K_M CUDA prompt-kernel timing result. It is not an NF4 result, a
human-audit rate, a persistent-server throughput result, a completed batching
sweep, or evidence about ASMP-8.
