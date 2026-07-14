# Qwen3-1.7B one-prompt host preflight

The original RSITopology-only preflight incorrectly assumed WSL was the only
approved execution path. Research_Engine already provides the active
Windows-native path and is now the source of truth.

The official Qwen3-1.7B revision and weight shards are present under
`D:\Research_Engine\Qwen_Storyworld\cache\models`. Its Windows Job Object
wrapper has validated memory and CPU policy fields, streamed 4-bit/BF16
loading, per-component checkpoints, I/O monitoring, and PID-scoped cleanup.
A completed preflight stayed within its registered caps and cleanup passed.

The multivariant canary subsequently passed its three-sample launch gate and
completed. Selection was reused from a completed 96-checkpoint run, the
registration was sealed, and the estimator completed all 384 registered
checkpoints without a cap breach. Its peak working set was 4.19 GB and cleanup
passed.

The prereveal pipeline then stopped `noise_floor_only` before behavioral
outcomes because all 192 sites received certification level 0 in both split
halves and no level-2 null-floor site existed. Thresholds were not relaxed.
The scientific interpretation and canonical hashes are recorded in
`qwen3_1p7b_identity_prereveal_result.md` and the adjacent JSON receipt. No
duplicate continuation should be launched.

The JSON correction receipt in the adjacent artifacts directory supersedes
the WSL-only assumption below; the historical failed WSL preflight remains
preserved as provenance.

## Historical RSITopology-only attempt

Run `qwen3-1p7b-one-prompt-jspace-v01` was fail-closed before weight acquisition.

The selected CPU-heavy path uses 16 GB RAM, 50% CPU, 50 MB/s I/O, zero swap, a one-hour timeout, four JVP directions per chunk, and a checkpoint after every registered site or edge chunk.

The local GPU is an RTX 3050 Laptop GPU with 4 GB total and 2.18 GB free, so it cannot hold the official 1.7B BF16 model plus differentiable JVP workspace. CPU execution therefore requires the registered WSL cgroup path.

WSL is currently unresponsive: listing distributions, entering as root, running the delegation installer, and `wsl --shutdown` all timed out. `WslService` reports running, but this session cannot restart it because it lacks elevated Windows service permissions. No model weights were downloaded or loaded and no run-owned process was created.

Resume from an elevated Windows PowerShell:

```powershell
Restart-Service WslService -Force
wsl --shutdown
```

If the service still cannot stop, reboot Windows. After WSL responds, the already-authorized sequence is:

```powershell
wsl.exe -u root -- bash -lc "cd /mnt/c/projects/RSITopology && bash scripts/enable_wsl_cgroup_delegation.sh --confirm-host-change I_UNDERSTAND_THIS_CHANGES_SHARED_WSL"
wsl --shutdown
wsl.exe bash -lc "cd /mnt/c/projects/RSITopology && bash scripts/verify_wsl_cgroup_delegation.sh"
```

The model remains blocked until the memory OOM, CPU quota, block-I/O, zero-swap, and owned-process cleanup probes all pass.
