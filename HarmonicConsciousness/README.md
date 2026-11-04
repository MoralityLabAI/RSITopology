# HarmonicConsciousness

**Research status:** speculative mechanism program, v0.1 (2026-10-27). The
purpose of this directory is to turn a proposed **N-dimensional Hilbert-space,
harmonic-resonance theory of consciousness** into mathematics that admits
counterexamples, operational measurements, and eventually causal tests.

The finite complex Hilbert space is a useful representation of coupled classical
signals; it does **not** import quantum-consciousness claims. No current
synthetic result establishes subjective experience, machine consciousness, or a
neural mechanism of awareness.

## Core distinction

- **Spatial harmonics:** eigenvectors of a fixed brain-connectome, sheaf, or
  graph Laplacian. Their eigenvalues describe spatial structure.
- **Temporal resonance:** oscillations of modal coefficients measured through
  time. A spatial eigenvalue becomes a temporal angular frequency
  `omega_k = sqrt(lambda_k)` only in the *specified* ideal wave equation
  `u'' + L u = 0`. Real neural activity has forcing, dissipation, nonlinear
  interactions, delays, and measurement artifacts.
- **Identity across contexts:** repeated eigenspaces admit arbitrary basis
  rotations. Compare their projectors and, when warranted, transport along
  explicitly registered paths; see RSI Topology's existing lineage/holonomy
  contracts. Phase-locking scores depend on a registered mode identification.

## First mathematical result: finite-mode localization

For `u(t) = sum_k a_k exp(i omega_k t) phi_k` and an observation operator `B`,
we compute the exact time-averaged localized energy

`E_T = (1/T) integral_0^T ||B u(t)||^2 dt`.

The interference between *different frequencies* obeys an explicit bound that
decays as `1/T` for fixed separated frequencies. Exact frequency degeneracies
are grouped as projectors, so the result survives arbitrary orthonormal basis
changes inside a degenerate eigenspace. This is a direct finite-dimensional
identity. It does **not** establish Sogge's local-smoothing conjecture for a
finite graph, brain, or transformer. See [FOUNDATIONS.md](FOUNDATIONS.md) for the
statement and proof.

OpenAI's 2026-10-26 release reports a Lean-formalized solution of Euclidean
local smoothing in all dimensions. That is external research under community
examination. We use it as motivation for asking *which* time-averaging effects
are observable in graph wave models. The continuum result is not assumed.

## Files

- [FOUNDATIONS.md](FOUNDATIONS.md): state model, a proved localization lemma,
  gauge/holonomy boundaries, falsifiable hypotheses, and relevant literature.
- [protocol_v0_1.json](protocol_v0_1.json): proposed preregistration with
  provenance, null controls, separation of construction/reveal, and stop rules.
- [probe.py](probe.py): small deterministic NumPy implementations of the exact
  finite-mode identity, numerical quadrature, phase locking, surrogate control,
  and effective rank.
- [example_run.py](example_run.py): reproducible JSON receipt from constructed
  signals, labelled **synthetic_only**.
- [synthetic_receipt.json](synthetic_receipt.json): pinned example of that receipt.
- [`../tests/test_harmonic_consciousness.py`](../tests/test_harmonic_consciousness.py):
  independent quadrature, degenerate-gauge, null, and input-validation tests.

Run from the repository root with Python 3.11+ and the existing dependencies:

```bash
python -m pytest -q tests/test_harmonic_consciousness.py
python -m HarmonicConsciousness.example_run
```

## Compatibility with RSI Topology

This independent research lane reuses the concepts in
[`../reports/mathematical_program.md`](../reports/mathematical_program.md) and
[`../reports/monitor_holonomy_insight.md`](../reports/monitor_holonomy_insight.md).
Its diagnostics add **no** certification tier, signed edit authorization,
identity-anchor bypass, or claim that synthetic coherence indicates awareness.
The existing `engineering_evidence` / `lineage_certified` / `holonomy_clean`
requirements continue to govern any later interaction with model edits.

## Source anchors

- OpenAI, 26 October 2026, [Working with academic communities to build
  scientific understanding](https://openai.com/index/building-scientific-understanding-with-academic-communities/).
- Luppi et al., 2023, [Distributed harmonic patterns of structure-function
  dependence orchestrate human consciousness](https://doi.org/10.1038/s42003-023-04474-1).
- Van Maldegem et al., 2025, [Connectome harmonic decomposition tracks the
  presence of disconnected consciousness during ketamine-induced
  unresponsiveness](https://doi.org/10.1016/j.bja.2024.12.036).
- Hunt and Schooler, 2019, [The Easy Part of the Hard Problem: A Resonance
  Theory of Consciousness](https://doi.org/10.3389/fnhum.2019.00378), a
  philosophical proposal whose causal claims remain hypotheses.

## HRC-FRC-01: self-designed evaluations (v0.2)

The [FRC resonance-calibration lane](FRC_CALIBRATION.md) connects the
independent `MoralityLabAI/EvalMath` feedback-channel program to this
repository's spectral geometry. It includes an exact modal-energy recurrence,
a resource-counted adaptive evaluation designer, an invisible high-frequency
failure control, and an independent squared-error readout. Source-stamped
synthetic receipts use `protocol_v0_2.json`, `frc_calibration.py`, and
`verify_frc.py`. This remains model-free `engineering_evidence`.

```bash
python -m pytest -q tests/test_harmonic_frc.py tests/test_harmonic_consciousness.py
python -m HarmonicConsciousness.verify_frc --output HarmonicConsciousness/frc_synthetic_receipt.json
```
