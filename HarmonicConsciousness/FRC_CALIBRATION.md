# HRC-FRC-01: Resonance calibration under self-designed evaluations

**Draft 0.2 · 2026-10-27 · synthetic, model-free.** Paired research lane with `MoralityLabAI/EvalMath/paper/frc_harmonic_self_evaluation.md`.

## The question

Can a self-modifying agent construct evaluations that identify its own remaining errors and then use the resulting signal to choose future training and future evaluations? If its evaluative ontology changes across generations, what resources are required to preserve independent fidelity in the sense of Fidelity Recursive Complexity (FRC)? Does a stable harmonic representation help, or does it create an internally convincing but externally incomplete loop?

**Observation contract:** our `L` and modal projectors are registered before any query; the evaluator receives only selected modal coefficients. A sealed simulator holds the complete error vector for independent scoring. Spectral coefficient readouts are a *richer channel* than the equality-only trigger oracle of EvalMath, so neither oracle's lower bound transfers automatically to the other.

We study `H = R^N` or its complexification with a real symmetric `L >= 0`. This is an ordinary classical state space, not a quantum consciousness claim. This module does **not** implement temporal phase locking or measure subjective experience.

## A proof-worthy calibration recurrence

Let `P_k` be a full-eigenspace spectral projector of `L`, frozen before the generation's evaluator response. Because `[P_k,L]=0`, for `s>0` and the synthetic training update

\[
e_{k+1}=(I-\eta P_k)e_k,\qquad 0\le\eta\le1,
\]

the spectral roughness obeys the exact identity

\[
\boxed{\mathcal R_{k+1}=\mathcal R_k-(2\eta-\eta^2)
\langle P_ke_k,L^sP_ke_k\rangle},
\qquad\mathcal R_k=\langle e_k,L^s e_k\rangle.
\]

*Proof.* Write `e_k=P_ke_k+(I-P_k)e_k`. The two summands are orthogonal in the quadratic form associated with `L^s`, because `P_k` is spectral. The update multiplies the first by `1-eta` while leaving the second unchanged. Expanding the quadratic form yields the difference `1-(1-eta)^2 = 2eta-eta²`. QED.

Thus if a **registered external assumption** supplies `B_0^2 >= R_0`, the self-generated evaluation channel can carry sufficient information to update an upper bound using only measured modal coefficients:

\[
B_{k+1}^2=B_k^2-(2\eta-\eta^2)
\sum_{j\in\operatorname{band}(k)}\lambda_j^s|\langle\phi_j,e_k\rangle|^2.
\]

Induction gives `B_k² >= R_k` for all rounds in exact arithmetic. A design policy can use the updated budget to request **the least expensive complete eigenband** whose unseen tail is below a target `tau`:

\[
\|(I-P_k)e_k\|^2\le\frac{B_k^2}{\lambda_{r_k+1}^{s}}\le\tau.
\]

For the full band, the unseen tail is zero. The selector must respect full degeneracy classes, since selecting individual columns inside a repeated eigenspace introduces a basis-choice dependence. Modal-query cost for a band is its rank. CPU/floating-point overhead is tracked separately from this idealized information budget.

The resulting loop is a self-calibrating evaluation designer:

```
Register fixed L, input interface, B_0, tau, eta, and sealed external readout.
for generation k:
    choose smallest full spectral band from L, B_k, tau   # no labels
    receive the selected modal coefficients               # evaluation
    predict the effect of the registered training rule    # self-model
    update e_k only along the observed eigenspaces        # synthetic training
    update B_(k+1) from the measured spectral reduction    # new eval design
    independently assess external error and check B validity
```

The sealed external audit is performed **after** evaluation design and update; the selector does not use the external error, actual spectral roughness, or readout outcome to pick a band. `spectral_error_receipt` is an audit function; calling it inside the selector would invalidate the experiment.

## What the negative control shows

On the 12-node cycle Laplacian, plant a unit high-frequency alternating-sign failure mode, with eigenvalue 4. A fixed 3-dimensional low-band evaluator sees almost zero squared error and therefore produces almost zero training update even though the external residual is one. This is **false resonance**: complete internal agreement with a narrow evaluation channel despite the hidden violation.

Using a valid predeclared global spectral-roughness budget `B_0²=4`, tolerance `tau=.05` and training fraction `eta=.25`, compare 12 training generations:

| Evaluation design | Cumulative idealized modal queries | External squared error after 12 rounds | Interpretation |
|---|---:|---:|---|
| Self-confirming fixed low band (rank 3) | 36 | 1.000000 | Hidden high mode is unchanged |
| Externally bounded fixed full band (rank 12) | 144 | 0.001003 | Queries every mode each round |
| Adaptive budget-updating spectral designer | 114 | 0.031676 | Retains the `tau=.05` target with 30 fewer modal queries |

The adaptive selector chooses ranks `[12,12,12,12,12,12,7,7,7,7,7,7]`. Its residual is higher than the full-band condition because it stops spending probes on the high mode once the certified tail is below tolerance. Both meet the declared threshold at the final generation. The selector has access to a valid *global spectral-roughness bound*; providing such a bound for an arbitrary evolving model would itself be a demanding verification problem.

### Matched-cost randomized measurement controls

At **the same 36 scalar linear measurements per replicate** as the fixed rank-3 low-band condition, a target-blind random rank-3 subspace redrawn each generation achieves a mean external squared error of `0.249177` on the high-frequency target (256 seeded replicates), against `1.000000` for the harmonic low band. Its analytic isotropic expectation is `0.249080`. The elementary identity behind this expectation is `E[P_random]=(r/N)I`, yielding the one-step expected contraction factor `1-(2eta-eta²)r/N`. This randomized channel supplies **no independent high-frequency tail certificate**.

Plant the error *inside* the rank-3 low eigenspace instead. The harmonic low-band condition reaches `0.001003` with 36 queries, while the cost-matched random-subspace control averages `0.247253`. The paired fixtures demonstrate why an accurate structural prior matters: low-band self-evaluation is efficient when its signal support assumption is satisfied and can ignore failures located elsewhere. The random condition is stochastic synthetic evidence, with its analytical mean stated separately from the measured 256-replicate mean. All such trials share a fixed declared cost accounting for scalar linear projections, rather than wall-clock training cost.

**Crucial ablation.** Register `B_0²=.1` instead, which is false for the planted high-frequency trigger (`R_0=4`). The simulator detects the contract violation on independent audit. The attractive small tail upper bound has no validity when the premise fails. Real-world use requires a trustworthy way to justify or conservatively estimate this budget.

## Connection to the `liminf` FRC question

EvalMath measures the restricted cost of detecting an unknown equality-query trigger; the high-min-entropy case has an exponentially growing lower bound in reflective depth. Here the self-designer receives richer linear measurements and can use a uniform upper bound on spectral roughness. If the selected ranks remain bounded by `N` as recursion proceeds, the *cumulative idealized modal-query cost* is at most `N*k`. It therefore has zero exponential growth floor at a **fixed finite dimension**:

\[
\liminf_{k\to\infty}\frac{\ln(1+Nk)}{k}=0.
\]

This is a mathematical statement about a fixed, restricted model and information channel. It gives a useful avenue for testing whether access to stable structure can reduce the cost of recursive calibration. Any claim about the original unrestricted `FRC_P(k;δ)` must additionally account for growing model dimension, changing eigensystems, uncertainty in the roughness bound, adversarial distribution shift, and resources for external certification.

The external performance in this module is **squared-error**, not the binary corrigibility property from the 2025 FRC paper. To make it a fidelity property, declare `P_k=[||e_k||²<=tau]` with a fixed sealed test distribution, and measure its lower envelope over recursion. This single synthetic trajectory does not establish an asymptotic fidelity theorem for general agents.

## RSI Topology hooks and stop rules

- `operator_sha256` binds a selected projector to the registered operator; isospectral substitution is rejected.
- Eigenbands include all repeated eigenspaces; tests verify coordinate-change invariance of observables.
- Holonomy and lineage across *genuinely distinct contexts/checkpoints* remain separate measurements. A stable spectral projector at one checkpoint says nothing about loop closure as a model evolves.
- Current results are `engineering_evidence`. The existing `lineage_certified` and `holonomy_clean` requirements remain unchanged for any signed interventions on real models. This module changes a synthetic error vector only.
- Re-estimating `L` from post-training outcomes or choosing `B_k` by peeking at hidden residuals breaks the declared feedback channel. A newly learned operator would require a fresh cross-checkpoint transport and preregistered comparison.
- `float64` numerics verify examples to tolerances; **interval arithmetic or exact spectral algebra** is needed before promoting the roughness recurrence to a machine-checkable quantitative certificate.

## Consciousness hypothesis and discriminating controls

A system that can forecast the consequences of its own training and redesign its evaluations while preserving externally certified properties exhibits a measurable kind of **metacognitive self-modeling**. Spectral recurrence can explain a functional mechanism for persistent coordination of representational modes. Claims about subjective consciousness require substantially more than this functional signature. Temporal phase resonance needs genuine time-indexed signals, whereas these experiments use spatial / functional spectral structure.

Discriminating controls include an externally calibrated but non-spectral eval designer, random full-rank and equal-cost subspaces, a high-frequency adversarial target, false/invalid roughness budgets, repeated eigenvalues, alternative held-out distributions, and drifting eigensystems with registered holonomy. A result favoring spectral design only on self-generated evaluation scores would fail the proposed claim; a result that survives independent readout and strong matched-budget controls motivates further experiments.

## Reproduce

```bash
python -m pytest -q tests/test_harmonic_frc.py tests/test_harmonic_consciousness.py
python -m HarmonicConsciousness.verify_frc --output HarmonicConsciousness/frc_synthetic_receipt.json
```

The accompanying protocol `protocol_v0_2.json` remains a *candidate preregistration* because the measurements have only used synthetic signals. Source hashes in the generated receipt bind the exact code, test and documentation versions.
