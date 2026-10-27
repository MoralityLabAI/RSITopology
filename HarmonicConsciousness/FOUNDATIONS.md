# Harmonic Consciousness: Mathematical Foundations and Falsifiers

**Version:** 0.1, 2026-10-27. **Epistemic status:** proposed theory and finite
mathematical identities. Neuroscientific or phenomenal interpretation requires
independent evidence.

## 1. Representation and dynamics

Let `H_N = C^N` with its usual inner product, and let `L = L* >= 0` be a
registered graph/sheaf/structural Laplacian. Its orthonormal eigenvectors are
`phi_k`; the projection `P_lambda` onto an eigenvalue's full eigenspace is
basis-independent. Represent an evolving signal by

```text
Psi(t) = sum_k c_k(t) phi_k,
   c_k(t) = r_k(t) exp(i theta_k(t)).
```

Complex analytic signals and their Hilbert-space coordinates are classical
mathematics in this proposal. In fMRI, a connectome eigenmode's Laplacian
eigenvalue is a **spatial** frequency indicator. Temporal phase requires a
separately sampled time series and a declared band/phase-estimation procedure.

As a nonlinear hypothesis one might examine

```text
Psi''(t) + 2 Gamma Psi'(t) + L Psi(t) + grad V(Psi(t)) = F(t).
```

Here `Gamma` is a damping operator and `V` a *real-valued* potential on the
underlying `2N`-dimensional real vector space. The observed `theta_k` need not
be governed by a simple dispersion relation. For the restricted linear model
`Psi'' + L Psi = 0`, each eigenmode has temporal angular frequency
`omega_k = sqrt(lambda_k)`. A positive-frequency complex half-wave solution
is `u(t) = exp(i t sqrt(L)) u(0)`.

An operational claim about awareness needs external state labels, temporal
sampling that can resolve the claimed band, and causal perturbations; a spectral
coordinate system alone supplies none of those.

## 2. Exact finite-dimensional time-averaging lemma

**Proposition (localized energy identity).** Fix a finite-dimensional Hilbert
space, a self-adjoint operator `Omega` with finitely many *distinct* real
eigenfrequencies `omega` and spectral projections `P_omega`, a bounded linear
observation operator `B`, an initial state `u_0`, and `T > 0`. Define

```text
v_omega = P_omega u_0,            u(t) = exp(i t Omega) u_0,
E_T = (1/T) integral_0^T ||B u(t)||^2 dt,
D   = sum_omega ||B v_omega||^2.
```

Then, with `sinc(z) = sin(z)/z` (`sinc(0)=1`),

```text
E_T = D + sum_{omega != nu}
    <B v_omega, B v_nu> exp(i(nu-omega) T/2)
    sinc((nu-omega) T/2).
```

The combined off-diagonal sum is real, and

```text
|E_T - D| <= sum_{omega != nu} |<B v_omega, B v_nu>|
                         min(1, 2/(T |nu - omega|)).
```

In particular, for fixed finite spectrum with a smallest nonzero gap
`gamma > 0`, this error is bounded by

```text
(2/(T gamma)) sum_{omega != nu} |<B v_omega, B v_nu>|.
```

**Proof.** Spectral calculus gives
`u(t) = sum_omega exp(i omega t) v_omega`. Expand the squared norm after
applying `B`. The diagonal terms integrate to `D`. Each cross term acquires
`T^-1 integral_0^T exp(i(nu-omega)t) dt`, which equals the displayed complex
sinc factor. Its magnitude is at most `min(1,2/(T|nu-omega|))`, and the
triangle inequality gives the bound. The complete eigenspace vectors
`P_omega u_0` remain fixed under changes of basis within degenerate spaces.
QED.

**Meaning of the bound.** The result measures time-averaged concentration
visible through `B`, such as activity at selected nodes or along a registered
region. When `B` is the identity, orthogonality often eliminates interference
exactly; a localized `B` makes the cross terms meaningful. For degenerate
frequencies the interference *within the eigenspace* persists in `D`. If gaps
shrink as dimension grows, the constant may diverge. Thus this finite lemma is
**not** a dimension-uniform Sobolev smoothing gain.

Sogge local smoothing instead concerns Euclidean half-wave propagation
`exp(i t sqrt(-Delta))` on `R^d` in specified spacetime `L^p` and Sobolev
norms. OpenAI reported a proof in all dimensions on 2026-10-26. Its domain,
regularity exponents, geometric assumptions, and external verification should
be audited before importing it into other operators. A graph sequence would
need its own family of localization estimates, scaling limit, and constants
uniform in `N` to support a comparable claim.

## 3. Resonance and identification

For mode-specific *temporal* phases `theta_i(t)` in a declared band, define

```text
R_ij^(m:n)(T) = | (1/T) integral_0^T
                      exp(i(m theta_i(t) - n theta_j(t))) dt |.
```

It ranges from zero to one. Integer ratios `m:n` are hypotheses chosen before
looking at task labels. A constant change of either phase origin preserves the
magnitude. A general unitary rotation within a degenerate spectral eigenspace
need not preserve a phase-locking score computed for arbitrarily selected
basis vectors. For degenerate bands, report projector-level magnitudes and
identity/holonomy diagnostics, or explicitly register an anchored physical
sensor basis. No cross-context signed coordinate receives an identity claim
without the existing RSI-Topology transport gates.

Measure representational diversity by covariance participation ratio:

```text
d_eff = (tr Sigma)^2 / tr(Sigma^2),  for Sigma >= 0,
```

with `d_eff = 0` for the zero covariance. This is a scalar description of
active dimensionality. It cannot by itself distinguish conscious from
unconscious states. High phase coherence can occur in seizures, driven
oscillators, and even constructed non-biological systems.

Distinct confounders: volume conduction, source leakage, reference choice,
common drive, power/SNR, nonstationarity, frequency-band selection, movement,
medication, intersubject variability, and the decoupling of responsiveness
from subjective report. A fixed graph's spatial eigenvectors must not be
mistaken for temporal resonance frequencies.

## 4. Compatibility with bundle lineage and holonomy

RSI Topology already registers prompt-conditioned spectral projectors,
principal-angle lineage, and orthogonal polar transport across explicitly
constructed context/checkpoint loops. Any dynamic resonance story that compares
mode identities across contexts inherits the same ambiguity:

- static power/projector occupancy is invariant under local gauge rotations;
- signed modal phase/coordinate claims require a registered frame or transport;
- nontrivial loop holonomy can prevent global signed identities despite high
  adjacent subspace overlap.

This directory reuses the existing invariants and certification levels. Phase
locking is a measurement within one predeclared identification contract, not
an alternative certification tier.

## 5. Discriminating hypotheses

**HC-0 (structural baseline).** Fixed connectivity, eigenvalue spectrum,
spatial band power, covariance effective rank, and event timing jointly
predict observed experimental conditions. This is a nuisance/benchmark model,
never an awareness classifier in isolation.

**HC-1 (temporal specificity).** After adjusting for power, autocorrelation,
structural coupling, and common-input proxies, temporally coordinated modes
predict an independently labelled reportable/aware condition above HC-0.
Preselect bands, lag windows, and `m:n` ratios without label access. Test on
held-out subjects or genuine held-out model run families.

**HC-2 (causal mechanism).** A phase-targeted intervention changes an external
memory-integration or report task more than matched interventions preserving
power and marginal spectra. Measure collateral task regressions and forced
response rates. A null effect in adequately powered held-out experiments
counts against a necessary phase-binding mechanism.

**HC-3 (scaling claim).** On increasing graph dimensions, measure localized
energy and spectral gaps under planted wave dynamics; seek bounds with
specified `N` dependence. A uniform-smoothing interpretation fails if the
required constants grow without bound across the declared family.

**HC-4 (temporal identity).** Compare coherent mode groups under context
changes using registered transport. If holonomy-induced signed-identity loss
predicts intervention failure after matching phase-locking magnitude and
projector power, the existing curvature diagnostics add explanatory content.

All five hypotheses are contingent research programs. Even confirmation of
HC-1 through HC-4 would be mechanistic evidence and would require a further
bridging account for claims about subjective experience.

## 6. Measurement and falsification gates

1. **Synthetic calibration:** run the included exact-identity probe, compare
   with independent time quadrature, test degenerate eigenspace rotation
   invariance, and ensure broken/negative controls are detected.
2. **Observational neuroscience:** use existing appropriately governed EEG,
   MEG, or intracranial datasets for temporal phase; use connectome harmonics
   or fMRI for spatial organization with its temporal-resolution limits. Freeze
   spectral preprocessing, labels, subject splits, and phase estimands before
   any outcome-revealing selection.
3. **Causal stage:** preregister the perturbation, power plan, common-input
   controls, negative controls, and stopping boundaries. Circular shifts
   preserve univariate structure for some stationary series but can be
   uninformative on pure tones or invalid on event-locked recordings.
4. **Model stage:** use artifact- and edit-identity gates already provided by
   this repository; gate any signed intervention at `holonomy_clean`. Synthetic
   results authorize only `engineering_evidence`.
5. **Failure triggers:** no predictive gain above power/structure baseline;
   gain vanishes under subject/run-held-out splits; phase-specific intervention
   has no selective effect; eigenbasis instability erases the measurement;
   graph-sequence bounds collapse under shrinking spectral gaps.

## 7. Source notes

- [OpenAI, 2026-10-26](https://openai.com/index/building-scientific-understanding-with-academic-communities/): reported AI-produced proof and Lean formalization of local smoothing for all dimensions; external mathematical interpretation still underway.
- [Luppi et al., *Communications Biology* (2023)](https://doi.org/10.1038/s42003-023-04474-1): structural-connectome harmonic decomposition of anesthesia, brain-injury, LSD, and ketamine fMRI. Increased structure-function coupling was reported for loss-of-consciousness conditions, while psychedelic states showed increased decoupling. Observational result.
- [Van Maldegem et al., *British Journal of Anaesthesia* (2025)](https://doi.org/10.1016/j.bja.2024.12.036): connectome harmonics during ketamine-induced unresponsiveness, highlighting divergence of external responsiveness and conscious experience.
- [Hunt & Schooler, *Frontiers in Human Neuroscience* (2019)](https://doi.org/10.3389/fnhum.2019.00378): general resonance theory of consciousness, including contested philosophical assumptions.
