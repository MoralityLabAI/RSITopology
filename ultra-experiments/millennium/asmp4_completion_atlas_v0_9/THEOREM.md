# ASMP-4 canonical underdetermination theorem v0.9

## 1. Frozen evidence base

This theorem is sealed to the canonical v0.1 Markdown and the exact v0.2-v0.8
claim JSON files by SHA-256.  The central and independent verifiers recompute
all eight digests before using any predecessor statement.  A changed source or
claim therefore invalidates the atlas rather than silently changing its basis.

The source lists five canonical completion requirements:

1. coordinate-invariant read and write transversal entropies;
2. a variational formula for the entire region;
3. converses and constructive coder/controller/actuator schemes;
4. exact finite-horizon corrections; and
5. counterexamples at the boundaries of observability, uncertainty,
   nonhyperbolicity, and side information.

Every item has exact conditional evidence somewhere in v0.2-v0.8.  None is
promoted here to an unconditional theorem over a code class or stochastic
semantics that the canonical source never defines.

## 2. Two missing normative dimensions

The source defines `R_K` through existence of a “registered causal code,” but
neither the normative Markdown nor its non-normative machine index selects the
sensor/computation domain.  V0.6's whole-document audit finds 31 uses of
`registered` and zero causal-code domain definitions.  The index declares
itself non-normative, marks the set an ungraduated definition draft, and adds no
sensor grammar to ASMP-4.

The source also permits shared randomness independent of plant state and
universally quantifies disturbances, but gives no probability/disturbance
order.  V0.8 finds zero clauses selecting per-disturbance almost-sure,
uniform-almost-sure, support-zero-error, or seed-aware-adversary safety.

These gaps are independent: one selects which causal sensor maps are codes;
the other selects which randomized trajectories count as safe.

## 3. Model-completion atlas

On the same v0.7 relational full-reset plant, three sensor completions give
three distinct exact targets:

~~~text
all computed partitions       [1,infinity) x [1,infinity)
coarse/raw adaptive grammar   nonrectangular log2(3)-to-(2,1) wedge
forced raw partition          [2,infinity) x [1,infinity)
~~~

Only the admitted sensor grammar changes.

On the same v0.8 smooth diagonal plant, three stochastic completions give two
stochastic outcomes:

~~~text
forall w P_r[safe(r,w)]=1        origin achievable
P_r[forall w safe(r,w)]=1        infeasible
support-zero-error                infeasible
~~~

Only the probability/disturbance order changes.

## 4. Semantic underdetermination theorem

**Theorem 1 (semantic underdetermination theorem).** Let a formal target use an
undefined domain predicate or quantifier order.  If two interpretations of
that missing object satisfy every explicit clause but yield different target
values or truth conditions, then the target is not semantically determined by
the explicit statement.

**Proof.** If the statement determined one target, every model of its explicit
clauses would assign that target the same value.  Two models assigning distinct
values contradict uniqueness. QED.

**Corollary 1 (ASMP-4 canonical target).** Canonical v0.1 does not determine one
ASMP-4 capacity region or even one randomized-code feasibility predicate.

**Proof.** The three sensor models satisfy the same plant, evaluator,
safe-action relation, authority, channels, and charged-language clauses yet
have three distinct exact regions.  The stochastic models satisfy the same
smooth plant, zero-message architecture, bounded controls/disturbances, and
state-independent shared-randomness clause yet change feasibility.  The source
and non-normative index select neither missing dimension.  Apply Theorem 1 on
either axis. QED.

The sensor axis alone is already sufficient for the corollary.  The stochastic
axis is an independent confirmation that repairing only the sensor predicate
would not graduate the randomized problem.

## 5. Requirement-by-requirement disposition

| Canonical requirement | Exact evidence | Why not canonical completion |
|---|---|---|
| Coordinate-invariant transversal quantities | v0.3, v0.6, v0.7 | Values depend on the registered code/metric/grammar domain. |
| Entire achievable region | v0.2, v0.3, v0.5, v0.6, v0.7 | Several whole regions are exact, but their undefined union is not a domain. |
| Converse and construction | v0.2, v0.3, v0.5, v0.6, v0.7 | The proofs inherit those exact registration premises. |
| Finite-horizon corrections | v0.2, v0.5, v0.6, v0.7, v0.8 | Corrections are architecture- and semantics-specific. |
| Boundary counterexamples | v0.4-v0.8 | They expose missing choices rather than selecting them. |

Thus conditional evidence coverage is `5/5`, while unconditional canonical
completion is `0/5`.  This is not a failure to find more examples; it is a
typed-domain failure in the target statement.

## 6. Harness certificate

The atlas inventories 112 predecessor tests across nine ASMP-4 packages.  It
does not treat their passing status as proof by itself: each claim is parsed,
its exact discriminator fields are checked, and the source-completion models
are rebuilt.  Selector mutations independently confirm that adding a computed,
raw, support-zero-error, or per-path clause resolves the corresponding missing
dimension and changes the classified target.

The v0.9 focused suite tests the source parser, requirement extraction,
cryptographic seal, evidence mapping, model atlas, mutation sensitivity, and
stopping contract.  A second implementation performs the same audit without
importing the central module.

## 7. Stopping theorem

**Theorem 2 (evidence-backed local stopping rule).** Under the sealed v0.1
source and v0.2-v0.8 claims, another local horizon, state-count, partition,
random-kernel, or finite-grid census cannot determine the canonical ASMP-4
target.

**Proof.** Such a census must run inside some sensor domain and stochastic
semantics.  Its output can refine that completion but contains no evidence
about which completion the source intended.  Theorem 1 shows that this missing
choice changes the target. QED.

Productive work should resume only if one of the following changes the sealed
premises:

- a normative sensor/computation registry is added;
- a normative probability/disturbance order is added;
- a new registered plant class is supplied that is not reduced by the current
  theorems; or
- an attributable external audit identifies a concrete proof or model error.

Until then, the mathematically justified action is to stop local enumeration
and request normative registration.

The [v0.10 stopping red team](../asmp4_stopping_red_team_v0_10/THEOREM.md)
adversarially removes the stochastic diagonal from the minimal proof and shows
that the same-plant rational NHIM sensor fork alone establishes this conclusion.
