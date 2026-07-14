# Resource-Enforcement Audit

## Verdict

No current wrapper enforces all three required hard caps. Further large-matrix,
model-bearing, training, or weight-loading runs are blocked until the host gains
an approved enforcement path.

## Evidence

- Windows Job Object run `jspace-operator-bridge-d32-l6-20260711` observed
  `1303.129 MB` private memory under a declared `1024 MB` limit without an OS
  termination. The run is invalidated. The independent watchdog was then added.
- Windows probe `cap-probe-128mb-20260711` was terminated by the watchdog, not
  by the Job Object. This is fail-safe behavior, not a hard-cap proof.
- WSL probe `wsl-cap-probe-64mb-v2-20260711` produced systemd result `oom-kill`
  under `MemoryMax=64M` and `MemorySwapMax=0`; the memory controller is valid.
- WSL probe `wsl-cpu-probe-25pct-20260711` consumed approximately 94% of one CPU
  despite `CPUQuota=25%`. The user manager's `cgroup.subtree_control` contains
  only `memory pids`, so CPU and I/O settings are not delegated.
- Docker is not installed. Passwordless system-level `sudo` is unavailable.

The WSL wrapper now checks delegation before launch and exits with status 3 if
`memory`, `cpu`, and `io` are not all available. It cannot silently fall back to
soft limits. Existing small unit tests remain permitted; they do not load model
weights or execute large registered experiments.

## Required external change

One of:

1. delegate CPU and I/O controllers to the WSL user manager;
2. provide a root-owned systemd wrapper with the registered limits; or
3. install an approved container runtime with memory, CPU, swap, and block-I/O
   limits.

Changing shared WSL configuration or installing privileged infrastructure is
not performed without explicit user authorization.

## Prepared remediation (not applied)

`wsl_cgroup_delegation_runbook.md` documents a guarded systemd delegation path.
The installer requires root plus a literal confirmation token, verifies unified
cgroup v2, preserves a conflicting drop-in, and deliberately does not restart
WSL. The accompanying verifier is read-only. This preparation does not alter
the verdict: promotion runs remain blocked until the host change is explicitly
authorized and all three controller probes plus cleanup validation pass.
