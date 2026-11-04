# ASMP-9 v0.34.1 engineering-smoke result

## Status

**Choice-surface smoke passed; GPU-memory accounting required amendment before
the full pilot.**

The no-thinking chat prefix repaired the v0.34 answer-alphabet failure. Across
six prompts and two planned cold starts:

```text
records accepted                         12/12
query types                              3/3
choice vectors exactly {A,B}             12/12
maximum cold-start probability delta     0
maximum cold-start target-log-odds delta 0
server sessions                          2/2
cleanup                                  passed
GPU memory after cleanup                 0 MB
```

The standard-gamble, compound-lottery, and policy-probe prompts all produced
finite A/B probabilities. The smoke is too small and deliberately lacks the
grid coverage needed for scientific analysis.

## Resource receipt issue

The Job Object enforced the aggregate 2,048 MB RAM and 50% CPU caps, and the
run stayed below 1,328 MB peak private memory. However, the wrapper's
PID-specific `nvidia-smi --query-compute-apps` path reported a false peak of
zero GPU MB even though the GPU temperature changed. That makes the
registered 1,600 MB VRAM gate unverifiable on this CUDA/llama.cpp build.

The full burned pilot therefore remained closed. Version v0.34.2 replaces the
PID query with a fail-closed whole-device delta:

```text
require device memory <= 64 MB before launch;
record baseline whole-device memory;
abort when whole-device memory - baseline > 1,600 MB.
```

An unrelated GPU process beginning during a run can only cause a conservative
abort; it cannot create a false pass.

## Local receipt hashes

```text
b2d80e207cfd680af49f4b64b968b7fca122ede7fd6d8c3f49fd859245d6d29d  summary.json
73906c82e29b2be6bdfa58f687da382201d172f1b86cff6f49899206e164addf  pilot_records.jsonl
07815a5f0330648d3d796b9dd0a1fb3f5f1c4f940ea15ad1170e5c19431f3cc7  wrapper/summary.json
0cb81f46456b7e633d1320b16c1df386d6e00b7d20d5a3f1738197c8534f0b67  wrapper/cleanup_summary.json
```

Local run directory:

```text
D:\Research_Engine\runs\asmp9_physical_acquisition_smoke_v0_34_1_20260729
```

## Claim boundary

This smoke validates prompt formatting, receipt completeness, cold-start
repeatability on six prompts, and owned-process cleanup. It is not burned-pilot
calibration or confirmation evidence and does not resolve ASMP-9.

