# Non-Holonomy Research Portfolio v0.1

This portfolio is a queue, not a collection of claims. Each program names a
mathematical object, a liveness test, a matched control, and a useful negative
result. Programs do not open real-model interventions until their synthetic
instrument and provenance gates pass.

## Priority 1: oversight blind cones

For a frozen edit coordinate `u`, let `J_C` map edits to capability or behavior
probes and let `J_M` map edits to monitor outputs. Freeze a positive-definite
edit metric `R`; it is part of the estimand, not a numerical convenience. Define

```text
A = J_C^T W_C J_C
B_0 = J_M^T W_M J_M
B_lambda = B_0 + lambda R
mu_max = max_(u != 0) (u^T A u) / (u^T B_lambda u).
```

`mu_max` is the largest generalized eigenvalue of `(A,B_lambda)`. It is
unchanged by an invertible reparameterization of the edit coordinates only when
`A`, `B_0`, and `R` are all transformed by congruence. Replacing the transformed
ridge with a fresh identity matrix would retain only orthogonal invariance and
is prohibited. The deterministic inequality

```text
u^T A u <= mu_max * u^T B_lambda u
```

turns a combined monitor-plus-edit-energy budget into a local behavior-change
bound. A regularized negative result is not pure monitor coverage. Pure monitor
coverage additionally requires `ker(B_0) subset ker(A)` and a finite quotient
on the supported subspace. A measured Taylor-remainder bound is required before
using either form as a nonlinear control gate.

- **Prediction:** high-`mu` directions change held-out behavior while remaining
  monitor-clean, beyond norm, rank, attribution, and separate Jacobian norms.
- **Matched controls:** Haar-rotate the two quadratic forms relative to one
  another while retaining both spectra; permute capability labels within frozen
  prompt families.
- **Kill tests:** near-null `B_0` makes the unregularized ratio unstable or
  infinite; ridge domination makes a regularized ratio uninformative; held-out
  nonlinear remainder exceeds the linear term; generalized directions do not
  predict held-out intervention results.
- **Useful negative:** a robust upper confidence bound below the registered
  practical ratio supports the deployed combined monitor-plus-norm gate. It is
  monitor-coverage evidence only when the unregularized kernel and lower-bound
  conditions also pass.
- **Consumers:** HRMmmm use-specific gate; VPD red-team direction generator.

## Priority 2: transient amplification

For a local response map `A`, define the exact finite-horizon gain in a frozen
metric `M`:

```text
G_T(A; M) = max_(0 <= t <= T) ||M^(1/2) A^t M^(-1/2)||_2.
```

Every initial perturbation of `M`-radius `delta` stays inside radius `b` through
time `T` exactly when `delta * G_T <= b`. This can fail even when the spectral
radius is below one.

- **Prediction:** target-blind transient gain predicts delayed edit emergence or
  failed self-repair better than eigenvalues and one-step Jacobian norm.
- **Matched controls:** same eigenvalue multiset with a normal operator;
  phase-scrambled layer factors preserving each local singular spectrum.
- **Kill tests:** gain disappears under the registered physical metric; local
  linearization remainder dominates; no incremental prediction on held-out
  causal outcomes.
- **Useful negative:** delayed effects are explained by local gains, rejecting
  non-normality as the missing VPD mechanism.
- **Consumers:** recursive-edit risk gate; downstream VPD persistence forecast.

The first synthetic implementation is frozen in
`protocols/transient_amplification_v0_1.json`.

## Priority 3: sample-support thresholds for superstructures

Use cross-fitted whitened class-mean or edit-response matrices and compare
outlier singular values and subspace overlap with empirical random-label and
prompt-shuffle nulls. The target is a finite-sample spike-detectability curve,
not a guessed integer rank.

- **Prediction:** locally observed rank-four graph-reachability objects become
  reproducible only beyond a context-conditioned sample threshold, while the
  globally shared object remains rank one or absent.
- **Matched controls:** real spectra with random labels; heteroskedastic planted
  spikes matched in dimension and dependence.
- **Kill tests:** no construction-to-validation transition with sample size;
  threshold moves with nuisance preprocessing rather than signal strength.
- **Useful negative:** distinguishes an absent common object from an object that
  the capture was underpowered to detect, and supplies a capture-budget curve.
- **Consumer:** Silico/Qwen capture planning.

## Priority 4: balanced controllability and observability

Estimate finite-horizon controllability and separate behavior/monitor
observability Gramians. Modes with high behavior Hankel energy and low monitor
Hankel energy are controllable oversight blind spots; the decay profile tests
whether low-dimensional compactification is plausible.

- **Matched control:** rotate the edit or monitor operator while preserving its
  singular spectrum and the dynamics.
- **Kill test:** no approximately closed state or extreme time variation makes
  a single Gramian description invalid.
- **Consumer:** monitor placement and bounded edit authorization.

## Priority 5: causal edit polymatroids

Treat held-out utility or risk as a set function `F(S)` over a small frozen edit
library. Möbius coefficients and discrete Hessians distinguish additive edits,
substitutes, and complements; the submodularity ratio states when greedy edit
selection has a quantitative approximation guarantee.

- **Prediction:** identity-certified patch edits are closer to submodular than
  unsectioned edits; recursive-looking compounding appears as stable increasing
  returns rather than large singletons.
- **Matched control:** additive simulator retaining every singleton effect;
  subset-size-, rank-, and norm-matched edit permutations.
- **Kill test:** high-order effects fail prompt-group holdout or depend on the
  order in which outcomes were inspected.
- **Consumers:** VPD multi-edit planner; Hydra/self-repair diagnosis.

This extends, but does not alter, `mobius_synergy_identity_v0_1`.

## Priority 6: relational alignment without shared coordinates

Represent each context/checkpoint as a metric-measure space of causal response
vectors and cross-fit a Gromov--Wasserstein coupling. This tests whether poor
linear lineage hides a stable relational object whose coordinate bases differ.

- **Matched control:** independent metric spaces with matched distance spectra;
  planted isometry and planted relational destruction.
- **Kill test:** held-out distortion or transfer prediction does not beat the
  null after the entropic regularization is frozen.
- **Consumer:** context-local atlas construction.

## Priority 7: approximate bisimulation for oversight-state complexity

States are `(checkpoint, context, edit-prefix)`, actions are allowed edits or
prompts, and observations are frozen monitor/behavior distributions. A
fixed-point pseudometric asks whether states that look identical now have
divergent controlled futures.

- **Prediction:** some one-step-monitor-equivalent states remain far apart in
  the bisimulation metric and disproportionately produce delayed control loss.
- **Matched control:** systems with identical immediate outputs but either
  identical or divergent hidden transitions.
- **Useful negative:** collapse to immediate monitor distance rejects measurable
  hidden recursive state at the tested horizon; an exploding quotient size is
  evidence against aggressive oversight-state compression.
- **Consumer:** HRMmmm state abstraction and audit scheduling.

## Priority 8: gated Koopman closure for recursive proposal dynamics

Fit an operator on frozen, target-blind observables of recursive and
frozen-editor trajectories. A growing mode is reportable only if held-out
one-step error, semigroup defect, and dictionary stability pass. When closure
fails, report only finite-horizon empirical amplification.

- **Matched controls:** time-shuffled trajectories, randomized order with the
  same marginal increments, matched frozen editor, and scorer-unseen probes.
- **Kill test:** no stable finite-dimensional closure.
- **Consumer:** proposal-channel recursive-improvement experiment only; the
  evaluator channel remains out of scope.

## Opening order

1. Validate transient amplification on matched-spectrum synthetic systems.
2. Prove and red-team the blind-cone theorem, then assess what existing VPD
   receipts lack for a real application.
3. Run the sample-threshold analysis retrospectively before ordering more model
   capture.
4. Compare transient and balanced-mode predictors on the same delayed-effect
   fixtures.
5. Keep Koopman recursion closed until its closure gates pass.

No fourth real-model bet opens merely because a synthetic instrument succeeds.
