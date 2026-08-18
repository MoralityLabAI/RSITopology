# ASMP-11 real-model access-ladder execution preflight v0.3

## Disposition

The proposed learned conditional-defection/access-ladder run is **NO-GO on
this host under the required safety contract**.  The preflight stopped before
loading model weights, starting WSL, creating adapters, or training.

This is a negative feasibility attempt for the current execution environment.
It does not test the scientific access-ladder hypothesis and does not resolve
ASMP-11.

## Frozen target and safety gate

The target design was a sequential local run using
`Qwen3.5-0.8B-Instruct`, eight independently seeded matched LoRA triples, and
three frozen access classes.  The experimental unit would be one independently
trained adapter seed; repeated prompt rows would not be treated as independent
units.

Before any model-bearing smoke, the safety gate required proof of all three
default hard caps from the local-training contract:

```text
RAM: 2,048 MiB
CPU: 50 percent
I/O: 50 MiB/s
```

Training task id, if later authorized, is
`asmp11-real-model-access-v0.3`; the proposed chunk is one adapter at a time,
with checkpoints every 32 optimizer steps or five minutes, whichever comes
first.  Aborts are valid outcomes.  Model objects and CUDA allocations would
require explicit `finally` cleanup and a PID-scoped post-run audit.

## Cap-path evidence

No inspected path establishes all three hard caps:

1. WSL 2.7.11.0 is installed, but its only `Ubuntu` distro was stopped and was
   not started.  `C:/Users/patri/.wslconfig` is VM-global with `memory=12GB`
   and `swap=32GB`; changing or applying it would affect shared WSL state.
   The repository's last verified WSL audit reports delegated `memory` and
   `pids` only, with CPU quota ignored and I/O unavailable.  The current WSL
   wrapper correctly refuses work unless memory, CPU, and I/O are all
   delegated.
2. No Docker CLI, daemon, executable, or service was found.
3. The Windows Job Object wrappers implement and query hard RAM and CPU caps,
   but only sample I/O once per second and kill after three consecutive
   breaches.  Their own validator calls this monitored fail-closed I/O, not a
   hard throttle.  Repository-wide search found no
   `SetIoRateControlInformationJobObject` implementation or equivalent.
4. The current Qwen Job Object wrapper has SHA-256
   `ba19b659e0d9bd763239737f26b83cf4b8b48046f4c35ea17dd6520499e3be66`;
   it matches no passed receipt hash and its schema allowlist does not include
   ASMP-11.

Relevant committed local evidence includes `TRAINER_PLAN.md`,
`reports/resource_enforcement_audit.md`,
`scripts/run_capped_discovery_wsl.sh`,
`scripts/run_qwen_holonomy_jobobject.ps1`, and
`scripts/validate_qwen_holonomy_jobobject.ps1`.

## Checkpoint and environment evidence

Checkpoint root:

```text
D:/Research_Engine/models/Qwen3.5/Qwen3.5-0.8B-Instruct
```

Fresh read-only bindings passed:

| object | bytes | SHA-256 |
|---|---:|---|
| numbered weight shard | 1,746,942,600 | `04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696` |
| `config.json` | - | `b90b86f35c8e6925ef74ee04d0e758f0a845c83a42089ad82bbaa948de9b4204` |
| `tokenizer.json` | - | `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42` |
| weight index | - | `d8a08838a613b025eb7952ed9db11696213e57e76a375661ef5c12f9dd5dcf4e` |

All 488 index entries point to the numbered shard.  `model.safetensors` and
the numbered shard are hard-link names for the same content.  The checkpoint
alone occupies 1,666.014 MiB, leaving only 381.986 MiB below the 2,048 MiB
RAM cap before tokenizer, Transformers, activations, optimizer, or adapter
state.

The host GPU was an idle RTX 3050 Laptop GPU with 4,096 MiB VRAM, driver
555.99, CUDA 12.5, zero reported compute processes, and temperature about
52 C.  No CUDA context was created.

Non-isolated package metadata reported Python 3.11.4, torch 2.5.1+cu121,
Transformers 5.3.0, safetensors 0.6.2, PEFT 0.11.1, Accelerate 1.12.0, and
bitsandbytes 0.49.1.  `pip check` already reports multiple conflicts,
including `sentence-transformers 5.1.0` requiring `transformers<5`.  The
required isolated-Python dependency probe also failed because PEFT is visible
only from the user site excluded by `python -I`.

## Decision rule and next authorization

The hard-cap gate failed, so the correct action was to stop before the
model-bearing smoke.  A future attempt requires either:

- a dedicated, owned WSL/systemd cgroup scope with validated memory, CPU, and
  block-I/O controllers; or
- a Windows wrapper with genuine OS I/O throttling and a fresh receipt bound
  to its current source.

That path must first pass a model-free cap probe.  Any model run must then use
a fully bound isolated environment, explicit checkpointing, structured
JSON/JSONL abort logs, PID-scoped cleanup, and a post-run CUDA/DRAM audit.

## Scientific claim boundary

No model output, training behavior, detector AUC, obfuscation effect, causal
ablation, or access-ladder contrast was observed.  This preflight says only
that the proposed real-model attempt was not safely executable on the current
host under the frozen default caps.  Existing ASMP-11 evidence therefore
remains transparent-parity-only, and the scientific real-model successor
remains open even though its current-host feasibility has now been tested to
a negative result.
