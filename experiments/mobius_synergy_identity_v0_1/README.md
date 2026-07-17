# Möbius Synergy Identity v0.1

This experiment asks whether a product-poset Möbius transform extracts a more
stable identity object than the between-class-scatter object that returned no
supported rank in the Gödel Globes Qwen3-1.7B run.

It is deliberately a separate experiment. It does not amend the Gödel Globes
protocol, relax its negative-control gate, or add an invariant above holonomy.

## Mathematical object

For a two-factor condition grid with hidden-state cell means `z[a,b]`, the
local product-poset Möbius coefficient is

```text
q[a,b] = z[a,b] - z[a-1,b] - z[a,b-1] + z[a-1,b-1].
```

The first-order effects of each factor cancel. The rows of `q` across context
shards and adjacent plaquettes define a candidate interaction subspace. Bases
are constructed independently on the frozen construction and
geometry-validation halves. Their worst principal-angle retention is compared
with a factor-label permutation null.

## Existing factorial grids

The completed activation capture already contains three eligible objects:

- `graph_reachability`: path length × distractor count (3×3);
- `grid_rotation`: quarter turns × grid size (3×3);
- `affine_recurrence`: multiplier sign × offset sign (a frozen 2×2 subset).

`symbol_transport` has no registered product-factor grid and is excluded.

## Confirmatory claim

The sole claim-eligible target is:

```text
runtime = full_float32
site = model.layers.22.self_attn.v_proj
family = graph_reachability
```

Ranks 1–8 are selected inside the gate using a permutation max statistic over
all ranks. The target passes only if at least one rank has

```text
bootstrap lower-95 retention - permutation max-statistic upper-95 > 0.02.
```

The BF16 version of the same target is a precision replication. Every other
runtime × site × family result is exploratory and cannot rescue a failed
target.

An eight-replicate engineering smoke was run on the target before the
machine-readable registration was written. It exposed ranks 1–2 and is
therefore disclosed in the protocol. The target, rank universe, null, margin,
and full 128-replicate decision rule were all left unchanged. The full result
is best described as a registered analysis after a disclosed engineering
pilot, not as an untouched preregistration.

## Nulls and claim boundary

- Factor-label permutations are applied before the Möbius transform.
- Construction and validation bases are always estimated separately.
- Permutation maxima control rank selection within each grid.
- Expected answers and model outcomes are never loaded.
- A supported synergy rank is representation evidence, not causal evidence.
- No lineage graph or holonomy claim is made by this phase. Those require a
  supported object and a separately registered transport experiment.

## Workflow

From the repository root:

```powershell
python experiments/mobius_synergy_identity_v0_1/run.py register `
  --capture-index D:\Research_Engine\runs\godel_globes_qwen17_capture_v0_2\capture_index.json `
  --prompt-manifest protocols/godel_globes_prompt_manifest_v0_1.json `
  --output experiments/mobius_synergy_identity_v0_1/registration.json

python experiments/mobius_synergy_identity_v0_1/run.py analyze `
  --registration experiments/mobius_synergy_identity_v0_1/registration.json `
  --output-dir D:\Research_Engine\runs\mobius_synergy_identity_v0_1
```

For a bounded engineering check that cannot support scientific claims:

```powershell
python experiments/mobius_synergy_identity_v0_1/run.py smoke `
  --capture-index D:\Research_Engine\runs\godel_globes_qwen17_capture_v0_2\capture_index.json `
  --prompt-manifest protocols/godel_globes_prompt_manifest_v0_1.json `
  --output-dir D:\Research_Engine\runs\mobius_synergy_identity_smoke_v0_1
```

Run the synthetic controls with:

```powershell
python -m pytest experiments/mobius_synergy_identity_v0_1/test_mobius.py -q
```

## Provenance-only v0.1.1 amendment

The original v0.1 protocol and registration remain byte-for-byte unchanged.
`protocol_v0_1_1_amendment.json` adds no scientific gate and changes no target,
rank, null, or margin. It requires exact validation of every indexed activation
chunk, a sealed analysis environment, and an atomic write-once release. The
claim-eligible run must use `run_v0_1_1.py` and its separately sealed
`registration_v0_1_1.json`; the earlier `run.py analyze` command is retained
only to reproduce the registered v0.1 implementation and must not be used for
the claim release.

## Provenance

The transform is motivated by Abel Jansma's *A Compositional Calculus for
Semantic Synergy in Language Model Embeddings* and its public reproduction:
<https://github.com/AJnsm/semantic_synergy_data>. This implementation is
independent and applies the product-poset transform to internal activations and
identity stability rather than idiom classification.
