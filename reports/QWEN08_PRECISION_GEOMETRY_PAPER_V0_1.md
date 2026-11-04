# Quantization erodes the geometry of a rank-one identity object before it touches the topology

**Margins, percolation, and forced holonomy under paired runtime precision in a frozen Qwen0.8B capture**

Patrick Dugan — RSITopology program — draft v0.1, 2026-07-17

---

## Abstract

We ask whether loop holonomy — the gauge-invariant transport of an identity
subspace around cycles in a lineage graph — detects damage that runtime
quantization does to a language-model identity object, or whether its
diagnostic utility at small scale is bounded. On a frozen Qwen0.8B development
model we measure a registered, target-blind, rank-one between-class identity
object (behavior family `graph_reachability`) at two sites (`model.layers.19`,
`model.layers.23`), two weight states (`base`, `naive_qlora`), and four fresh
context shards, under two runtime precisions on byte-identical prompts: NF4
4-bit double-quantization with float16 compute, against unquantized float16
weights. Four findings. **(1)** Quantization uniformly compresses the object's
support margin: all eight paired cells at layer 19 show positive
float16-minus-4-bit deltas (points 0.149–0.231). **(2)** A pre-registered
precision-specificity sentinel fails: the fine-tuned sentinel cell's precision
delta is indistinguishable from background (0.041, 95% CI [−0.131, 0.244]) —
precision damage is broad, not fine-tuning-specific. **(3)** Percolation
structure survives: cycle-emergence thresholds shift insignificantly, and the
one grid suppressed under 4-bit is traced to a single node's support-gate
failure, not loop deletion. **(4)** Every measured cycle's holonomy sign is
+1 in both precisions — but we prove this was geometrically forced: with edge
angles α = arccos√r, no cycle's angle budget exceeds 99.7°, and a rank-one
cycle can be non-orientable only if its budget reaches 180°. The first
Stiefel–Whitney class therefore carries zero information beyond edge lineages
on this capture. The live holonomy observable is instead the *frustration
margin* (180° minus the maximal cycle angle budget), which quantization
measurably erodes at layer 19: 23.5° (22.6% of the float16 margin,
descriptive 90% interval [5.1°, 53.1°]), clearing the registered descriptive
decision rule. This interval is not a calibrated confidence statement. The
useful pattern is a strict
degradation ordering — margins compress, one gate crosses, the angle budget
erodes, topology never moves — and a falsifiable condition for when the
metric obstruction ceases to make the binary topological test vacuous.

---

## 1. Introduction

Mechanistic interpretability leans on subspace identifications: a feature or
monitor direction found in one context, checkpoint, or precision is treated as
"the same object" elsewhere. This program's prior receipts show why that
inference needs more than similarity numbers: retention statistics discard the
polar factor that transports signed coordinates, and a system can beat every
retention control while returning a monitor rotated far from its original
orientation after one loop. The gauge-invariant repair is holonomy: transport
the subspace around closed loops in a graph whose nodes are measurement
conditions, and report only conjugacy-class data. For a rank-one object the
entire holonomy group is O(1): each cycle carries a sign, and the assignment
of signs to the cycle space is the first Stiefel–Whitney class `w1` of the
line bundle the object traces over the condition graph.

This paper stress-tests that instrument with runtime precision as the probe.
Quantization is an attractive probe for three reasons: it is a controlled,
practically relevant perturbation; it acts on weights rather than prompts, so
prompt-side confounds can be eliminated exactly; and if identity geometry is
to be useful for monitoring deployed models, it must survive — or fail
legibly under — the precisions models are actually served at.

We ask two questions. **Q1:** does 4-bit quantization degrade a registered
rank-one identity object, and is the degradation specific to a fine-tuned
weight state? **Q2:** does holonomy detect anything margins do not — is the
topological channel a useful pattern or diagnostically empty here?

The answer to Q1 is yes and no respectively: degradation is uniform and
well-resolved, and the pre-registered specificity hypothesis fails cleanly.
The answer to Q2 is the paper's main methodological contribution: the binary
`w1` outcome was **geometrically forced** on this capture — the test could
not have failed — and we show how to convert that dead binary channel into a
live graded one (the frustration margin), which quantization measurably
erodes. We report the forcing bound as a general liveness criterion that any
rank-one holonomy claim must clear.

## 2. The object and the instrument

**Identity object.** The measured object is a rank-one between-class identity
direction for the `graph_reachability` behavior family, constructed by
cross-fitted between-class scatter on frozen Qwen0.8B activations
(float32-stored in both arms). Candidate bases were sealed (SHA-256 per-cell
basis hashes in the receipts) before any outcome was read.

**Lineage graph.** Nodes are measurement cells (weight state × context
shard) at a fixed site and precision: a 2 × 4 ladder with 8 nodes and 10
edges — 6 within-state adjacent-context edges and 4 between-state checkpoint
edges. Its cycle space has β₁ = 3; the longest simple cycle has 8 edges.

**Support statistic and gates.** Each cell's support is
`minimum_edge_worst_direction_retention`, where worst-direction retention is
the minimum squared singular value of the transported basis product —
r = cos²α for principal angle α. A cell passes if its retention clears a
registered null boundary (95th percentile of a matched label-permutation
null, matched on site, rank, prompt count, spectrum, and RNG stream, plus a
strict margin of 0.02). The signed support margin is the distance to that
boundary. A grid is supported only if every node passes.

**Holonomy at rank one.** Each edge carries a transport sign; each cycle's
holonomy is the product of its edge signs, gauge-invariant on the GF(2) cycle
space. Canonical angles are suppressed by construction: SO(1) is trivial, and
the only invariant at rank one is the O(1) sign class. Every holonomy row in
this program is diagnostic-only: it adds no attestation level and reopens no
causal stage.

**Theorem 1 (rank-one holonomy liveness).** Let
`L_0, …, L_m = L_0` be a cycle of real lines. For each adjacent pair, let
`α_i ∈ [0, π/2]` be its projective principal angle, and use shortest-geodesic
rank-one transport. If the cycle has negative holonomy, then

```text
Σ_i α_i ≥ π.
```

Consequently, `Σ_i α_i < π` certifies positive holonomy. With measured
rank-one retention `r_i`, the edge length is `α_i = arccos sqrt(r_i)`.

*Proof.* Choose a unit representative `v_0` of `L_0` and lift each successive
shortest projective-geodesic segment continuously to the unit sphere. Negative
holonomy means that the terminal lift is `−v_0`. The spherical distance from
`v_0` to `−v_0` is `π`, while the lifted polygon has length `Σ_i α_i`.
The spherical triangle inequality therefore gives `Σ_i α_i ≥ π`. ∎

Equality can occur only when the lifted polygon is itself a minimizing
geodesic from `v_0` to `−v_0` (possibly subdivided), so that its vertices lie
in order on a great semicircle. In particular, reaching `π` removes the
forcing obstruction but does not imply negative holonomy.

**Corollary 1 (upper-bound certificate).** If registered edge-wise upper
bounds `bar(α_i)` satisfy `Σ_i bar(α_i) < π`, then the cycle has positive
holonomy. Thus a rank-one cycle can test orientability only after its measured
or conservatively upper-bounded angle budget reaches 180°. Below that, a
holonomy sign of `+1` (equivalently, `w1` evaluates to zero on the cycle) is
forced by the measured lineages and observing it confirms nothing.

Liveness is a property of the *measured angles*, not of loop length or of the
edge-admission threshold τ: lowering τ admits no new edges once all captured
edges already exceed it.

## 3. Experimental design

All protocols were frozen with SHA-256 hashes before execution; all elementary
outcomes were sealed before derived statistics were computed. Three registered
analyses are reported, in execution order:

| Analysis | Protocol / SHA-256 (abbrev.) | Registered category |
|---|---|---|
| Paired precision compute | `qwen08_l19_precision_context_v0_1` / `6437d637…adb5ef8b` | `sentinel_not_reproduced_or_not_precision_specific` |
| Filtration + w1 | `923b2cff…9b7830aa` | `precision_stable_diagnostically_thin` (interpretation superseded, §4.5) |
| Frustration margin | `qwen08_precision_frustration_margin_v0_1` / `a407503b…a53bed069` | `w1_forced_orientable_all_graphs` |

**Precision arms.** 4-bit NF4 double-quantization with float16 compute,
versus unquantized float16 weights. Activations are float32-stored in both
arms. This is **not** an fp32 arithmetic comparison; all claims are relative
between these two runtime configurations.

**Prompt identity.** Both arms consumed byte-identical prompt sets: 2,304
prompts per precision view, common payload SHA-256
`87d2f05e…5806c14e`, same tokenizer source, order, and final non-padding
token rule (`identical_except_runtime_precision: true`).

**Cells.** 2 precisions × 2 states × 2 sites × 4 shards = 32 cells, each
with sealed basis hashes, a 256-replicate bootstrap, and a 256-replicate
matched permutation null.

**Sentinel.** One cell — `naive_qlora` / `model.layers.19` / `shard-02` —
was pre-registered as the precision-specificity sentinel. The registered
requirement: its complete-margin precision delta must exceed the per-draw
median non-sentinel delta (64 inner replicates, 1,024 outer bootstrap).

**Statistical discipline.** No multiplicity correction was registered;
individual cell intervals are descriptive, and the robust claims below are
stated as sign-consistency across cells. Bootstrap intervals for max-type
threshold statistics (τ_cycle, angle budgets) are percentile-descriptive: the
full-sample point may fall outside them and no calibrated coverage is
claimed.

## 4. Results

### 4.1 Quantization uniformly compresses support margins

*(Figure A: `figure_a_paired_margin_deltas.png`)*

All eight paired cells at layer 19 show positive float16-minus-4-bit
complete-margin deltas:

| state | shard | delta | 95% CI |
|---|---|---:|---|
| base | 00 | 0.192 | [0.040, 0.354] |
| base | 01 | 0.197 | [0.051, 0.364] |
| base | 02 | 0.204 | [0.047, 0.379] |
| base | 03 | 0.149 | [0.012, 0.306] |
| naive_qlora | 00 | 0.213 | [0.041, 0.404] |
| naive_qlora | 01 | 0.223 | [0.066, 0.377] |
| naive_qlora | 02 | 0.231 | [0.073, 0.422] |
| naive_qlora | 03 | 0.170 | [0.027, 0.336] |

Every interval excludes zero individually, but the registered claim is the
8/8 sign consistency. The effect is site-graded: under 4-bit, layer 23 keeps
comfortable margins (0.115–0.220) while layer 19 sits on the support boundary
(base-state margins as thin as 0.0017).

### 4.2 The precision-specificity sentinel fails

The sentinel cell itself reproduces under 4-bit (gate passed, margin 0.061),
but its precision delta minus the per-draw median non-sentinel delta is
0.041 with 95% CI [−0.131, 0.244]: the registered specificity requirement
fails and the sentinel classification is `inconclusive`. Precision damage is
**broad across states and shards, not specific to the fine-tuned state**.
The parent category name conflates two outcomes; the receipts disambiguate:
*reproduced, not precision-specific*.

### 4.3 One local support-gate crossing

31 of 32 cells pass their support gates. The single failure is
4-bit / `naive_qlora` / layer 19 / shard-01 (margin −0.0246, matched-label
gate failed, classified `degraded_under_precision`). This is the boundary
crossing that the margin compression of §4.1 predicts for the thinnest cells,
and it is the sole cause of the one unsupported grid in §4.4.

### 4.4 Percolation structure survives quantization

*(Figure B: `figure_b_filtration_curves.png`)*

Exact critical floors over the full edge filtration:

| precision | site | τ_conn | τ_cycle = τ_loop | fragility vs frozen 0.9 floor |
|---|---|---:|---:|---|
| 4bit | L19 | 0.9059 | 0.9418 | critical_surface_overlap (0.0418) |
| 4bit | L23 | 0.9159 | 0.9357 | critical_surface_overlap (0.0357) |
| float16 | L19 | 0.9484 | 0.9666 | robustly_above_floor (0.0666) |
| float16 | L23 | 0.9182 | 0.9465 | critical_surface_overlap (0.0465) |

All four graphs reach β₁ = 3 at τ = 0; τ_cycle > τ_conn everywhere,
consistent with the program's earlier finding that cycles can close before
the node universe connects. The paired precision contrasts on τ_cycle are
not established under the registered descriptive decision rule (L19: 0.0248,
descriptive 90% interval [−0.0037, 0.0867]; L23: 0.0108, descriptive 90%
interval [−0.0136, 0.0551]). These max-statistic bootstrap ranges are
descriptive sensitivity summaries, not calibrated confidence intervals.

The 4-bit layer-19 grid suppression in the parent analysis is **not** a
percolation phase transition: diagnostic cycles already exist at
τ_cycle = 0.9418, above the frozen 0.9 floor. The grid was suppressed
because the shard-01 node of §4.3 failed its support gate. Node support,
not loop availability, was the binding constraint.

### 4.5 Holonomy is trivial in both precisions — and provably had to be

Every one of the seven nonzero GF(2) cycle classes per graph (six connected
simple cycles of 4–8 edges plus one non-simple chain) carries holonomy sign
+1 in both precisions at both sites, with construction/validation agreement
and bootstrap sign agreement of 1.0 throughout, and a gauge preflight of
10,752 cycle decisions across 384 reframings per graph with zero
determinant-decision mismatches.

This is not evidence of stability. Applying the liveness criterion of §2
with the correct conversion α = arccos√r:

| precision | site | max cycle angle budget | frustration margin | 90th-pct upper budget |
|---|---|---:|---:|---:|
| 4bit | L19 | 99.29° | 80.71° | 168.49° |
| 4bit | L23 | 99.68° | 80.32° | 163.45° |
| float16 | L19 | 75.75° | 104.25° | 125.82° |
| float16 | L23 | 92.65° | 87.35° | 145.67° |

No point-estimate cycle budget approaches 180°, so Theorem 1 deterministically
forces positive holonomy on every measured graph. The 90th percentile of the
paired bootstrap angle-budget distribution also remained below 180° in all
four graphs; this is descriptive and not a calibrated confidence statement.
The maximal budget always falls on the 8-edge outer cycle; the frozen 2 × 4
ladder contains no longer simple cycle by construction. The earlier registered
category `precision_stable_diagnostically_thin` remains sealed, but its
interpretation is formally superseded by
`w1_forced_orientable_all_graphs`: on this capture, `w1` supplies no
information beyond the edge lineages that force it.

### 4.6 The frustration margin is the live holonomy observable

*(Figure C: `figure_c_frustration_margins.png`)*

The graded quantity 180° − (max cycle angle budget) is live, gauge-relevant,
and precision-sensitive. Quantization erodes it:

- **Layer 19: 23.54° erosion** (22.6% of the float16 margin), descriptive
  90% interval [5.11°, 53.11°] — **established under the registered
  descriptive decision rule**, not as a calibrated confidence statement.
- Layer 23: 7.03° erosion (8.0%), interval [−5.20°, 29.10°] — not
  established under the registered descriptive decision rule.

The site ordering matches §4.1: the site whose margins quantization
compresses hardest is also the site quantization pushes fastest toward the
frustration boundary.

## 5. Discussion

**The pattern.** The receipts fix a strict degradation ordering under 4-bit
quantization: support margins compress uniformly (8/8 cells) → the thinnest
cell crosses its gate → the projective angle budget erodes measurably at the
fragile site → the topological class never moves, and provably could not
have. Identity geometry degrades from the metric outward; topology is the
last invariant standing, and at this scale it is protected by forcing rather
than tested by measurement.

**What this says about holonomy's utility.** For rank-one objects on small
condition graphs at high lineage, the binary holonomy channel is
*diagnostically empty* — a bound, not a failure. Any pipeline that reports
"w1 trivial, therefore orientation-stable" without computing angle budgets is
reporting a tautology; this paper's own first-pass filtration analysis made
exactly that error before the forcing computation corrected it, and we keep
both registrations visible as the audit trail. The utility that survives is
graded: the frustration margin behaves as a continuous precursor — a
distance-to-frustration that perturbations consume long before any sign can
flip — and it detected quantization damage at layer 19 with an effect size
(22.6% of margin) large enough relative to the measured margin to motivate a
preregistered deployment-monitoring follow-up.

**A falsifiable exit condition.** The forcing bound converts "diagnostically
thin" into a prediction: the angle-budget obstruction ceases to force
positive holonomy only when some cycle's budget reaches 180°. Reaching that
boundary is necessary for negative holonomy to become possible, but does not
ensure a negative sign. Two candidate routes for a separately preregistered
follow-up are: (i) more context shards — longer simple cycles accumulate
budget roughly linearly in context-edge count (context edges carry 14–26°
here; checkpoint edges ≈3–5° are nearly free); (ii) harsher perturbation — at
the observed L19 erosion per precision step, further quantization pressure
(e.g. 3-bit) plausibly closes the remaining ≈80° gap. If a frustrated cycle
then appears where float16 stays coherent, holonomy detects damage margins
cannot localize; if budgets
cross 180° and every sign stays positive, that is the first *earned*
orientability result for this object family.

**Relation to the sentinel negative.** The specificity failure is
informative: naive QLoRA fine-tuning did not make the identity object more
quantization-fragile than the base state at the sentinel. Precision damage
here acts like a global contraction of context transport, not an interaction
with the fine-tuning delta — consistent with the checkpoint edges' near-unit
retentions in both states.

## 6. Limitations

- Single frozen development model (Qwen0.8B), one behavior family, one
  rank-one object; no cross-model claim.
- NF4/float16-compute vs float16 weights; not an fp32 arithmetic comparison.
- Four context shards give a 2 × 4 ladder whose longest simple cycle is 8
  edges; the ladder cannot express the ≥180° budgets needed for a live
  binary test. This is a capture-design limit, now a registered parameter
  for the follow-up.
- Bootstrap intervals on max-type statistics (τ thresholds, angle budgets,
  erosion) are descriptive percentile ranges; points may fall outside them
  and no calibrated coverage is claimed. No multiplicity correction was
  registered.
- The sentinel is a single pre-registered cell; the specificity negative is
  one contrast, not a survey of fine-tuning methods.
- Stage B (conditional L23 replication) and the Qwen3-1.7B identity negative
  are program context only; they use different protocols and objects and are
  **not pooled** with any statistic here.

## 7. Reproducibility

| Item | Value |
|---|---|
| Parent protocol SHA-256 | `6437d637d6a25efe47c462a0cadeb9aa2dd18a018a794f9e688befa4adb5ef8b` |
| Filtration/w1 protocol SHA-256 | `923b2cff503952cc7d6eea29ff999416d0c82ee4f40f015b8804e36d9b7830aa` |
| Frustration-margin protocol SHA-256 | `a407503b908fa484e7ee09a608eed3d14f1aa7e6e3eca9e731cf34ca53bed069` |
| Prompt payload / manifest SHA-256 | `87d2f05eb24e7074943b6625c907bf08362db5ffa5ac24f6a313f7d75806c14e` / `9315073ff8db07fb258563957b509cdbe6ecfdc80ab0a12b869fe614077e88db` |
| Registration / implementation commits | filtration: `70e169a` / `95846b0`; frustration: `789e465` / `cdfccc3` |
| Replicates | support: 256 bootstrap + 256 permutation per cell; paired: 64 inner × 1,024 outer; filtration: 256 paired stratified, seed 2026071719 |
| Runtime (analyses) | filtration 210 s, peak RAM 1.024 GB; frustration 114 s, peak RAM 1.023 GB; bounded job objects, cleanup and release hashes passed |
| Artifacts | `analysis_v0_1_1/`, `analysis_filtration_w1_v0_1/`, `analysis_frustration_margin_v0_1/` under `runs/qwen08_l19_precision_context_v0_1/` |

## 8. Claim boundary

This is an outcome-free measurement study. It can establish or falsify
precision-conditioned reproducibility of a rank-one between-class identity
object on the frozen Qwen development model, fresh prompts, sites, states,
and runtime precisions, and it can bound when rank-one sign holonomy is
forced or live on this capture. It cannot establish semantic identity,
causal edit value, VPD efficacy, monitor sufficiency, capability
preservation, compactification, recursive self-improvement, or RSI.
Holonomy remains a downstream diagnostic only: it adds no attestation level
and reopens no closed causal or VPD stage.
