# Confinement-width CPU validation: pilot report

Date: 2026-07-16  
Protocol: `confinement-width-cpu-validation-v0.1`  
Implementation SHA-256: `dce91a403a4c248097c277fb3b03be18b78c957c000de21155b2dfd3a7956c2e`

## Outcome

The smoke configurations passed all six instrument gates. In the bounded pilot
configurations, experiments 1--5 passed their registered gates and experiment 6
failed its instrument-availability gate because only 67 of 72 registered cells
recovered at least one clean critical point. The failed gate is retained as a
stop; no spin-glass robustness conclusion is drawn from the incomplete grid.

| Experiment | Pilot result | Registered status |
| --- | --- | --- |
| 1. Split read/write rate | 2,408 primary cells: 1,148 certified infeasible and 1,260 constructively feasible; zero asymmetric-compensation violations; all three controls passed; 332 finite-horizon coasting cells | Pass |
| 2. Entropy versus unstable index | Entropy fit: slope 0.9894, R-squared 0.99949. Mode-count fit: R-squared 0.02456 | Pass |
| 3. Finite-horizon correction | Active-bound rounding residual 0.00676--0.96559; largest lower-bound-to-construction gap 3 bits | Pass |
| 4. Evaluator-transversal index | Zero coupling produced evaluator index 1; nonzero coupling produced indices 2, 3, 5, and 9; 84 finite-horizon partial-visibility cells were reported rather than coerced | Pass |
| 5. Sufficiency auditing | Maximum binomial-standardized random-probe error 2.3499 against the frozen ceiling 4.5; 54 cells retained a post-design undetected direction | Pass |
| 6. Spin-glass sampler robustness | 67/72 cells recovered critical points; five high-evaluator-level cells were unavailable | **Instrument fail** |

## Interpretation

The first pilot directly illustrates the split-channel mechanism: increasing
read capacity does not compensate for an under-capacity write interface, or
vice versa. Its red cells are certified by the registered finite-horizon volume
obstruction; its green cells have an explicit aligned-box construction. These
labels are not complements in general, and any unresolved gap must remain
`undetermined`.

The second pilot supports the manuscript's use of

`h2(A_u) = sum_{abs(lambda_i)>1} log2(abs(lambda_i))`

rather than unstable-mode count alone on the planted spectral families. This
is a numerical calibration of a classical data-rate mechanism, not a new proof.

The third and fourth pilots recover the expected finite-horizon coasting and
evaluator-transversal distinctions. The fifth quantifies the audit burden:
random fiber probing follows its analytic spherical-cap baseline, while an
occupant allowed to choose a direction after seeing the probe bank can remain
undetected whenever the bank leaves a null direction.

The sixth pilot is informative about the instrument rather than the landscape.
The unavailable cells all occur at evaluator level `tau=0.7`, across both
dimensions and multiple samplers. Increasing starts or adding continuation may
be reasonable, but doing so now would be a versioned sampler-extension study,
not a repair of this frozen pilot.

## Evidence boundary

These are seeded CPU-synthetic experiments. They do not prove the manuscript's
theorem, establish a Kac--Rice result, evaluate a trained language model, or
provide evidence of recursive self-improvement. In particular:

- a constructive failure above a lower bound is not evidence for the bound;
- Monte Carlo non-failure is not universal confinement;
- basin-weighted Newton samples are not uniformly sampled critical points;
- the full configurations remain unexecuted specifications.

## Reproducibility receipts

Every atomic work unit records a scientific identity, deterministic seed,
implementation fingerprint, payload, and result. Receipt filenames are
implementation-specific, while seeds are derived from the frozen mathematical
cell rather than the implementation hash. Thus changed code cannot silently
reuse receipts, and a renderer-only change cannot resample scientific cells.

The final audit independently recomputed 3,682 file hashes across 12 smoke and
pilot runs. Every manifest, configuration hash, and implementation fingerprint
matched its run receipt.

Primary artifacts:

- `artifacts/confinement/01_split_rate/pilot_v1/`
- `artifacts/confinement/02_spectral_entropy/pilot_v1/`
- `artifacts/confinement/03_finite_horizon/pilot_v1/`
- `artifacts/confinement/04_transversal_index/pilot_v1/`
- `artifacts/confinement/05_sufficiency_audit/pilot_v1/`
- `artifacts/confinement/06_spin_glass/pilot_v1/`

The frozen implementation plan is in `IMPLEMENTATION_PLAN.md`; the executable
gate definitions are in `protocols/confinement_validation_v0_1.json`.

## Next registered step

Do not reinterpret the failed spin-glass pilot after increasing its search
budget. If that branch is continued, create a versioned protocol and fresh run
ID that predeclare the sampler extension, minimum recovered-point count, and
comparison to the v0.1 cells. Experiments 1--5 are ready for explicit full-run
authorization; the full configurations are not launched automatically.
