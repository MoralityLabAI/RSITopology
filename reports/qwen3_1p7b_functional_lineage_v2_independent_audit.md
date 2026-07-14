# Qwen3-1.7B functional-lineage v2.0.1: independent artifact audit

**Audit date:** 2026-07-13  
**Audit scope:** `D:\projects\VDP\JSpace\artifacts\functional_lineage_v2\real_v3`  
**Mode:** read-only, independent replay; no source-run artifact was modified

## Verdict

The sealed primitive bundle and scientific summary are intact, mutually
consistent, and reproducible from their recorded inputs. The registered result
`noise_floor_only` is correct. No module cleared the lineage-support threshold,
all supported identity ranks remain zero, behavioral outcomes were not started,
and signed interventions remain unauthorized.

The only audit finding is a low-severity provenance/documentation inconsistency
in the external `wrapper_manifest.json`. Its generic descriptive fields do not
describe the run that its own command arguments actually launched. This does
not alter the primitive bundle, summary, input universe, replay, or scientific
decision, but it should be corrected or explicitly annotated before external
circulation.

## Artifact hashes

| Artifact | Independently computed SHA-256 | Receipt comparison |
| --- | --- | --- |
| `functional_primitives_v2.npz` | `69b6ed5c678c27283b1792807d08240af190369ea49593a1a90b96a1696ed0f5` | Exact match to `primitive_bundle_sha256` in the summary |
| `functional_lineage_summary.json` | `398d027e0fb12fdf1149e80f45ed77159b85f017f5ef7efbffd2cf78eb0c1ebe` | Independent audit hash; the summary is not self-hashed |
| Frozen protocol | `79ab8f20a8f5dab5a63de7e335ce28362f7516922e45d0e15122fb686e9ea003` | Exact match |
| Frozen v2.0.1 amendment | `388aca790095c067b7d98e1dcca3074cb572b3938bc21022b6294517fc2d8d77` | Exact match |
| Collector | `a2a6b7a6bfc802d68e1422727ee302cc52e2a52060f6c246b573b6dcbcbe0aad` | Exact match |
| Functional-lineage implementation | `17ea26caa9c2549f0f7943fda5344d72f882b896872a13a64d8c7da703b7902a` | Exact match |
| Formula-conformance runner | `cc98d06abf9b2a7f7221756c950cb24de2044f241e218f4b31b97fee8bb0266a` | Exact match |

The summary and the NPZ-embedded manifest agree exactly on the protocol,
amendment, implementation, anchor, anchor-producer, and estimator-producer
receipts. The registered C0 formula-conformance receipt is
`20cba6c8a0c90a0bbcd0023c823c6b87f3d92fc5e937e2580160e6f863c3881d`.

The audit also rehashed the complete upstream input chain:

- 288 of 288 anchor tensor files matched their sealed hashes;
- 384 of 384 estimator checkpoint files matched their sealed hashes;
- both filename universes were exact, with no missing or extra recorded input;
- all ten required producer-run receipt files matched their recorded hashes;
- the anchor-run summary hash matched exactly; and
- no missing file or hash mismatch was found.

## Primitive-bundle structure

The NPZ passed its ZIP CRC check. It contains 4,232 members with 4,232 unique
names and no duplicate archive entries. It loads with `allow_pickle=False`.

| Array family | Count | Shape per array | Type |
| --- | ---: | --- | --- |
| `signature` | 1,152 | `(12, 16)` | `float64` |
| `signature_spectrum` | 1,152 | `(12,)` | `float64` |
| `gram_diagnostics` | 1,152 | `(7,)` | `float64` |
| `projector` | 288 | `(12, 12)` | `float64` |
| `holonomy_polar` | 96 | `(1, 1)` | `float64` |
| `transport` | 384 | `(1, 1)` | `float64` |
| `threshold_null` | 3 | `(4096,)` | `float64` |
| `audit_null` | 3 | `(4096,)` | `float64` |
| `null_threshold_curve_r1_to_r8` | 1 | `(8,)` | `float64` |
| `manifest_json_utf8` | 1 | `(204941,)` | `uint8` |

All numerical values are finite except the seven intentionally unresolved
rank-2-through-rank-8 entries of `null_threshold_curve_r1_to_r8`. Those entries
are `NaN` in the NPZ and are correctly represented as `null` in the JSON
summary. No other nonfinite value was found.

The embedded geometry index contains 288 local-projector records and 96
elementary-loop records. Its 768 array references are unique and cover exactly
all stored projector, holonomy-polar, and transport arrays; there are no orphan
or missing geometry arrays.

Independent algebraic checks found:

- signature spectra reproduce with maximum error `0.0`;
- projector symmetry error `0.0`;
- maximum projector idempotence error `8.881784197001252e-16`;
- maximum rank-one trace error `1.6653345369377348e-15`;
- transport and holonomy orthogonality error `0.0` for the stored rank-one
  geometry; and
- loop polar factors reproduce from their four transports with error `0.0`.

## Independent replay

The audit recomputed all 1,152 functional signatures from the 288 sealed anchor
files and the selected sealed estimator checkpoint states using the recorded
implementation. It did not reuse the stored signature arrays as inputs to this
step.

| Recomputed object | Count | Maximum absolute error against NPZ |
| --- | ---: | ---: |
| Functional signatures | 1,152 | `0.0` |
| Signature spectra | 1,152 | `0.0` |
| Gram diagnostics | 1,152 | `0.0` |

Starting from those primitives, the audit replayed spectral-endpoint
eligibility, four-direction cross-fit retention, local projectors, edge
transports, loop holonomy, structured-conjugation nulls, familywise threshold,
rank flags, and gates.

All stored geometry and observed summary statistics reproduced exactly. A fresh
structured-null replay differed from the stored null arrays only at floating
linear-algebra roundoff: the maximum absolute array difference was
`2.393918396847994e-16`, and the rank-one threshold differed by less than
`1e-17`. These differences did not change any exceedance, threshold decision,
rank, or gate.

Using the sealed null arrays reproduces the registered quantities exactly:

- rank-one familywise threshold:
  `0.014836506490870583`;
- audit exceedances: 27 of 4,096 draws; and
- audit familywise false-support rate:
  `0.006591796875`.

## Scientific result

Only three physical modules had an eligible rank-one spectral-band endpoint.
No module had an eligible endpoint at ranks two through eight.

| Physical module | Worst-direction retention | Null threshold | Margin | Supported? |
| --- | ---: | ---: | ---: | --- |
| `model.layers.16.self_attn.v_proj` | `0.00010422520967150192` | `0.014836506490870583` | `-0.014732281281199081` | No |
| `model.layers.22.self_attn.v_proj` | `0.006695448196632646` | `0.014836506490870583` | `-0.008141058294237937` | No |
| `model.layers.27.self_attn.v_proj` | `0.000009791651159197717` | `0.014836506490870583` | `-0.014826714839711385` | No |

The registered gates therefore replay as follows:

| Gate | Result | Audit interpretation |
| --- | --- | --- |
| U0 exact factorial universe | Pass | Exact 1,152-node registered universe and producer/input checks |
| C0 formula conformance | Pass | Receipt and implementation binding valid |
| N0 matched-null holdout | Pass | Exact draw coverage; false-support rate below 0.05 |
| L0 lineage support | Fail | 0 of 12 physical modules supported |
| D0 predictor identifiability | Fail | All 12 supported identity ranks equal zero |
| H0 signed-support descriptive | Fail | 0 lineage-certified and 0 holonomy-clean modules |

Consequently, `status = noise_floor_only`, `outcomes_started = false`,
`thresholds_relaxed = false`, and `signed_interventions_authorized = false` are
the internally required conclusions.

## Low-severity wrapper-manifest caveat

The separate `wrapper_manifest.json` includes stale generic descriptive fields:

- `modules = ["model.layers.27.mlp.down_proj"]`;
- `variants = ["full"]`;
- `prompt_groups = []`; and
- `independent_split_seeds = false`.

Those fields conflict with the actual frozen design verified by U0: 12
`self_attn.v_proj` modules at layers 16 through 27, eight prompt groups, four
independent replicas, and checkpoints 1, 4, and 8. However, the manifest's
`arguments` array correctly launches the functional-lineage collector with the
frozen protocol, amendment, anchor run, estimator run, conformance receipt, and
`real_v3` output directory. The collector derives and enforces the scientific
universe from those inputs rather than from the stale descriptive fields.

This is therefore a documentation/provenance presentation defect, not evidence
of a mismatched scientific run. Before external circulation, regenerate the
wrapper manifest with accurate descriptive metadata or add a signed annotation
that identifies the stale fields and points to the verified argument list and
U0 receipt.
