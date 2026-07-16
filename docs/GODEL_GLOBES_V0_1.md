# Gödel Globes v0.1: real-model identity geometry

## What changed

This protocol incorporates the harness upgrades that predate the original
falsification memo. It does not reconstruct the identity stack from scratch.
It consumes:

- the v0.3 cross-fitted between-class-scatter object and label-permutation
  null;
- the mandatory instrument-calibration cap in `AnchorRegistry.certify`;
- the lineage-first `beta_1` bifiltration;
- the existing holonomy, edit-sectioning, persistence, audit-placement, and
  attestation implementations; and
- the existing three-level consumer policy. No fourth invariant was added.

The old proposal of using adjacent layers as the loop axis is retired. The
measured EM-pair receipts showed median adjacent-layer worst-direction
retention near `0.003`, so that graph has no usable depth ladder. The registered
real grid is now runtime precision × context shard at a fixed physical site
and behavior family.

The archived Silico planted-reward run is calibration only. It found a sharp
runtime boundary: same-precision float32 coordinates realized at all three
registered sites, while bfloat16 did not. That finding motivated
`full_float32` and `full_bfloat16` as the two shells. It is not counted as a
result from this protocol. Its independently retrieved hashes, negative
transport result, resource observation, and non-consumption policy are recorded
in `reports/godel_globes_silico_calibration_anchor.json`.

## Frozen inputs

- Protocol: `protocols/godel_globes_falsification_v0_1.json`
- Prompt manifest: `protocols/godel_globes_prompt_manifest_v0_1.json`
- Protocol SHA-256: `df06540a6428ad57c307f21671682ba5a3fe687cb2d543424ad052c258be514b`
- Prompt-manifest SHA-256: `19dc2bbe38ab959036ab1e437e10536e0b4dec12792afccf7134d17ffc865794`
- Model: `Qwen/Qwen3-1.7B`, revision
  `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`
- Sites: `model.layers.16` through `model.layers.27`,
  `self_attn.v_proj`
- Families: affine recurrence, symbol transport, grid rotation, and graph
  reachability
- Prompt design: nine family subconditions, eight context shards, two
  construction and two independent geometry-validation prompts per cell;
  1,152 prompts total

Expected answers are sealed generator checks. Identity construction never
reads model answers or expected-answer cells.

## Data path

The live capture writes one NPZ chunk per
`runtime × site × shard × half`. Each chunk contains exactly one finite matrix
named `activations`; prompt order lives in the sealed capture index. The
captured vector is the registered `v_proj` output at the final non-padding
prompt token. Generation, gradients, scoring, interventions, and weight writes
are prohibited.

The analyzer then:

1. evaluates ranks 1–8 with one shared bootstrap/permutation run;
2. finds the largest rank supported at every node of each runtime grid;
3. reports `runtime_specific_identity` if only one precision arm survives;
4. constructs adjacent-shard and same-shard cross-precision transports;
5. filters edges at the frozen lineage floor and computes `beta_1`;
6. measures only admitted elementary loops on the held-out half;
7. compares loop closure against prompt-resampling and flat/noise controls;
8. produces patch plans, persistence curves, audit rankings, anchor records,
   and use-specific certificates; and
9. exports the existing Gödel Globe JSONL contract.

The two-row strip cannot distinguish an area law from a perimeter law because
`perimeter = 2*area + 2`. The analyzer reports that calibration as
`not_identifiable_on_two_by_n_strip` instead of fitting a decorative
regression.

## Commands

Regenerate the frozen prompt manifest (write-once):

```powershell
python scripts/run_godel_globes_v0_1.py generate-prompts `
  --output protocols/godel_globes_prompt_manifest_v0_1.json
```

Create and analyze a synthetic contract fixture:

```powershell
python scripts/run_godel_globes_v0_1.py make-smoke-capture `
  --prompt-manifest protocols/godel_globes_prompt_manifest_v0_1.json `
  --output-dir D:\godel-smoke\capture --ambient-dimension 24 --planted-rank 8

python scripts/run_godel_globes_v0_1.py analyze `
  --prompt-manifest protocols/godel_globes_prompt_manifest_v0_1.json `
  --capture-index D:\godel-smoke\capture\capture_index.json `
  --output-dir D:\godel-smoke\release

python scripts/run_godel_globes_v0_1.py verify `
  --prompt-manifest protocols/godel_globes_prompt_manifest_v0_1.json `
  --capture-index D:\godel-smoke\capture\capture_index.json `
  --release-dir D:\godel-smoke\release
```

Open `godel-globe/index.html` and load the release's edge, loop, certificate,
and calibration files together.

## Live-capture authorization

`scripts/capture_godel_globes_qwen.py` refuses to run without a write-once
authorization binding the exact protocol and prompt bytes, explicit RAM/CPU/
I/O/timeout/GPU/swap caps, a passed hard-cap validation receipt, and the
registered cleanup script. The capture loads float32 and bfloat16 sequentially,
checkpoints every shard/half group, records structured events, and explicitly
releases model objects and CUDA memory.

The repository's current resource audit still blocks an uncapped local
promotion run. A Research_Engine/SLURM or other wrapper may supersede that
block only by supplying a new machine-readable passed validation receipt. The
analysis and synthetic tests are CPU-only and do not require that authorization.

Once such a wrapper has passed, prepare the write-once authorization with
explicit values (there are deliberately no live defaults):

```powershell
python scripts/run_godel_globes_v0_1.py prepare-authorization `
  --run-id <run-id> `
  --prompt-manifest protocols/godel_globes_prompt_manifest_v0_1.json `
  --hard-cap-wrapper <wrapper.ps1-or-sh> `
  --hard-cap-validation-receipt <passed-receipt.json> `
  --cleanup-script <post-run-cleanup.ps1> `
  --memory-mb <cap> --host-reserve-mb <reserve> `
  --cpu-percent <cap> --io-mb-s <cap> `
  --timeout-seconds <cap> --gpu-allowance-mb <cap> `
  --checkpoint-every-seconds 300 --swap-bytes 0 --confirm-caps `
  --capture-output-dir <capture-dir> --device cuda --batch-size <size> `
  --output <capture-authorization.json>
```

For the registered local CPU lane, the current proposed envelope is 14,000 MB
job memory plus a 2,048 MB host reserve, 50% CPU, 50 MB/s monitored I/O, a
12-hour timeout, 1 MB GPU allowance, durable checkpoints at most 300 seconds
apart, and zero registered swap. The wrapper refuses to start unless free
physical RAM is at least `memory_mb + host_reserve_mb`; recording
`swap_bytes=0` alone is not treated as a Windows no-pagefile guarantee.

The authorization is itself the Job Object run spec. Launch it only through:

```powershell
powershell -NoProfile -File scripts/run_qwen_holonomy_jobobject.ps1 `
  -RunSpecPath protocols/godel_globes_capture_authorization_v0_1.json
```

The passed validation receipt must bind the exact wrapper and cleanup-script
hashes used by the authorization. A receipt for an earlier wrapper revision is
invalid even when its top-level status says `passed`.

## Interpretation

- `beta_1 = 0` means holonomy is structurally unavailable, not that curvature
  was measured as zero.
- A float32-only result cannot authorize bfloat16 rewards or edits.
- A failed family co-rotation bet yields separate family Globes; it does not
  invalidate per-family certificates.
- Too many patches switches the viewer to hierarchical navigation; it is not a
  scientific rejection.
- Signed intervention, signed reward, and disparate weight edit still require
  `holonomy_clean`. Bundle energy requires `lineage_certified`.
- Causal edit value remains in the separately frozen patchwise VPD P2 holdout.
