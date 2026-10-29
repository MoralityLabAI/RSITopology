# Qwen 500,000-audit launch abort v0.1

## Outcome

The model-forward 500,000-audit run did not start. Its detached launcher waited
for the frozen cool-state and free-memory gates, but Windows restarted
unexpectedly before those gates passed.

- Last launcher event: `2026-07-23T22:21:01.1530358Z`.
- New Windows boot: `2026-07-23T18:22:29.5000000-04:00`.
- Recorded events after boot: Kernel-Power 41 and EventLog 6008.
- Last prereboot launcher sample: 73 C, 0 MiB GPU memory, zero CUDA compute
  processes, and 8,720 MiB free physical RAM.
- Corrected probability smoke started: no.
- Full model-forward run started: no.

The restart occurred while the launcher was only polling resource state. This
does not show that the proposed Qwen run caused the restart. It does show that
the host is not presently stable enough for a guarded eight-hour GPU job.

The frozen consequence is:
`do_not_launch_gpu_500k_until_host_stability_is_remediated`.

## What did complete

The CPU-only ASMP-8 reduction completed 500,000 audits per stream over 1,024
streams, for 512,000,000 total synthetic audit draws. The first eight-request
Qwen server smoke also completed before the queued launch was created, but its
token-probability parser required the prospectively recorded v0.2 amendment.
The amended smoke never ran because of the later resource gate and restart.

## Receipts

Runtime launcher receipt:
`D:\Research_Engine\runs\asmp8_qwen08_completion_audits_500k_v0_1\launcher\launcher_summary.json`

Launcher-summary SHA-256:
`f04ba8133da5ef4185ca4093d18c01560acca2e1b5634ee3b47b51dd9836684d`

## Claim boundary

This is a host-stability abort receipt, not a model result, an ASMP-8 result,
or evidence that the proposed workload caused the restart.
