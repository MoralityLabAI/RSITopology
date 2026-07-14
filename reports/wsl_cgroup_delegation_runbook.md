# WSL Cgroup Delegation Runbook

## Status and authority boundary

This is a prepared remediation path, not an applied host change. Installing a
systemd drop-in and restarting WSL affect the shared distribution. They require
the user's explicit authorization and must not be performed as an incidental
test step. Passing the read-only verifier is also not sufficient: memory, CPU,
and block-I/O cap probes must pass before model weights are loaded.

## Preconditions

- Run from the intended WSL distribution with systemd enabled.
- Unified cgroup v2 must be mounted at `/sys/fs/cgroup`.
- Registered run data and scratch space must be on the WSL ext4 filesystem,
  not `/mnt/c` or another drvfs/9p mount. The I/O controller meters block
  devices and does not reliably constrain Windows-mounted files.
- Keep `.wslconfig` changes out of this procedure. If the verifier reports a
  hybrid hierarchy, enabling `cgroup_no_v1=all` is a separate host change that
  requires a separate review and authorization.

## Authorized installation procedure

Only after explicit authorization, from the repository inside WSL:

```bash
sudo bash scripts/enable_wsl_cgroup_delegation.sh \
  --confirm-host-change I_UNDERSTAND_THIS_CHANGES_SHARED_WSL
```

The script verifies cgroup v2, backs up a conflicting drop-in, installs the
tracked `config/wsl-user-delegate.conf`, and reloads systemd. It deliberately
does not restart WSL.

From Windows PowerShell, after saving other WSL work:

```powershell
wsl.exe --shutdown
```

Re-enter the same distribution, return to the repository, and run:

```bash
bash scripts/verify_wsl_cgroup_delegation.sh
```

The verifier exits 3 unless `memory`, `cpu`, and `io` are delegated to the user
manager and the working home is not a Windows mount.

## Mandatory post-change probes

Do not run the one-prompt benchmark immediately. First rerun the existing
strict-wrapper probes and preserve their receipts:

1. memory: confirm `MemoryMax`/`MemorySwapMax=0` produces an OS `oom-kill`;
2. CPU: confirm `CPUQuota=25%` measures near 25% of one core, not the prior
   approximately 94%;
3. I/O: confirm the registered read/write limit on an ext4-backed scratch file;
4. cleanup: confirm no owned descendant PIDs, GPU compute processes, or stale
   scopes remain.

Any missing controller, ignored limit, ambiguous termination, or cleanup
failure keeps the promotion path blocked. Only after all probes pass may the
one-prompt registration be frozen and executed under
`scripts/run_capped_discovery_wsl.sh`.
