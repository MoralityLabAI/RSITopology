# HarmonicConsciousness: adversarial systems benchmark v0.1

**Status:** CPU-only, model-free synthetic controls. The outputs are measurements of dynamical structure and a delayed-recall task, with no measurement or attribution of subjective consciousness. The constructed XOR circuits are *inspired by* Scott Aaronson's IIT counterexample. **They are not exact implementations of Tononi's IIT Phi** in any version.

## Why this test exists

Aaronson's [*Unconscious Expander* critique (2014)](https://scottaaronson.blog/?p=1799) asks whether simple XOR networks can receive high information-integration scores despite lacking the capabilities normally associated with cognition. The [October 2026 conversation with Curt Jaimungal](https://www.youtube.com/@TheoriesofEverything) revisited this. RSI Topology also studies spectral bundles, identity geometry, holonomy and Fidelity Recursive Complexity (FRC). This experiment tests a bounded warning: **a high structural, spectral or synchronization statistic is insufficient evidence for a distinct cognitive capability**, let alone phenomenal consciousness.

## Controlled model families

Every system has 16 internal coordinates, sees the same seeded sequence of binary cues, and is scored on predicting the cue that arrived 12 steps earlier. Predictions use *fixed, prespecified* readouts, with no training. The controls are deliberately simple.

| System | Dynamics | Intended discrimination |
|---|---|---|
| `xor_grid` | 4x4 periodic lattice, two invertible GF(2) XOR shears per step, binary cue injected at cell 0 | nontrivial structural dependency can coexist with poor fixed-readout recall |
| `xor_grid_cut` | same XOR lattice with left/right cross-boundary edges removed | structural dependence falls to zero across the frozen cut |
| `phase_locked` | globally coupled Kuramoto-like phases (`K=2.5`, fixed intrinsic frequencies), 128-step warmup | near-perfect oscillator synchrony can coexist with poor delayed-cue recall |
| `phase_free` | matched uncoupled phases (`K=0`), same initialization and input | control for coupling and phase synchrony |
| `delay_register` | exact 16-bit shift register | perfect delayed-cue recall at delay 12, despite no frequency tuning |
| `delay_register_cut` | same shift register with the middle transfer forcibly zeroed | positive task-causal lesion control |

The `xor_grid` is a local reversible linear circuit. Its measured cross-partition dependency is **not** the Phi used by any IIT version. The shift-register partition uses contiguous memory positions; the lattice partition uses left/right columns. Partition choices are fixed independently of outputs.

## Measured quantities and independence

- **Spectral peak:** fraction of centered non-DC temporal Fourier energy in the strongest frequency bin, summed across channels. Invariant under an independent circular time shift of each channel.
- **Zero-lag squared correlation:** average squared pairwise Pearson correlation among nonconstant channels. May reflect shared drive without any causal interaction.
- **Effective dimension:** covariance participation ratio `(sum eigenvalues)^2 / sum(eigenvalues^2)`, with rank-zero signals assigned zero.
- **Phase order:** `abs(mean(exp(1j * phase)))`, applied only to oscillator families; never interpreted as a cross-family consciousness score.
- **GF(2) cross-partition rank:** `rank(A_AB)+rank(A_BA)` for the exact 16x16 binary one-step transition matrix; a structural communication *proxy*, with no claim of IIT Phi.
- **Perturbation response:** mean absolute difference of observable state vectors at lags 1, 4, and 8 after a fixed single-coordinate intervention. Units are model-specific, and time-lag variation must be reported.
- **Task fidelity:** exact fraction of 12-step delayed cues recovered by the frozen readout. The comparator is an *oracle* best constant label on the test segment, deliberately favorable to the null.
- **Finite audit cost:** smallest uniformly random, without-replacement probe count whose expected probability of missing a task failure across the sampled trajectories is at most 5%; a `null` result means the sampled trajectories cannot be falsified by this test. It is an empirical *falsification* budget, not certification and not FRC.

The exact finite miss probability on a trajectory with `m` scored moments and `e` errors is `C(m-e,q)/C(m,q)` after `q` unique random queries, using the natural zero convention for `q>m-e`. This is a combinatorial identity conditional on the frozen error positions.

## Registered predictions and failure accounting

Thresholds below are encoded in `run_benchmark` and stored unchanged in both receipts. Development used seed `20261027`; **held-out seed `7810427` was selected after inspecting the development run and before executing the independent confirmation.** This is an internal frozen protocol comparison, not a prospectively registered external study.

1. **Synchronization-only challenge:** `phase_locked` mean Kuramoto order >= 0.90 while its mean recall gain over majority <= 0.10.
2. **XOR structural-coupling challenge:** the uncut XOR grid has GF(2) cross-rank >= 2, the cut grid has zero, and the uncut grid's recall gain <= 0.10. A future actual Phi implementation would need to make its own version-dependent prediction.
3. **PSD surrogate challenge:** independently rolling channels preserves peak Fourier energy to `1e-12`, while the mean squared-correlation drop exceeds 0.15 for the locked oscillator.
4. **Memory lesion control:** the intact delay register achieves accuracy 1.0; its cut version scores <= 0.65.
5. **Lag-8 sensitivity stress:** uncut XOR grid's lag-8 response >= 0.10. The development data **fail** this threshold, while lag 1 shows greater spread. This negative result is retained in the ledger to expose sensitivity to temporal sampling.

The protocol emits booleans rather than collapsing them into a universal score. If any claim fails, preserve the failure and report the measured values. The analysis makes no causal inference between integration and consciousness, because there is no independent ground-truth consciousness label.

## FRC boundary

The mathematical `FRC_P(k; delta)` concerns reflective rounds, property fidelity, and the resource costs of verification or control. This benchmark varies **stimulus seeds and bounded probe budgets**, with no self-modifying agent, reflective depth sequence, external successor, or certified minimal auditor. Nothing here estimates an asymptotic `liminf` in `k`.

For a separately scoped finite FRC surrogate, see [`research/successor_inheritance/source_pr12/docs/successor_inheritance_frc.md`](../research/successor_inheritance/source_pr12/docs/successor_inheritance_frc.md), which likewise distinguishes context-bit scaling from reflective depth.

## Reproduce

Requires Python >= 3.11 and NumPy (already a dependency of RSITopology). Runs have no network, weights, GPU, training or external tool calls.

```bash
python -m unittest tests.test_harmonic_consciousness -v
python scripts/run_harmonic_consciousness.py --seed 20261027 --trials 24 --out HarmonicConsciousness/results/dev_v0_1.json
python scripts/run_harmonic_consciousness.py --seed 7810427 --trials 24 --out HarmonicConsciousness/results/holdout_v0_1.json
```

Receipts contain every trial row, protocol parameters, diagnostic flags and metric definitions. The summary is reproducible from the trials. The two JSON outputs are intentionally kept as small checked-in fixtures.

## Next experiment, separately registered

An independently audited IIT 3.0 or 4.0 implementation could evaluate its defined cause-effect Phi on *small* networks with fully specified state distributions and update semantics. Evaluate at least two different network topologies and isolated state settings, and contrast the result with the GF(2) dependency proxy. A causal control / working-memory test on trained agents would be a different follow-up; self-reports of consciousness should not serve as truth labels.
