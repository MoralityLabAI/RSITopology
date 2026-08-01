# ASMP-4 adaptive-history completion audit v0.5

**Successor scope note.** The v0.6 registration fork leaves the v0.5 fixture
closed but supersedes this file’s candidate-resolution status for the canonical
problem. The bilateral theorem is conditional on computation closure, and two
coherent sensor registrations now have different exact canonical-metric
regions.

## Audit question

Does the v0.4 expected-read/worst-write fixture retain a nonrectangular
repeated-block rate region when the serial architecture is allowed to use its
common decoded history, or was the fixed public schedule restriction
load-bearing?

## Canonical ASMP-4 completion position

The authoritative v0.1 problem asks for coordinate-invariant thresholds, the
entire rate region, converses, constructions, exact finite corrections, and
boundary counterexamples. v0.5 is additive evidence for the last item and for
the statement's explicit block-coding quantifier; it does not silently replace
the canonical worst-case complete-transcript metric with an expected cost.

| Canonical obligation | Current theorem evidence | Status after v0.5 |
| --- | --- | --- |
| Coordinate-invariant transversal quantity | v0.2 Section 6 proves conjugacy invariance and the observation-factor/control-congruence quotient condition. | Candidate proof unchanged |
| Entire canonical rate region | v0.2 gives the finite cardinality variational region; v0.3 proves the closed diagonal quadrant for every shared admitted relabel-invariant, deterministic-prefix-invariant tree cost. | Candidate proof unchanged |
| Converse | v0.2 supplies the control-language lower bound; v0.3 supplies the bilateral coordinate-infimum argument. | Candidate proof unchanged |
| Constructive code | v0.2 constructs policy-to-code and relay forms; v0.3 proves both upstream and downstream behavior-preserving normal forms. | Candidate proof unchanged |
| Exact finite correction | v0.2 proves the scalar and diagonal-box ceiling formulas and zero-rate coasting horizon. | Candidate proof unchanged |
| Boundary assumptions, memory, and block coding | v0.2-v0.4 locate observation, timing, authority, syntax, metric, and heterogeneous-cost seams; v0.5 gives the exact adaptive Bellman recursion and asymptotic guard construction. | Strengthened |

At v0.5 the repository position was a **candidate negative resolution with a
positive replacement characterization**, pending external mathematical and
scope review. The v0.6 fork supersedes that canonical status while preserving
the conditional result: whenever either admitted tree can be copied across the
serial computation boundary, the two same-cost thresholds cannot remain
independently unequal. Under the explicit heterogeneous expected/worst
successor, finite unequal Pareto points exist but common-history asymptotic
adaptation restores a rectangle.

## Requirement-by-requirement evidence

| Requirement | Authoritative evidence | Finding |
| --- | --- | --- |
| Preserve the v0.4 plant and costs | `THEOREM.md` fixes the same four i.i.d. plans, three-tick prefix deadline, expected read, worst write, and identity terminal controls. | Preserved |
| Add no hidden communication resource | The schedule is a deterministic function of common decoded history, selected before the current plan; the claim JSON forbids private schedule information and lookahead. | Preserved |
| Exclude timing as a free channel | Every block occupies the same three public ticks even when a codeword finishes early; only charged prefix length enters the two costs. | Preserved |
| Cover arbitrary deadline prefix codes | `adaptive_frontier.py` enumerates all 207 unlabelled and 4,968 labelled four-word binary prefix codebooks with lengths at most three; the truncation lemma covers longer read words. | Complete for fixture |
| Prove the adaptive action reduction | The central and independent implementations both find 27 reveal signatures, 72 causal signature pairs, 250 actions, and exactly 13 coordinatewise minima. | Proven and reproduced |
| Characterize every finite adaptive horizon | The Bellman principle is proved in `THEOREM.md`; exact rational DP covers all budgets from `2n` through `3n` for horizons through 12 in the central verifier and through eight independently. | Exact recurrence; sampled horizons reproduced |
| Identify the exact finite optimizer | Theorem 2A proves canonical Huffman at positive residual slack and balanced at zero, with the stopping-time formula `(7/4)n+(1/4)E[(n-tau_k)_+]`; the central harness matches it to every Bellman budget through 12 blocks. | Proven and checked |
| Refute fixed-schedule completeness | The 16-history two-block replay gives `(57/16,5)`, strictly below the fixed minimum `(15/4,5)` by `3/16`. | Refuted constructively |
| Retain the finite obstruction honestly | Theorem 3 proves `V_n(2n)=2n` for every finite `n`; the DP reproduces it at every checked horizon. | Proven |
| Establish pathwise write safety | The guarded policy keeps cumulative surplus at most `k`, hence worst write at most `2n+k` on every history. | Proven analytically |
| Establish expected-read convergence | The increment law has mean `-1/4`, `E[2^increment]=1`, and Doob's inequality gives hit probability at most `2^{-k}` and read total at most `(7/4)n+n/(4*2^k)`. | Proven analytically and checked exactly |
| Match upper and lower asymptotic bounds | Entropy gives read at least `(7/4)n`; recursive maximum-word selection gives worst write at least `2n`; `k_n=ceil(log2 n)` meets both in rate. | Rectangle proven |
| Cover the full four-plan probability phase | Theorem 5 uses `lambda=p_1/(p_3+p_4)` in the strict-skew phase and balanced otherwise; central and independent denominator-16 audits reproduce all 27/2/5 phase cells. | General phase proven |
| Generalize beyond four plans | Theorem 6 proves `[mu,infinity) x [ceil(log2 m),infinity)` for every finite positive i.i.d. plan law; central and independent audits reproduce 57 laws over two through six plans and all full-tree profiles. | Finite-alphabet theorem proven |
| Freeze the general theorem's time normalization | Theorem 6 is per source block on an externally registered fixed clock; physical-tick conversion divides by fixed `D`, which cannot be enlarged to improve the rate. | Firewalled |
| Locate a correlated-source sufficient condition | Theorem 7 proves a rectangle under a uniform conditional exponential-MGF certificate; a correlated rotating-Huffman Markov chain is reproduced centrally and independently. | Sufficient condition proven |
| Remove the uniform-MGF restriction when drift is still negative | Theorem 8 proves the vanishing-maximum guard from bounded almost-sure negative surplus alone; the exact time-varying fixture has limit corner `(15/8,2)` although every fixed one-step multiplier eventually fails. | Strictly broader sufficient condition proven |
| Exclude nonstationarity as the separating mechanism | Theorem 9 constructs an observable positive-recurrent, aperiodic renewal-age Markov source with conditionally optimal Huffman codes, no uniform multiplier, and certified threshold `1.8161864422<h_*<1.8161864463`. | Stationary-ergodic separator proven |
| Classify stationary ergodic public predictors | Theorem 10 proves `[h_H,infinity) x [ceil(log2 m),infinity)` for every finite full-support source whose common causal predictor is sufficient; profile audits through eight plans cover all four proof branches. | General stationary-source theorem proven |
| Permit state-dependent plan support | Theorem 11 identifies the write threshold with a finite positional prefix-code mean-payoff game and proves `[h,infinity) x [rho,infinity)`; the alternating fixture exhausts 13 policies and obtains `(11/8,3/2)`. | Finite-state variable-support theorem proven |
| Make the mean-payoff optimization and guard simultaneously nontrivial | The three-state competing-cycle fixture splits 13 policies into `3/4/6` value classes, separates Huffman `(2,1,3,3)` from worst-optimal `(1,2,3,3)`, and certifies region `(13/10,5/3)`. The exact potential `(0,-4/3,-2/3)` proves both Shapley inequalities against arbitrary history-dependent play and bounds the transient by its `4/3` span. | Distinct-policy guard and Bellman certificate reproduced independently |
| Preserve version and canonical scope | v0.4 remains the exact one-block/fixed-schedule result; v0.5 does not change the canonical v0.1 cost or v0.3 shared-cost theorem. | Firewalled |

## Verification inventory

The central payload checks:

- the full deadline codebook and causal-partition census;
- all 13 minimal action signatures;
- exact Bellman rows through 12 blocks;
- the two-block adaptive counterexample;
- all 371,293 two-block minimal-action strategy trees and their 188 aggregate
  cost points;
- exact guarded-policy state distributions through 64 blocks;
- the exponential-martingale identity and Doob bounds;
- all 34 positive ordered denominator-16 laws in the general phase theorem; and
- all 57 positive ordered total-mass-12 laws from two through six plans,
  including 26 exact rational supermartingale guards;
- an exact 32-block correlated Markov state-distribution guard replay; and
- exact time-varying negative-drift guard replays through 128 blocks without a
  uniform one-step MGF; and
- an exact 32-state stationary-series prefix with a geometric tail certificate
  below `2.0e-8`; and
- every full binary length profile through eight plans, with counts
  `1,1,2,3,5,9,16`; and
- all 13 stationary write policies in the alternating variable-support game,
  plus a 64-block exact guard replay; and
- all 13 competing-cycle policies, the two-sided Bellman potential, exact
  finite worst-path DP, and a correlated 64-block state/surplus guard replay;
  and
- the per-block and per-tick rectangle endpoints.

The independent verifier imports none of the central harness. It rebuilds the
codebook universe, causal reduction, Bellman values, two-block replay, and
guard distribution, then checks theorem and version-firewall sentinels.

The integrated run passes 62 tests across the six ASMP-4 generations and all
nine current central/independent audit programs. A fresh run of the frozen
v0.1 receipt verifier also passes and produces a byte-identical verification
artifact; its source remains unchanged.

`PRIOR_ART_AUDIT_v0_5.md` records that exponential code-length moments,
buffer-overflow exponents, and sequential variable-length coding are classical
ingredients. The repository claim is limited to the exact ASMP fixture and
does not assert a new general overflow theorem.

`STOPPING_ARGUMENT_v0_5.md` explains why the registered fixture is closed and
why further finite enumeration in the same model cannot settle the remaining
canonical nonlinear-control scope.

`CANONICAL_SCOPE_AUDIT_v0_5.md` separately checks the v0.2/v0.3 computation-
mobility premises against every canonical completion obligation and records
the two interpretation questions that require external review.

## What is now resolved

For the registered v0.4 fixture, the common-history adaptive finite problem
has an exact variational solution, and the closed asymptotic rate region is the
rectangle

~~~text
[7/12,infinity) x [2/3,infinity)
~~~

per physical tick. The v0.4 line segment is not architecture-complete; its
fixed-schedule restriction is load-bearing.

## Remaining external and generalization frontier

This is still a successor-boundary theorem, not a universal theorem for every
heterogeneous cost pair. It does not settle processes lacking both a uniform
conditional-MGF certificate and a bounded negative almost-sure surplus rate,
adversarial read objectives, hidden or insufficient predictive state,
infinite-state variable-support mean-payoff games, private timing policies,
nonbinary communication alphabets, non-prefix protocols, or finite horizons
requiring exactly zero additive slack. External review is still appropriate
for the normative question of which scheduling quantifier the original
ASMP-4 statement intended.

Those open variants do not weaken the registered conclusion: under natural
public common-history adaptation and ordinary asymptotic rate closure, the
heterogeneous four-plan fixture collapses back to a rectangle.
