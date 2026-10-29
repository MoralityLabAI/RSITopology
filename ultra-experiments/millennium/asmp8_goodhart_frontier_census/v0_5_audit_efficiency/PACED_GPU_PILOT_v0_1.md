# Paced Qwen0.8B GPU audit pilot v0.1

Date: 2026-07-23

Status: **passed as an engineering pilot; not a scientific gate**

## Why this pilot exists

The unpaced 500,000-audit v0.4 run reached its independently monitored
88-degree-Celsius hard-abort threshold before its first atomic checkpoint. The
abort was a valid resource-safety result. It did not answer whether the audit
workload could run with a bounded thermal duty cycle.

Version 0.1 adds request-side pacing:

- pause new request batches when the GPU reaches 85 C;
- resume only after it cools to 80 C;
- retain the external 88 C hard abort;
- check temperature every 20 audits;
- checkpoint scientific and thermal state every 20 audits.

## Frozen pilot result

| Field | Result |
|---|---:|
| Audits | 200 / 200 |
| Probability coverage | 200 / 200 |
| Returned-probability variance | 0.0024420589349782307 |
| Effective throughput, including cooling | 5.251406587285132 audits/s |
| Thermal pauses | 5 |
| Cooling time | 25.273384199999782 s |
| Guard peak temperature | 87 C |
| Peak GPU memory | 697 MB |
| Guard status | completed |
| Cleanup | passed |

The pilot therefore passed its frozen engineering gate. At the pilot rate,
500,000 audits would take approximately 26.45 hours. The full v0.5 protocol
uses a 36-hour timeout because a 200-audit pilot cannot establish the
long-horizon thermal duty cycle.

## Bindings

- Pilot protocol SHA-256:
  `0c825e0523455c7a46df5d621b876c39c2f3a272948e54e5ad9cbbbcac5f1cb3`
- Runner SHA-256:
  `a908b10f33eddb939cf1aa3bee87c0e3a0d387d7c70a4a5425b3e11a73777a7f`
- Pilot summary SHA-256:
  `014efce84dffde13c70d3606ef7b919f9c8ecab105e0109291dab63351e92e6f`
- Guard summary SHA-256:
  `9f0a291ee1909e1b71c0e689f23217e08f33bd2e1fa94f4b5d52a3a7c3bc187f`
- Wrapper summary SHA-256:
  `8dde7bb23971dda23af0e0dc0d6155952ea3c90e44ef85526dbe8874a0c07ec9`

Canonical run directory:
`D:\Research_Engine\runs\asmp8_qwen08_completion_audits_paced_pilot_v0_1`

## Claim boundary

This is a thermal-pacing and throughput pilot. Repeated evaluations of the
same frozen 576 prompts are not independent evidence. The result neither
tests the ASMP-8 theorem statement nor licenses a claim about model oversight
quality.
