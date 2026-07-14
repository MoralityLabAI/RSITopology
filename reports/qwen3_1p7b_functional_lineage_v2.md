# Qwen3-1.7B functional-lineage v2.0.1: registered result

**Registered outcome:** `noise_floor_only`. The completed `real_v3` run passed
the universe, formula-conformance, and held-out-null gates, but found zero
lineage-supported physical modules. Predictor identifiability therefore failed,
no finite-norm or behavioral outcomes were started, no threshold was relaxed,
and signed interventions remain unauthorized.

## Construction

V2 replaces raw overlap between weight components at different transformer
layers with a same-site functional response. For component $c$, frozen
candidate-logit probe $p$, module input $X$, output gradient $G_p$, and
VPD factors $(v_c,u_c)$, the response coordinate is

\[
S_{pc}=\sum_{t,o}G_{p,t,o}(X_tv_c)u_{c,o}.
\]

The component basis is whitened by its Frobenius Gram before the functional
subspace is measured. Comparisons are between the same physical module across
independent replica seeds and optimization checkpoints.

For fit cells $F$, let $P_v$ be the rank-$k$ local functional projector,

\[
\bar P_F=|F|^{-1}\sum_{v\in F}P_v,
\qquad V_F(k)=\operatorname{top}_k(\bar P_F).
\]

On cells $E$ disjoint in both prompt group and replica seed, v2 reports

\[
R_{F\rightarrow E}(k)=
\min_{v\in E}\lambda_{\min}(V_F(k)^TP_vV_F(k)).
\]

For every unit coordinate $a$, $x=V_F(k)a$ therefore satisfies

\[
\lVert P_vx\rVert^2\ge R_{F\rightarrow E}(k).
\]

This is an exact worst-case energy-retention bound for the first-order
functional construction. It does not prove finite-norm persistence or
behavioral prediction accuracy.

Rank authorization is attached only to spectral-band endpoints satisfying the
frozen boundary gap. This avoids treating a gauge-undefined cut through a
nearly degenerate band as a stable rank.

## Frozen design and prereveal amendment

- 12 Qwen `v_proj` modules, layers 16–27;
- eight ARC prompt groups;
- four independent VPD replica seeds, all trained on all eight registered
  prompt groups;
- checkpoints 1, 4, and 8;
- 1,152 module × prompt × replica × checkpoint nodes;
- registered, heldout, and side-effect contexts, with A–D logits used as
  unlabeled functional coordinates;
- maximum rank 8, relative spectral floor $10^{-4}$, and boundary-gap ratio
  1.25;
- 4,096 structured-conjugation threshold draws and a disjoint 4,096-draw
  audit null;
- sequence length 192; the longest observed prompt was 167 tokens, so no
  prompt was truncated; and
- signed interventions unauthorized throughout this construction protocol.

The base v2.0.0 protocol was frozen under SHA-256
`79ab8f20a8f5dab5a63de7e335ce28362f7516922e45d0e15122fb686e9ea003`.
The v2.0.1 prereveal amendment was frozen under SHA-256
`388aca790095c067b7d98e1dcca3074cb572b3938bc21022b6294517fc2d8d77`;
it records that no outcomes existed at freeze. The amendment:

1. pins both the prompt-manifest byte hash and canonical semantic hash, plus
   the actual model-shard hashes;
2. makes reciprocal cross-fit directions share one coherent conjugated
   quadrant universe within each null draw;
3. separates lineage certification from descriptive holonomy cleanliness;
4. evaluates identifiability across physical modules without multiplying by
   component count; and
5. requires complete producer, checkpoint, geometry, implementation, and
   cleanup provenance.

## Registered `real_v3` result

The following table reports the preregistered decisions, not a post hoc
interpretation.

| Gate | Result | Registered evidence |
| --- | --- | --- |
| U0: exact factorial universe | Pass | Exact 1,152-node universe; prompt, model, checkpoint, seed, context, and sequence-length checks all passed. |
| C0: formula conformance | Pass | Independent float64 receipt passed with maximum error $7.1054\times10^{-15}$ against tolerance $10^{-10}$. |
| N0: matched-null holdout | Pass | Three eligible null families, exact draw coverage, and audit familywise false-support rate 0.006591796875 (limit 0.05). |
| L0: lineage support | **Fail** | 0 of 12 physical modules had `supported_identity_rank >= 1`; the gate required at least 3. |
| D0: predictor identifiability | **Fail** | All 12 module-level supported identity ranks were 0, so no supported-rank margins were materialized. |
| H0: signed-support descriptor | **Fail / descriptive only** | 0 lineage-certified modules and 0 holonomy-clean modules. H0 could not authorize signed use in this protocol in any case. |

Only rank 1 was an eligible spectral-band endpoint for any module, and only at
layers 16, 22, and 27. Each observed worst-direction retention was below the
rank-1 familywise null threshold:

| Layer | Worst-direction retention | Mean principal retention | Null threshold | Lineage margin |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 0.0001042252 | 0.3891621938 | 0.0148365065 | -0.0147322813 |
| 22 | 0.0066954482 | 0.1703363923 | 0.0148365065 | -0.0081410583 |
| 27 | 0.0000097917 | 0.3892692893 | 0.0148365065 | -0.0148267148 |

No physical module supplied an eligible endpoint at ranks 2–8: at each such
module/rank combination, at least one of the 96 registered cells cut through
an unresolved spectral band. Those ranks were ineligible under the frozen
rule rather than counted as ordinary retention failures.

The registered decision rule maps failure of L0 or D0 to
`noise_floor_only`. The result summary additionally records
`outcomes_started: false`, `thresholds_relaxed: false`, and
`signed_interventions_authorized: false`.

## Interpretation, separate from the registered result

The result rules out the tested construction as a basis for proceeding to
finite-norm signed edits: the frozen 12-coordinate A–D/context probe did not
yield a stable, null-beating lineage rank across the registered Qwen3-1.7B
modules. Average principal retention was not sufficient; the weakest retained
direction collapsed at every admissible module. Most higher ranks could not be
posed as stable band endpoints under the registered gap rule.

It does **not** establish that Qwen3-1.7B or transformers generally lack
high-dimensional functional identity, global sections, consensus bands, or
useful edit coordinates. It does not compare causal edit utility against
matched random edits, predict control loss, demonstrate compactification, or
support an RSI claim. A different response probe, band rule, module family, or
finite-norm construction would be a new hypothesis and requires a new
preregistration rather than reinterpretation of this run.

Two data-use boundaries matter:

- Because every VPD replica was trained on all eight prompt groups, the
  prompt-and-replica cross-fit is an anchor-response holdout, not evidence of
  generalization to prompts withheld from VPD training.
- Registered heldout and side-effect contexts contributed to the functional
  construction. They are not untouched outer behavioral outcomes for later
  reuse.

Within these boundaries, the negative is informative: it distinguishes
moderate mean overlap from certifiable worst-direction identity and prevents a
first-order geometric signal from being promoted to edit authorization.

## Conformance and provenance

The amended float64 conformance receipt is SHA-256
`20cba6c8a0c90a0bbcd0023c823c6b87f3d92fc5e937e2580160e6f863c3881d`.
It covers the functional signature, Gram whitening and truncation,
band-ineligibility behavior, coherent-null reordering, exact replay,
worst-case bound, gauge invariance, holonomy angle and determinant, and the
orientation-reversal flag. Its maximum numerical error was
$7.1054\times10^{-15}$.

Primary result artifacts:

- result summary SHA-256:
  `398d027e0fb12fdf1149e80f45ed77159b85f017f5ef7efbffd2cf78eb0c1ebe`;
- reconstructible primitive bundle SHA-256:
  `69b6ed5c678c27283b1792807d08240af190369ea49593a1a90b96a1696ed0f5`;
- stage, wrapper, and cleanup SHA-256 values:
  `95486e7a21d4b999a8009593e37a1fce78fc5cecdb506cef1d748eacc20e2c2b`,
  `e5cf44366987dac1bfd6372343e1a4c17f11ee42284d4c91ee1671d06f4e8a78`,
  and `fb57844d6977ae60af9adc86b4819a7d19850739beb571607943b0f111ac94e9`;
- implementation SHA-256 values: collector
  `a2a6b7a6bfc802d68e1422727ee302cc52e2a52060f6c246b573b6dcbcbe0aad`,
  conformance runner
  `cc98d06abf9b2a7f7221756c950cb24de2044f241e218f4b31b97fee8bb0266a`,
  and functional-lineage analysis
  `17ea26caa9c2549f0f7943fda5344d72f882b896872a13a64d8c7da703b7902a`;
- prompt-manifest byte SHA-256:
  `a4f246fd30450d9cee510f93c9fc55b5605115a79ad36bb83b78c45a1b9c9db3`;
  canonical prompt-corpus SHA-256:
  `4aac9f77d9531073e9196ff0df625109cec336e046e6ce8f40db6009c716fc1d`;
- model revision `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`, with
  shard SHA-256 values
  `169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5`
  and
  `912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9`.

The released stage completed with exit code 0. The resource wrapper reports no
timeout, cap breach, wrapper exception, or cleanup failure; peak working set
was 1,559.66 MB and peak private commit was 2,389.32 MB. The cleanup receipt
records `cleanup_passed: true`. Producer receipts in the result summary also
seal the 288 anchor-chunk hashes and the anchor and estimator run summaries.

One low-severity provenance caveat remains. The analysis-stage
`wrapper_manifest.json` inherited stale generic descriptive fields
(`variants: ["full"]`, a single `model.layers.27.mlp.down_proj` module,
`independent_split_seeds: false`, and an empty prompt-group list). Its executed
`arguments` array correctly names the frozen protocol and amendment, the real
anchor and estimator runs, and the amended conformance receipt; U0 independently
validated the exact `v_proj` module, prompt, replica, checkpoint, model, and
seed universe consumed by the collector. The stale display metadata therefore
does not change the registered result, but the wrapper manifest itself should
not be treated as an authoritative design receipt and should be corrected in
future runs.

The base protocol links this construction to the earlier prereveal negative
result under parent SHA-256
`bc3369f3b3793219261d73c3d685632c7d96ff86391b835d2f34cf92654ea9bf`.

## Local handoff artifacts

- `reports/qwen3_1p7b_functional_lineage_v2_independent_audit.md` records the
  independent hash-chain, primitive-bundle, algebraic, and exact-replay audit.
- `artifacts/qwen_functional_lineage_v2/real_v3_result_receipt.json` is the
  compact machine-readable result receipt.
- `artifacts/qwen_functional_lineage_v2/rank1_layer_boundary_table.json` and
  `.csv` expose the complete rank-1 layer boundary used for reporting and
  visualization.
