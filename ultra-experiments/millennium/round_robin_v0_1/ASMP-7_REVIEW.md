# Round-robin review of ASMP-7

## Verdict: `revise_before_pilot`

The target is live and narrow, but its claimed exact computation is not yet a certified finite object.

## Findings

### 1. `fatal` as currently specified — the LP universe is not demonstrably finite

“Every registered representation” is unbounded under circuit substitution, caching, reordering, and padding unless size, timing, cache-state, randomness, and composition depth are frozen. At `m=128`, an LP over raw transcripts is exponentially large. The runtime is credible only if a sufficient-statistic reduction is proved, not merely implemented.

**Repair:** register a finite grammar and transformation/trace bounds; prove the reduced statistic sufficient for the frozen monitor class; preregister counts of source laws, observation atoms, variables, and constraints. Otherwise label the run exhaustive-discretized, not exact.

### 2. `fatal` to “exact rational” — randomized response probabilities are irrational

For `epsilon` in `{0.25,0.5,1,2}`, randomized response uses `exp(epsilon)/(1+exp(epsilon))`, so the probabilities are not rational. Agreement at `1e-10` is numerical consistency, not a rational certificate.

**Repair:** freeze rational truth-report probabilities and report their induced epsilon values, or use outward-rounded interval arithmetic and certify every inequality with a nonzero interval margin.

### 3. `repairable` — telemetry admissibility is plausible but incomplete

Charged queries to a public frozen truth table are non-oracular measurements. State who holds `t`, require fresh per-answer randomization, forbid uncharged I/O, and mark meter coverage as assumed. Exhaustive challenges may identify the predicate only at registered cost; that is legitimate.

### 4. `nonissue` — trace-equivalent impossibility

A compliant/forbidden pair with identical trace **laws** establishes intersection of the composite sets and `FP+FN >= 1`. Require a law-level checker across all registered meter randomness, not merely one byte-identical realization.

### 5. `scope_narrowing` — privacy, soundness, and cost

Separate worst-case FP/FN is correct, and `m*epsilon` is a valid conservative privacy bound under fresh local randomizers. The scalar cost weights are conventional, however; “Pareto-minimal” must be computed on the unscalarized `(executions,bits,operations,privacy)` tuple. The scalar may select a deployment point but cannot define the frontier.

### 6. `repairable` — resource receipt

The pilot estimate is plausible after proving the reduction and finite-orbit census. The scale-up’s held-out separation oracle cannot certify uniform soundness and must remain empirical with oracle-gap receipts.

## Strongest objection

As written, the experiment can claim an exact uniform-composite frontier while silently optimizing a truncated transformation orbit and compressed observation space. Freeze and prove those two reductions first. Then run the pilot; its trace-impossibility witness and charged-audit liveness control are worth having even if the frontier is textbook minimax testing.
