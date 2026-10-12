# ASMP-9 resolution audit after v0.7

Date: 2026-07-28

## Verdict

**ASMP-9 is not resolved.**

The program now contains a connected sequence of exact results spanning
undiscounted and discounted shaping, population and finite-sample direct
comparisons, one behavioral response model, one deterministic policy channel,
and one explicit inconsistency certificate. Those results close several
finite access grammars. They do not establish the uniform statement over the
reward classes, behavioral models, data sources, and intervention families
required by the candidate problem.

## Canonical resolution obligations

The non-normative v0.2 candidate statement requires:

1. the maximal invariance group for each registered data source;
2. necessary and sufficient query/environment interventions for quotient
   identification;
3. sharp query, sample, and intervention-order bounds;
4. robustness to a frozen class of behavioral misspecification; and
5. a no-go theorem when the demonstrator class admits no coherent latent value
   object of the declared kind.

The evidence below is assessed against those five clauses rather than against
what the current experiments happened to test.

## Evidence matrix

| Layer | Authoritative evidence | What is proved | Resolution status |
|---|---|---|---|
| Undiscounted exact returns | [v0.1 audit](AUDIT_ADDENDUM_v0_1.md) | Exact fundamental-cycle returns recover edge rewards modulo ordinary potential coboundaries; `beta_1` queries are necessary and sufficient in the frozen graph grammar. | Complete only for that direct linear oracle. |
| Ordinal population access | [v0.2 summary](ordinal_frontier_v0_2/PUBLIC_SUMMARY_v0_2.md) | Query count and coefficient width are distinct resources; exhaustive narrow queries can remain non-separating. | Finite registry only. |
| Sharp comparison width | [v0.3.1](width_theorem_v0_3_1/PUBLIC_SUMMARY_v0_3_1.md) and [v0.4](zero_radius_theorem_v0_4/PUBLIC_SUMMARY_v0_4.md) | Sharp dimension-uniform coefficient widths for positive threshold ambiguity and exact ties. | Complete for bounded primitive integer reward rays under the declared sign grammar. |
| Finite-sample direct comparison | [v0.5.1](finite_sample_v0_5/PUBLIC_SUMMARY_v0_5_1.md) | Known independent sign-and-tie noise preserves the width liveness boundary; constructive upper and information lower bounds; adaptive/nonadaptive separation. | Does not cover unknown channel parameters, dependence, or behavioral observations. |
| Discounted potential shaping | [v0.6](discounted_shaping_v0_6/PUBLIC_SUMMARY_v0_6.md) | The quotient is a gain-graph incidence quotient; balanced components determine rank; finite trajectory comparisons survive shaping exactly when discounted boundary signatures match. | Complete for finite edge rewards and the declared discounted shaping operator, not for every behaviorally invariant transformation. |
| Behavioral scalar coherence | [v0.7](behavioral_wellposedness_v0_7/PUBLIC_SUMMARY_v0_7.md) | Exact population log-odds require `|V|-c` edges for promised scalar reconstruction, all non-bridge edges for coherence-only certification, and all edges for both. Hodge residuals exactly certify scalar-model failure. | One Bradley-Terry population-law specialization. |
| Deterministic policy access | [v0.7](behavioral_wellposedness_v0_7/PUBLIC_SUMMARY_v0_7.md) | A one-state intervention channel has sharp ambiguity radii `2^-k` adaptive and `1/(k+1)` nonadaptive; finite exact identification of a continuous reward coordinate is impossible. | Minimal calibration only, not general finite-MDP policy access. |

## Requirement-by-requirement audit

### 1. Maximal invariance groups

**Partially established.**

- Ordinary potential coboundaries are closed for the v0.1 edge-reward object.
- Discounted potential shaping is closed for the v0.6 gain-incidence object.
- Positive scale is explicitly quotiented in the bounded reward-ray theorems.
- Component translations, and positive scale when inverse temperature is
  unknown, are explicit in the v0.7 scalar comparison model.

Missing:

- maximal invariances for deterministic optimal policies, stochastic policies,
  trajectory demonstrations, and mixed data sources;
- entropy-regularized and transition-redistribution invariances;
- whether environment changes shrink the invariance partition uniformly; and
- a single theorem relating the registered source-specific groups rather than
  listing separate special cases.

### 2. Necessary and sufficient query/intervention access

**Partially established.**

The suite has sharp access theorems for exact loop returns, bounded sign
comparisons, one known noisy sign channel, discounted boundary-matched
trajectory functionals, exact pairwise log-odds, and a one-dimensional policy
threshold oracle.

Missing:

- general finite-MDP policy and demonstration observations;
- multiple transition kernels or discount factors;
- joint use of preference, policy, and intervention data;
- adaptive environment selection beyond scalar threshold interventions; and
- necessary and sufficient access over a nontrivial registered MDP family.

### 3. Sharp query, sample, and intervention-order bounds

**Partially established.**

Coefficient width is sharp in v0.3.1 and v0.4. Version v0.5.1 gives a
constructive finite-sample upper bound, a Fano lower bound, and a sharp
nonadaptive Farey coverage obstruction. Version v0.7 gives sharp adaptive and
nonadaptive policy-threshold approximation rates.

Missing:

- tight finite-sample constants for estimated behavioral response laws;
- sample bounds with unknown response parameters;
- dependent-response and sequential-demonstration bounds;
- intervention-order bounds in a general MDP; and
- stability bounds after estimating both the demonstrator and reward quotient.

### 4. Behavioral misspecification robustness

**Not established at resolution scope.**

Version v0.7 detects exact cycle inconsistency and quantifies its closest
unweighted scalar projection. That is a model-checking theorem, not a
robustness theorem. The frozen v0.2 half-unit threshold perturbation is an
adversarial oracle model, not human-model misspecification.

Missing:

- finite-sample confidence regions for the Hodge residual;
- tolerance to unknown link functions and inverse temperature;
- contextual, history-dependent, and correlated responses;
- declared misspecification balls with downstream reward-error guarantees; and
- conditions under which the inferred object should be a choice kernel or
  preference relation rather than a scalar reward.

### 5. No-go for incoherent latent values

**Established for one narrow class; open generally.**

A nonzero pairwise log-odds circulation is an exact witness that no scalar
Bradley-Terry value generates the registered response law. The deterministic
policy arm also proves that finite action observations cannot exactly recover
an arbitrary continuous quotient coordinate.

Missing:

- no-go theorems for broader stochastic-choice and non-expected-utility
  demonstrators;
- contextual preference reversals where a context-indexed scalar might still
  exist;
- dependent demonstrations in which marginal pairwise coherence is
  insufficient; and
- a decision rule for when to stop scalar inference and report a richer
  preference object.

## Highest-value next sequence

### v0.8: unknown response-link frontier

Separate three cases prospectively:

1. known Bradley-Terry link and known inverse temperature;
2. known link with unknown positive inverse temperature, which should collapse
   to the already-registered positive-scale gauge at population level; and
3. unknown strictly increasing symmetric link, for which complete pairwise
   probabilities can still fail to identify a utility ray.

The decisive object is an explicit pair of non-affinely-related utility
vectors with separate admissible links that induce the same complete response
law. This directly attacks the unresolved response-parameter clause.

### v0.9: finite-sample coherence certification

Estimate edge log-odds from binomial comparisons, carry simultaneous intervals
through a cycle basis, and predeclare:

- a coherent null;
- a planted circulation alternative;
- graph-dependent sample complexity;
- multiple-testing control over the registered cycle basis; and
- an `inconclusive` region rather than treating failure to reject as scalar
  coherence.

### v0.10: general finite-MDP intervention access

Freeze a finite tabular MDP class and compare:

- one optimal policy;
- stochastic policy probabilities;
- multiple transition kernels;
- multiple discount factors; and
- trajectory preferences.

The target should be the exact rank or polyhedral dimension of the remaining
reward quotient, explicitly positioned below existing general identifiability
results.

### v0.11: richer-demonstrator no-go

Construct a declared contextual or history-sensitive choice class for which:

- every context separately admits a scalar;
- no shared scalar exists;
- a context-indexed preference kernel does exist; and
- the observation map cannot distinguish the shared-scalar and
  context-indexed hypotheses below a sharp access threshold.

## Completion criterion

The goal cannot be marked complete merely because every row has a bounded
example. A defensible resolution requires a frozen family of data sources and
behavioral models broad enough to make the quantifiers meaningful, a maximal
invariance characterization for each source, matched upper and lower access
bounds, a misspecification theorem, and a two-sided scalar-existence/no-go
classification. Current evidence does not meet that bar.
