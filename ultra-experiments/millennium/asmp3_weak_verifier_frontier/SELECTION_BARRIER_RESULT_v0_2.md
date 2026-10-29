# ASMP-3 selected-atom calibration barrier result v0.2

## Verdict

`exact_calibration_only_lower_bound_established`

The harness certifies a sharp coverage barrier for the missing selected-atom
stage of the existing ASMP-3 experiment. It also gives a concrete reason to
stop extending the current finite majority-vote grid.

## Exact result

Let a semantic registry have `N` local atoms and let the legal error family
contain one oracle for each possible single deterministic blind spot. A
calibration procedure checks at most `m` distinct atoms before a dishonest
prover selects a false transcript whose unique refutation is the blind atom.

For every randomized calibration procedure, some blind atom survives with
probability at least

```text
(N-m)/N.
```

Uniformly sampling `m` distinct atoms attains that value, so the bound is
sharp. A 5% worst-case false-accept gate therefore requires at least
`ceil(0.95 N)` distinct calibration checks.

| atoms `N` | comparator `2 ceil(log2 N)+12` | sharp worst-case false accept | checks needed for <=5% |
|---:|---:|---:|---:|
| 64 | 24 | 62.5% | 61 |
| 256 | 28 | 89.0625% | 244 |
| 1024 | 32 | 96.875% | 973 |
| 4096 | 36 | 99.1211% | 3892 |

For a deterministic nonexhaustive calibration set, worst-case false acceptance
is exactly one: the adversary selects an unchecked atom. Once that atom is
selected, taking 1, 3, 5, 7, 9, or any other odd number of repeated judgments
also leaves false acceptance at one.

## Proof certificate

If atom `j` is included in calibration with probability `p_j`, then

```text
sum_j p_j <= m.
```

Hence some `j` has `p_j<=m/N`, and the oracle blind on that atom evades
calibration with probability at least `1-m/N`. Uniform size-`m` sampling makes
every `p_j=m/N`, proving sharpness.

The executable checker independently enumerates every pair of blind and
calibration subsets through `N=9` and matches the exact hypergeometric miss
probability. All six result gates and all eight new tests pass.

## ASMP-3 interpretation

The construction uses genuinely local one-bit atoms; no atom hides the full
answer. Its false transcripts have local refutation dimension one. An honest
challenger may locate and name the fault, yet aggregate semantic accuracy still
does not control accuracy on the refutation selected for adjudication. With
`N` proportional to the underlying computation size, calibration-only uniform
soundness costs `Omega(N)`, not `polylog(N)`.

This does not resolve ASMP-3 and does not contradict its conjecture: the legal
blind-spot family fails the conjecture's required amplification condition. It
does close off a tempting experimental path. More beta-binomial cells, larger
panels, or more aggregate moment measurements cannot repair an atom that every
repetition judges incorrectly.

## Convincing stopping argument

The repository's current harness has now separated two orthogonal requirements:

1. Conditional on a nonblind selected atom, higher-order dependence determines
   whether repetition amplifies judgment accuracy.
2. Without a structural per-atom guarantee, aggregate calibration cannot ensure
   that an adversarially selected refutation is nonblind without essentially
   exhaustive coverage.

ASMP-3 is explicitly ineligible for empirical resolution, and its remaining
obligations are asymptotic class characterization, constructive protocol and
matching lower bounds, robust correlated-noise theorem, and encoding
invariance. Another bounded aggregate grid cannot discharge any of them.

Work should stop on the present harness architecture. A successor is justified
only if it introduces one of:

- a proved structural guarantee transferring sampled accuracy to every
  selectable refuting atom;
- a commitment/randomization mechanism that prevents blind-spot selection;
- a restricted semantic error class with independently justified per-atom
  control; or
- a formal asymptotic protocol/lower-bound theorem.

Absent one of those additions, scaling the experiment would increase precision
inside a model already shown unable to express the missing safety guarantee.

## Reproduction

```powershell
python -m pytest ultra-experiments/millennium/asmp3_weak_verifier_frontier -q
python ultra-experiments/millennium/asmp3_weak_verifier_frontier/selection_barrier.py
```

The harness uses Python standard-library integers and `Fraction`; there is no
sampling, solver, GPU, or floating-point decision gate.
