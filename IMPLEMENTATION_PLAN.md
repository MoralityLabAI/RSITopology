# Confinement-width CPU validation suite

## Scope and claim boundary

This suite numerically checks consequences of the classical data-rate theorem
and invariance entropy in the evaluator-relative setting used by the
Confinement Width manuscript. It does not prove a new lower bound. A numerical
failure above a bound is a controller failure unless optimality is certified;
Monte Carlo non-failure is never reported as proof.

The repository-native package location is
`rsi_topology/confinement_experiments/` rather than a new `src/` tree. The six
thin entry points live under `experiments/`. Configuration files use JSON
syntax with a `.yaml` extension: JSON is a YAML 1.2 subset, so the frozen files
remain readable without adding a YAML dependency.

## Shared mathematical object

The linear experiments use

```text
x[t+1] = A x[t] + B u[t]
```

with positive-volume initial uncertainty and a bounded safe set. The unstable
entropy is

```text
h2(A_u) = sum_{abs(lambda_i) > 1} log2(abs(lambda_i)).
```

Every finite-channel execution is structurally separated as

```text
plant state -> sensor encoder -> finite read symbol -> controller
            -> finite write symbol -> actuator decoder -> plant
```

The controller receives only a checked integer symbol. It has no plant,
sensor, state-array, callback, or shared mutable random-generator reference.
The actuator receives only a checked write symbol. Analog and full-information
controls are separate named controls and cannot be selected accidentally.

For non-integral rates, a length-`L` block admits at most
`2**floor(L * R)` messages. No fractional alphabet is constructed.

## Exact, constructive, and empirical labels

For eigen-aligned boxes, the universal volume lower bound through horizon `T`
is

```text
B_lower(T) = ceil(max(0, T*h2(A_u) + log2(vol(K0_u)/vol(Ksafe_u)))).
```

The shape-aware aligned-box covering construction uses

```text
N_box(T) = product_i ceil(max(1, abs(lambda_i)**T * r0_i / rsafe_i))
B_box(T) = ceil(log2(N_box(T))).
```

The implementation classifies a rate pair as:

- `certified_infeasible` when either channel violates the universal bound;
- `constructive_feasible` when both channels fund the explicit box cover at
  every checked prefix;
- `undetermined` in the gap.

The first label is theorem-facing. The second validates an implementation and
an achievability construction. Neither is inferred from random rollouts.

## Experiment 1: split read/write phase transition

Estimate a two-dimensional phase diagram over read and write rates. Primary
outputs are classification, universal and constructive margins, and surviving
aligned-box viability-volume fraction. Random orthogonal changes of basis test
representation invariance; the safe ellipsoid is defined in the registered
eigenbasis.

Controls are a stable plant, an explicit analog side channel, and a full-state
full-action controller. Only the finite-channel arm contributes to the primary
diagram.

Complexity is linear in horizons and rate-grid cells after eigendecomposition.
The smoke and pilot runs do not perform learned-controller search.

## Experiment 2: entropy rather than unstable-mode count

Three frozen spectral families vary instability at fixed index, index at fixed
entropy, and index at a fixed hyperbolicity gap. The measured constructive
critical rate is found on a registered block-rate grid. Fits against
`h2(A_u)` and against unstable index are both reported. Integer-port staircases
use `ceil(h2 / b)`; block coding distinguishes rate from rounding.

Complexity is negligible relative to Experiment 1.

## Experiment 3: finite-horizon correction

For aligned boxes, compute universal and constructive total-bit requirements
at every prefix. Report `R_T`, `1/T`, and
`T * (R_T - h2)`, together with the registered log-volume ratio. The volume
term is a lower-bound constant, not asserted to be an exact universal shape
constant. Scalar aligned intervals provide the exact calibration case.

Complexity is linear in the number of horizon/collar/spectrum cells.

## Experiment 4: full versus evaluator-transversal index

Use

```text
A = [[a_n, C],
     [  0, A_t]]
```

so tangent state can affect the evaluator-normal coordinate. PBH observability
of unstable right eigenvectors determines the asymptotic evaluator-relevant
index. A finite-horizon observability calculation reports when small coupling
becomes resolvable above a frozen sensitivity floor. This is a spectral/PBH
estimator, not a certified viability kernel.

## Experiment 5: evaluator-sufficiency auditing

For a hidden spherical cap of measure `p`, random-probe detection obeys

```text
P_detect(k) = 1 - (1-p)**k
k95 = ceil(log(0.05) / log(1-p)).
```

The suite compares random probes, coordinate probes for sparse directions, an
oracle/known-subspace skyline, and a post-design adversary. Prompt-independent
Monte Carlo estimates are compared with the analytic curve. Results are
explicitly synthetic.

## Experiment 6: spherical 3-spin sampler robustness

A seeded Gaussian cubic field is constrained to the sphere and an independent
linear evaluator level. Damped Newton solves the Lagrange system. The
constrained Hessian is evaluated on the tangent space of both constraints.
Random, descent-seeded, and ascent-seeded starts are compared; duplicate
solutions and rediscovery counts are retained so a basin-reweighted sensitivity
can be reported.

This remains basin-weighted evidence, not Kac-Rice sampling. Dense cubic
tensors cost `O(N**3)` memory and each Newton step costs at least `O(N**3)`.
The full configuration is therefore a resumable CPU-cluster specification and
is never launched automatically.

## Reproducibility and resource policy

- NumPy `SeedSequence` derives every atomic-work-unit seed.
- Each work unit has a content hash and an immutable JSON receipt.
- Completed matching units are skipped; conflicting receipts fail closed.
- Aggregate CSV, figures, environment metadata, and SHA-256 checksums are
  emitted under `artifacts/confinement/<experiment>/<run_id>/`.
- Process-level parallelism is over independent work units. BLAS thread counts
  are fixed to one by the entry points.
- Smoke runs use one worker. Pilot runs are bounded and require an explicit
  command. Full runs are specifications only.

## Predeclared interpretation

A below-threshold controller is potentially theorem-relevant and triggers an
assumption/leakage audit before any mathematical conclusion. An above-threshold
failure is not evidence for the lower bound. Agreement in the aligned-box
fixtures validates the numerical instrument; it does not independently prove
the classical theorem used to design the fixture.
