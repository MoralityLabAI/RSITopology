# Capped Discovery/Training Plan

The current run is a CPU-only synthetic control, not model training. Any future
model-bearing policy or edit run must use `scripts/run_capped_discovery.ps1`
with explicit command-line limits. There are no implicit live-run defaults.

Required live-run declarations:

- `RunId`: unique training task ID;
- `MemoryLimitMB`: Windows Job Object aggregate memory cap;
- `CpuPercent`: Windows Job Object hard CPU-rate cap;
- `IoLimitMBps`: watchdog abort threshold over consecutive one-second windows;
- `CheckpointInterval`: carried into the run manifest;
- `ChunkStrategy`: carried into the run manifest and scientific receipt;
- `TimeoutSeconds`: hard wall-clock abort.

Recommended dry/synthetic values are 1024 MB RAM, 25% CPU, 20 MB/s I/O,
checkpoint after each fixture phase, candidate chunks of 64, and a 15-minute
timeout. Recommended model-bearing defaults are not authorized until the user
chooses them explicitly.

The Windows Job Object wrapper is retained as a fail-safe but failed its hard
memory-cap probe and is not approved for promotion runs. WSL2's memory cgroup
passed an OOM-kill probe, but its user service delegates only `memory` and
`pids`; CPU quota was empirically ignored and I/O is not delegated. Docker is
absent. `scripts/run_capped_discovery_wsl.sh` now refuses to run unless all
three controllers are delegated. There is currently no approved promotion-run
path; enabling system cgroup delegation (or Docker) is required. Abort/block is
a valid outcome.

A guarded remediation path is prepared in
`reports/wsl_cgroup_delegation_runbook.md`. It includes a tracked systemd
drop-in, an explicit-confirmation installer, and a read-only verifier. Nothing
has been applied to the shared WSL host. Even after delegation, the promotion
path remains blocked until separate memory, CPU, I/O, and cleanup probes pass.

The runner emits JSONL events, a JSON summary, and checkpoints. Cleanup targets
only the recorded PID tree, never process names. The cleanup receipt records
lingering owned PIDs, RAM, GPU compute applications, and top private/working-set
processes.

For high-dimensional operators, mean projectors are matrix-free and candidate
features are evaluated in registered row chunks. No full activation matrix may
be materialized. A future sparse-Laplacian backend must pass the same planted,
outcome-null, matched-rank Haar, and grouped-holdout gates before model use.
