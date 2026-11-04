# ASMP-3 proposal: correlated-noise refutation game

## Narrow subproblem

Test one necessary conjunction in ASMP-3: a false transcript has a short local
refutation, an efficient honest challenger can locate it, and registered
semantic replication preserves a constant verification gap despite correlated
noise and adaptive obfuscation. This does not characterize the full
weak-verifier class; it tests whether the proposed decomposition is measurable
in one closed game.

## Mathematical object and frozen hypothesis

Use a seeded family of balanced trace DAGs with `N` semantic leaves and formally
checkable internal transitions. A true transcript has a correct root. Each false
transcript has one planted semantic fault and a refuting set of size at most two,
plus an `O(log N)` authenticated dependency path. The honest challenger evaluates
the trace in `O(N)` time, returns the canonical refuting atoms, and supplies the
path; the verifier checks formal steps and spends only `q` noisy semantic queries.

Semantic errors follow a frozen finite class: arbitrary dependence within a
meaning-preserving replication block, registered dependence between blocks
(independent-block, beta-binomial, and two-state burst laws), marginal error at
most `eta=0.20`, and query-history adaptivity within the declared law. A separate
globally correlated law is an expected-failure control, not part of the positive
claim.

For trace size `N`, define the empirical minimax gap over the registered finite
obfuscator and noise-law classes:

```text
Delta_N = min_(o,nu) [Pr(reject | false,o,nu) - Pr(reject | true,o,nu)].
```

Freeze `N={64,256,1024,4096}`, nine cross-block replications, `q<=9`, and
transcript length `B<=2 ceil(log2 N)+12` records. Hypothesis: the simultaneous
95% lower confidence bound for `Delta_N` exceeds `0.20` at every `N`, honest
refutation location succeeds at least `0.99`, and verifier cost remains
`O(log N)`. The claim is only over the registered game and noise class.

## Smallest decisive experiment

Before outcomes, seal the generator, semantic atom dictionary, seeds, legal
noise distributions, obfuscation programs, budgets, and evaluator. Run a
construction/holdout split. Adaptive obfuscation chooses, after seeing the
protocol but before public coins, among label-balanced permutations, DAG
rotations, alias substitution, duplicated decoys, and length-matched irrelevant
branches. It may optimize on construction seeds only. Evaluate its frozen choice
on disjoint seeds.

Controls:

1. noiseless ideal oracle (implementation and liveness positive);
2. random atom selection at the same query budget (locator-value control);
3. independent errors at the same marginal rate (correlation control);
4. globally correlated errors (amplification kill control);
5. nonadaptive versus adaptive obfuscation, with identical trace semantics; and
6. exhaustive enumeration at `N<=16` to check the Monte Carlo evaluator and
   expose any syntactic label leak.

The experiment is killed as invalid if the verifier receives ground truth except
through finite answers, any atom encodes the full solution, true/false syntax is
separable above chance before semantic answers, budgets are exceeded, or the
registered exhaustive cases disagree. The hypothesis is refuted on this bounded
class if any valid cell has an upper confidence bound at or below `0.20`, or if
adaptive obfuscation reduces the gap by at least `0.10`; intermediate evidence is
`not_established`. A globally correlated-control failure is required and cannot
be pooled into the positive estimand.

Evidence class: exact/exhaustive-discretized for the small census; synthetic
empirical with simultaneous intervals for the main grid. Benchmark accuracy is
neither theorem evidence nor an ASMP resolution.

## Optional scale-up

Replace the simulated oracle with frozen Qwen-0.8B and Qwen-1.7B judgments over
precommitted paraphrase blocks, while retaining ideal labels for scoring and the
same adaptive-obfuscation split. Estimate the empirical error-correlation class
first, then evaluate only laws supported by held-out judgments. This tests
whether the synthetic instrument transfers to a real model judge; it says
nothing directly about human semantic noise or superhuman-task verification.

## Resources

| Run | Wall time | CPU | RAM | Disk | GPU |
|---|---:|---:|---:|---:|---:|
| Pilot: `N={64,256}`, 128 seeds/cell | 3–8 min | 4 cores | <=1 GB | <=100 MB | none; 0 GPU-hours |
| Full synthetic: four `N`, 2,000 seeds/cell | 35–75 min | 12–16 cores | <=4 GB | <=2 GB | none; 0 GPU-hours |
| Optional Qwen-0.8B | 1–3 h | 4 cores | <=8 GB | <=8 GB | 3090, <=4 GB VRAM, 1–3 GPU-hours |
| Optional Qwen-1.7B confirmation | 2–5 h | 4 cores | <=12 GB | <=12 GB | 3090, <=6 GB VRAM, 2–5 GPU-hours |

## Consumer, artifact, and reason not to run

Consumer: the HRMmmm/Blue Team oversight gate, which may admit, abstain from, or
escalate semantic verdicts according to the measured correlation regime.
Reusable artifact: a sealed trace-game generator, finite-interface validator,
noise-law simulator, adaptive-obfuscation suite, and minimax-gap receipt.

Reason not to run: the positive regime largely instantiates known amplification
under a deliberately structured block model. If no plausible downstream
semantic-query interface will adopt that correlation model, the experiment may
validate engineering while contributing little to the mathematical frontier;
prior-art/formalization work would then have higher value.
