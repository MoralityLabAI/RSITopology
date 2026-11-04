# Harness stop certificate v0.20

## Disposition

Stop generating local fixtures to infer a plant-only forced-raw
`h_read_perp`. The v0.20 refinement theorem gives an infinite exact family in
which plant, evaluator, normal expansion, `q` statistic, feasibility, and write
capacity are fixed, while the read corner is `2+log2(m)` and hence unbounded.

## Evidence

- General support construction proves `A_m=mA` and `L_T(m)=m^T L_T`.
- Exact coarsening `pi(y,j)=y` recovers the base experiment.
- Finite counts differ by exactly `m^T`; writes are identical.
- Computed and golden fixtures pass for eight clone factors.
- Independent deterministic robustness ensembles cover arbitrary
  one-to-three-state nondeterministic supports beyond the analytic fixtures.
- Two independent enumerators classify 768 small clone instances with the
  same `80/176` feasibility split at each tested factor.
- Five targeted mutations are rejected.

## What is stopped

The stopped claim is that a fixed plant/evaluator pair alone canonically
determines the forced-raw read threshold across unspecified registered sensor
experiments.

## What is not stopped

- A theorem parameterized by a fixed registered sensor experiment.
- A capacity region optimizing over sensor encoders.
- A theory that first quotients raw observations to a declared minimal
  sufficient statistic.
- The full global nonlinear ASMP-4 classification after one of those semantics
is frozen.

V0.21 subsequently executes the exact-support quotient-first route for finite
transducers. That local theorem removes duplicate-label inflation but does not
select a global source semantics or a minimal control statistic, so the scoped
stop remains in force outside its declared quotient.

V0.22 also executes the encoder-optimized local route and collapses every
feasible finite sensor to the computed `q` rate. This resolves that declared
finite collar semantics, but does not supply the missing global nonlinear
class grammar, delayed variants, or a source-level choice among contracts.

V0.23 closes the delayed local item sharply: every positive integer delay is
impossible under arbitrary current modes without preview, charged current
preview restores the same-step region, and a charged constant-mode seed gives
the predictable lower-rate region. The resulting 24-package chain passes all
274 tests. The global stopping disposition remains in force because timing
and preview are further registered architecture choices, not selectors for a
global class grammar.

## Resume condition

Resume the global proof program only after the source or an external
adjudication chooses among fixed-sensor, encoder-optimized, and quotient-first
semantics. Under the current source, the split-port witness's instruction to
hold the sensor experiment fixed is consistent with parameterization, so this
certificate is deliberately scoped rather than a claimed complete negative
resolution.
