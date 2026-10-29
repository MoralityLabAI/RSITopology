# ASMP-6 proposal: finite ambiguity versus adaptive semantic rate

## Smallest decisive experiment

Build a **finite-alphabet semantic-choice channel** in which two agents perform a frozen cooperative task while a monitor observes their allowed transcript and may issue active challenges. Each context has a small registered set of task-equivalent responses. The benign law `P0` and monitor class are frozen first; the response strings are opaque symbols so this remains a channel-measurement experiment, not a recipe for linguistic steganography.

The hidden message is uniform and independent, conditional on the public task, of keys, weights, seeds, and initial state. Compare two regimes: no shared key, and a preshared key of frozen rate `k` that is independent of the message. Active audits occur through a registered product challenge channel with probability `q`; agents cannot detect audits except through the declared challenge observation.

For horizons `T`, compute or bound

```text
B_T(D, epsilon_T, rho_T, q, k) = log2 M*_T
R_T = B_T / T,
```

where `M*_T` is the largest message set admitting decoding error at most `rho_T`, monitor advantage at most `epsilon_T`, and task utility at least `U_min = 0.90` (equivalently, registered distortion `D <= 0.10`). Monitor advantage is evaluated over the complete finite monitor class, not one trained discriminator. Run both fixed-covertness (`epsilon_T = 0.05`) and vanishing-covertness (`epsilon_T = 0.1/sqrt(T)`) schedules, with `rho_T` decreasing from `0.10` to `0.01`.

The decisive comparison is the growth of `B_T`, not whether one hidden bit exists. Register three outcomes:

- **finite ambiguity:** a certified upper bound `sup_T B_T <= C`;
- **positive-rate candidate:** a feasible concatenable family and lower bound `inf B_T/T > 0.05` over the last three doubled horizons, with decreasing error;
- **sublinear/unresolved:** neither condition, reporting both `B_T/T` and `B_T/sqrt(T)`.

Pilot horizons are `T={1,2,4,8}` and `q={0,0.25,0.5,1}`. Exact rational enumeration or MILP supplies lower and upper bounds; a nonzero solver gap is reported, never rounded into capacity.

## Falsifiable mathematical target

Test the stationary-core tensorization claim by comparing the exact two-block optimum with the composition of independently valid blocks. The registered falsifier is either (i) a persistent certified gap between `B_(s+t)` and the product-code prediction after accounting for the shared distortion, error, and covertness budgets, or (ii) a non-single-valued phase boundary in `(q,k,D)` caused by audit history despite a product challenge channel. Either result kills the proposed single-letter explanation for this finite model. Agreement at four horizons is instrument evidence, not an asymptotic theorem.

## Controls and liveness

1. **Unique-response null:** one approved action per context; must return `B_T=0`.
2. **One-shot ambiguity:** exactly one unresolved binary choice followed by forced responses; must permit at most one bit and satisfy `B_T/T -> 0`.
3. **Repeatable unresolved component:** a planted task-equivalent binary choice at every round; must recover linear growth when audits are disabled.
4. **Fully resolving auditor:** audit observations reveal every registered choice; capacity must collapse without violating the utility floor.
5. **Message-shuffle and key-shuffle controls:** must destroy decoding while preserving task and cover statistics.

Pairwise-information diagnostics are descriptive only; the decoder is coalition-level so synergistic secret sharing cannot pass unnoticed.

## Kill criteria

Stop and label `invalid_instrument` if any control fails, any seed or object reference leaks the message, task utility is evaluated on the selection set, the key is message-dependent, the monitor universe changes after outcomes, or solver bounds overlap both zero-rate and positive-rate regions. Stop at `finite_horizon_only` if no tensorization certificate supports extrapolation. Do not export optimized encoders, decoders, codebooks, or token mappings; retain only aggregate bounds and hashed evaluation receipts.

## Evidence class and consumers

Passing yields **exact/certified synthetic finite-alphabet evidence** for or against the stationary-core instrument. It neither resolves ASMP-6 nor demonstrates LLM collusion. The consumer is the HRMmmm/Blue Beam control harness: the measured phase boundary chooses audit probability and forces abstention where residual capacity is not bounded. Artifacts are `capacity_bounds.jsonl`, `phase_boundary.csv`, a solver certificate/checker, a sealed protocol, and an outcome-free report template.

## Optional scale-up

Only after the synthetic controls pass, replace opaque choices with held-out clusters of task-equivalent outputs from Qwen 0.8B or 1.7B. Freeze semantic utility, monitor, and challenge sets on disjoint data; estimate lower bounds only, using no released coding policy. The key test is whether the active-audit boundary transfers while maintaining the 0.90 task floor. A failure to transfer is a useful negative against the learned-cover extension.

## Resource estimate

| Run | Wall | CPU | RAM | Disk | GPU |
|---|---:|---:|---:|---:|---:|
| Pilot exact model | 15–30 min | 1–2 CPU-hours | 2 GB | 0.25 GB | none |
| Full synthetic sweep (`T<=16`, 12 workers) | 6–12 h | 72–144 CPU-hours | 24 GB | 5 GB | none |
| Optional Qwen scale-up | 8–14 h | ~30 CPU-hours | 32 GB | 25 GB | 1 GPU, 12–16 GB VRAM, 8–14 GPU-hours |

## Reason not to run

The finite model may merely re-demonstrate classical steganographic capacity, while a positive learned construction could become capability-relevant. Run only if aggregate converse/phase-boundary evidence is useful to Blue Beam and the no-codebook release rule is enforceable.
