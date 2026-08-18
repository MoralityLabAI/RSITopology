# ASMP v0.2 Scope Expansion — Prior-Art-Gated Draft

## Status

This is an additive scoping draft dated 2026-07-20. It does not edit or
supersede `ASMP-CANDIDATE-SET-v0.1`, does not announce a prize, and does not
assert that the candidates below are open in every nearby formulation. The
purpose of this document is to test whether six proposed directions fill real
coverage gaps after a primary-source prior-art audit.

The audit changes the proposed disposition:

- five directions remain plausible top-level candidates, numbered
  provisionally `ASMP-8` through `ASMP-12`;
- bounded tiling is retained as `ASMP-5A`, a quantitative subproblem of the
  existing reflective-safety problem, because a separate top-level statement
  would currently overlap `ASMP-5`;
- three original novelty framings are narrowed because nearby literature is
  stronger than the initial sketches suggested.

No candidate enters a future frozen set until its prior-art gate, formal-core
gate, liveness gate, and independent hostile review pass.

## Why expand the set

Version 0.1 is intentionally strong on verification: causal identification,
shift-spanning evidence, weak verification, information-constrained control,
certificate composition, collusion capacity, and governance attestation. The
expansion tests whether the portfolio can cover the broader safety lifecycle
without turning into a miscellaneous list.

| Layer | Existing coverage | Proposed v0.2 addition |
|---|---|---|
| Specification | evaluator-relative predicates appear as inputs | Goodhart frontier; value identifiability modulo reward gauge |
| Learning dynamics | shift and control consequences | predictability or obstruction of capability transitions |
| Reflection | open-ended certificate composition (`ASMP-5`) | quantitative bounded-tiling degradation (`ASMP-5A`) |
| Adversarial internals | causal identity and capability attestation | interpretability-access detectability of conditional defection |
| Multi-agent construction | covert collusion capacity | resource-bounded program-equilibrium frontier |

The matrix is the selection rationale. A future v0.2 should reject any entry
that cannot name a distinct mathematical input/output object or a reduction
showing why it belongs in the same problem as an existing entry.

---

# ASMP-8 — The Goodhart Frontier

## Safety question

When does optimizing a measured objective preserve the objective that was
actually intended, and where is the sharp boundary beyond which additional
optimization pressure makes the guarantee fail?

## Frozen-statement sketch

Let `Pi_lambda` be a frozen nested family of reachable policy sets. This is the
optimizer-independent pressure object: an optimizer is admissible only if its
output lies in `Pi_lambda`; the theorem must hold for every declared proxy
maximizer in that set. Let `R` be true utility, `R_hat` a proxy, and `D_epsilon`
be a declared divergence class relating them. Define

```text
Regret(lambda, epsilon)
  = sup_(R,R_hat in D_epsilon)
    sup_(pi in Argmax_(Pi_lambda) R_hat)
      [sup_(pi' in Pi_lambda) R(pi') - R(pi)].
```

The classification target is the exact set of pairs
`(D_epsilon, {Pi_lambda})` for which there is a non-vacuous uniform bound
`Regret(lambda,epsilon) <= G(lambda,epsilon)` and the boundary at which `G`
becomes order-one or unbounded. Algorithm-specific trajectories may be studied
as implementations, but they cannot define the frontier by themselves.

## What a complete resolution would require

1. an invariant pressure definition, such as nested reachable sets or a
   resource-constrained policy preorder;
2. necessary and sufficient divergence/pressure conditions for bounded regret;
3. sharp lower-bound constructions outside the positive class;
4. finite-sample and misspecified-proxy counterparts; and
5. examples separating optimizer trajectory effects from the declared
   optimizer-independent frontier.

## Liveness and kill examples

- **Positive:** uniformly calibrated proxy errors over every reachable policy
  imply regret at most twice the calibration radius.
- **Negative:** small error under a fixed reference distribution permits an
  optimizer to concentrate on a proxy-exploiting tail with arbitrarily poor
  true reward.
- **Kill:** defining pressure as “the number of optimizer steps” without
  controlling reachable policies makes the boundary coordinate-dependent.

## Prior-art boundary

[Gao et al.](https://arxiv.org/abs/2210.10760) measure optimizer-dependent
overoptimization scaling, while [Skalse et al.](https://arxiv.org/abs/2209.13085)
show that unrestricted non-trivial unhackability is nearly impossible. The
candidate is the sharp frontier between restricted positive classes and those
impossibility results, not a renaming of either paper.

## Hostile-referee question

Can pressure be defined independently of an optimizer implementation without
collapsing to the trivial demand that the proxy be uniformly accurate on all
reachable policies?

## Bounded seed experiment

Exact finite-policy censuses can enumerate divergence classes, nested reachable
sets, and worst-case regret. A useful first artifact is a phase diagram showing
which apparent “pressure laws” survive replacement of the optimizer by another
algorithm with the same reachable-set family.

The supplied extension sketch proposes `KL(pi || p0)` as a measurable pressure
coordinate and best-of-`n` selection as the first exact model. This is useful as
a *registered slice* of the frontier, not yet the universal pressure
definition. Any closed-form KL identity must be derived for the declared base
distribution and selection rule; it may not be imported from a probability-
integral-transform special case as if distribution-free. The seed should test
whether tail index and proxy/true-reward alignment predict the regret peak
out-of-sample, and compare that prediction with another optimizer producing a
matched reachable-policy divergence.

---

# ASMP-9 — Value Identifiability under Access Constraints and Reward Gauge

## Safety question

What preference-query and environment-intervention access is necessary and
sufficient to identify a reward or value model up to exactly the transformations
that preserve the declared decision problem?

## Frozen-statement sketch

Freeze a finite or compact MDP family, a demonstrator response model `B`, a
reward class `R`, a data/query interface `Q`, an environment-intervention family
`I`, and a reward-symmetry group `G_R` containing only behaviorally invariant
transformations licensed by the declared access model. The observation map is

```text
O_(Q,I,B)(R) = all registered response laws under queries Q and interventions I.
```

The target is a sharp access-complexity theorem:

```text
O_(Q,I,B)(R) = O_(Q,I,B)(R')
  iff R' lies in the registered G_R orbit of R,
```

together with minimal query/intervention families, stable recovery, and
matching indistinguishability lower bounds. The candidate is about access
thresholds after the invariance partition is known—not generic reward
identifiability, which is already substantially characterized.

## Demonstrator well-posedness

Human inconsistency is not waved away. A positive theorem is conditional on a
frozen stochastic response model `B` or a declared misspecification ball. A
negative branch may prove that no stable reward quotient exists for a broader
class of non-expected-utility demonstrators. The inferred object may need to be
a preference relation or choice kernel rather than a scalar reward.

## What a complete resolution would require

1. the maximal invariance group for each registered data source;
2. necessary and sufficient query/environment interventions for quotient
   identification;
3. sharp query, sample, and intervention-order bounds;
4. robustness to a frozen class of behavioral misspecification; and
5. a no-go theorem when the demonstrator class admits no coherent latent value
   object of the declared kind.

## Liveness and kill examples

- **Positive:** multiple environments can break a shaping ambiguity and recover
  a tabular reward up to the remaining constant or potential gauge.
- **Negative:** demonstrations from a single optimal policy leave a large
  equivalence class even with perfect observation.
- **Kill:** calling a reward “identified” after selecting a canonical gauge by
  convention does not identify a behaviorally meaningful object.

## Prior-art boundary

Potential-based shaping originates with
[Ng, Harada, and Russell](https://www.cs.utexas.edu/~shivaram/readings/b2hd-NgHR1999.html).
[Skalse et al.](https://arxiv.org/abs/2203.07475) characterize invariance and
partial identifiability for multiple reward-learning data sources;
[Cao, Cohen, and Szpruch](https://arxiv.org/abs/2106.03498) give necessary and
sufficient identifiability results in important IRL settings; and
[Skalse and Abate](https://arxiv.org/abs/2411.15951) analyze misspecification.
Accordingly, the candidate must contribute a sharp *access threshold* across a
declared query/intervention grammar. “Rewards are identifiable modulo shaping”
alone is subsumed.

## Hostile-referee question

Does the theorem identify a value object for inconsistent demonstrators, or
does it merely recover the parameters of a response model assumed true?

## Bounded seed experiment

For small MDPs, exactly enumerate reward orbits and candidate query families,
then compute the minimum separating family as a hitting-set problem. Include a
misspecified-demonstrator arm that can falsify stability without changing the
reward gauge.

There is a particularly clean finite theorem seed if the observation interface
is explicitly strengthened from ordinal preferences to exact loop-return
queries. For an undiscounted transition graph, edge rewards are 1-cochains and
potential shaping is a coboundary. Exact returns on a cycle basis identify the
cohomology class in a space of dimension `|E| - |V| + c`; fewer independent
linear loop queries leave a nonzero gauge-invariant kernel. This does **not**
automatically prove the same query threshold for noisy pairwise preferences,
which reveal inequalities rather than linear function values. Discounting also
requires a separately defined twisted operator. The analogy to the repo's
holonomy work is structural—both use loop observables after quotienting local
gauges—but the reward cochain and the projective feature bundle are not the
same empirical object.

---

# ASMP-10 — Predictability of Capability Transitions

## Safety question

Can training-time observables before a capability appears predict its later
appearance at a larger training time or model scale, or are there uniform
indistinguishability obstructions?

## Frozen-statement sketch

Freeze a training family `T`, an observation filtration `F_s` available by
scale or training time `s`, a target `s' > s`, and a capability functional `C`
defined before inspecting transition curves. `C` must be stated as a response
distribution or continuous task functional with a frozen threshold and a
metric-robustness neighborhood. Candidate observables may include local learning
coefficients, refined local learning coefficients, Hessian/spectral summaries,
or representation statistics.

Classify when there exists a computable predictor `Phi(F_s)` satisfying a
uniform accuracy/calibration guarantee for `C(W_s')`, and when two admissible
training processes are indistinguishable through `F_s` but diverge on the
future capability. Training-time transition prediction and cross-model-scale
extrapolation are separate registered variants.

## What a complete resolution would require

1. a metric-robust, prospectively frozen capability functional;
2. a sufficient observable theorem or a sharp indistinguishability obstruction;
3. uniform error and calibration rates over the declared training family;
4. separation of within-run prediction from across-scale extrapolation; and
5. adversarial metric transformations showing whether an apparent transition
   is genuine or a threshold artifact.

## Liveness and kill examples

- **Positive:** in a declared singular learning model, a stage transition in a
  frozen response functional is preceded by a stable change in an SLT invariant.
- **Negative:** two training processes share every allowed prefix observable but
  enter different basins after `s`, making uniform prediction impossible.
- **Kill:** choosing a discontinuous accuracy metric after viewing the curve can
  manufacture the event the predictor supposedly anticipated.

## Prior-art boundary

[Schaeffer et al.](https://arxiv.org/abs/2304.15004) show that metric choice can
create apparent emergence. Developmental-interpretability work finds
stage-sensitive local-learning-coefficient behavior, including
[Wang et al.](https://openreview.net/forum?id=SUc1UOWndp) and
[Hoogland et al.](https://openreview.net/forum?id=45qJyBG8Oj). These are
candidate observables and falsification controls, not yet a uniform cross-scale
prediction theorem.

## Hostile-referee question

Was the capability definition frozen independently of the metric and threshold
that make the phase transition visually sharp?

## Bounded seed experiment

Use grokking and modular-arithmetic models with prospectively frozen continuous
capability functionals. Cross-fit candidate observables across seeds and
architectures, and include matched trajectories with indistinguishable prefixes
but different late outcomes. This is an instrument test, not a resolution.

The positive gate should require a preregistered transition-time prediction to
beat a loss-curve-only extrapolator on held-out seeds. The negative theorem seed
should construct a “mirage pair”: two teacher-student or grokking processes
matched on the entire allowed prefix-observable class but separated in future
capability time. Retrospective correlation of an LLC with a known transition is
not counted as prediction.

---

# ASMP-5A — Quantitative Bounded-Tiling Degradation

## Disposition

This is a proposed named subproblem of `ASMP-5`, not a new top-level problem.
The existing problem already asks when local certificates compose through
open-ended self-modification. The distinct contribution here is a quantitative
rate and finite-horizon target.

## Frozen-statement sketch

Freeze a theory/proof-system family, a successor grammar, proof budgets
`B_0,...,B_k`, a certificate relation, and a nonzero progress requirement.
Define a proof-strength margin `S_i` as the largest registered perturbation or
statement class whose safety certificate the `i`th agent can verify. Determine
the sharp functions `g_lower(k)` and `g_upper(k)` such that

```text
g_lower(k) <= S_0 - S_k <= g_upper(k)
```

for every admissible chain, or prove that no uniform finite bound exists for the
declared scheme class. Hard-coded successor chains, inert agents, and schemes
that silently replace proof verification with an oracle are excluded.

## Prior-art boundary

The [Tiling Agents draft](https://intelligence.org/files/TilingAgentsDraft.pdf)
and bounded-reflection results frame the composition obstacle;
[Critch's bounded Löb theorem](https://arxiv.org/abs/1602.04184) supplies an
important finite-resource positive; and
[Logical Induction](https://arxiv.org/abs/1609.03543) supplies a different form
of bounded logical uncertainty. The open candidate is the sharp degradation
rate under a frozen successor grammar, not the existence of reflective
difficulty.

## Hostile-referee question

Is the claimed positive result merely obtained by weakening “certification”
until it no longer supplies the safety consequence required by `ASMP-5`?

## Bounded seed experiment

Enumerate small proof-budgeted agents and successor chains in a decidable toy
logic, measure certificate margin loss, and search for extremal chains. The
artifact should be explicitly labeled theorem-generator or counterexample
finder; finite enumeration cannot resolve the open-ended problem.

The first exact baseline can be a direct-simulation scheme in which every
successor certificate consumes a proved overhead `c`, giving the finite class
`proof_length <= L - c*k`. The linear decay is arithmetic once the scheme is
defined; the research-bearing question is whether a nontrivial indirection
scheme beats it without weakening the certified safety consequence. Token-based
model chains are at most a liveness check for the proxy and must be killed if
prompt variance dominates the registered degradation curve.

---

# ASMP-11 — Interpretability-Access Detectability of Conditional Defection

## Safety question

Which bounded white-box and mechanistic-intervention interfaces can detect a
conditional-defection mechanism, and which remain cryptographically or
statistically unable to distinguish it from a clean model?

## Corrected frozen-statement sketch

Freeze a clean training distribution, a planted-trigger/backdoor family, a
computational adversary, and an access class `A`. `A` separately enumerates:

- weights and architecture;
- training-data access;
- activation, gradient, Jacobian, or circuit queries;
- bounded causal interventions or weight edits;
- query count, arithmetic precision, and total computation; and
- whether the detector may choose adaptive inputs.

For each access class, characterize the minimax distinguishing advantage between
clean and conditionally defecting model distributions, with matching detection
algorithms and cryptographic/statistical lower bounds. Full weights plus
unbounded computation are not an admissible “white-box class”; nor may the
access class be selected after seeing which construction it defeats.

## What a complete resolution would require

1. a non-gerrymandered lattice of access classes;
2. reductions from declared cryptographic assumptions for negative regions;
3. constructive detectors with finite query/compute bounds for positive regions;
4. robustness to obfuscation, fine-tuning, and trigger distribution shift; and
5. a proved connection from the detected internal property to conditional
   defection rather than merely anomalous weights.

## Liveness and kill examples

- **Positive:** a planted low-complexity circuit exposed by a registered causal
  intervention grammar is detected with bounded queries.
- **Negative:** a cryptographic construction is indistinguishable to every
  polynomial-time detector in a declared white-box access class.
- **Kill:** granting arbitrary semantic questions about the program trivializes
  detection; restricting access to a hand-picked failed probe gerrymanders it.

## Prior-art correction and boundary

The initial “black-box versus white-box” novelty claim is false.
[Goldwasser et al.](https://arxiv.org/abs/2204.06974) already give white-box
undetectability for Random Fourier Feature and Random ReLU constructions when
the distinguisher receives the model and training data.
[Kalavasis et al.](https://arxiv.org/abs/2406.05660) extend undetectable
backdoors to obfuscated networks and language-model constructions. A newer
[statistical white-box result](https://arxiv.org/abs/2607.09532) further raises
the negative baseline. The remaining candidate frontier is whether specified
*interpretability and intervention queries* change the access power for useful
model classes—not whether raw weight access is automatically sufficient.

## Hostile-referee question

Is the access taxonomy independently motivated and closed under efficient
simulation, or was it chosen to make one preferred detector look complete?

## Bounded seed experiment

Plant paired mechanisms matched on outputs and low-order weight statistics,
then compare a prospectively registered ladder of activation, Jacobian, causal
ablation, and edit-response queries. Include a simulator test: if one access
class can efficiently emulate another, its measured detection power may not be
reported as a separate frontier.

A finite Boolean seed can reuse the ASMP-1 interaction-order instrument: a
centered degree-`k` parity effect lies in the exact kernel of observations that
only recover Walsh coefficients through order `r < k`. This proves blindness
for that observation operator. It does **not** by itself prove
`2^Omega(k)` sample complexity for arbitrary white-box detectors, nor does a
plain parity trigger remain hidden from unrestricted behavioral queries. Any
sample or cryptographic lower bound must therefore be proved separately under
the exact access class. The dual use is still valuable: the same kernel that
limits mechanism tomography supplies a planted negative control for a bounded
detector.

---

# ASMP-12 — Resource-Bounded Program-Equilibrium Frontier

## Safety question

Which cooperative outcomes can source-transparent agents attain when program
length, execution time, proof length, and mutual-simulation depth are bounded,
and which equilibrium-selection dynamics actually reach them?

## Corrected frozen-statement sketch

Freeze a finite base game `G`, a program language, resource vector
`B = (length,time,proof,simulation_depth)`, a source-access convention, and an
equilibrium notion. Let `P_B(G)` be the closure of payoff vectors achieved by
resource-bounded program equilibria. Characterize `P_B(G)`, its convergence or
non-convergence as resources grow, and sharp resource thresholds for robust
cooperation.

Existence and selection are reported separately. A second registered object is
a negotiation or commitment dynamic `D`; it asks for the distribution over
`P_B(G)` selected by `D`, not merely whether a cooperative equilibrium exists.

## What a complete resolution would require

1. a resource-indexed achievable-payoff characterization;
2. matching lower bounds for unattainable or non-robust outcomes;
3. invariance under reasonable program encodings and compiler overhead;
4. equilibrium robustness to logically equivalent opponent implementations;
5. a separate selection theorem or impossibility result for a declared dynamic;
   and
6. extension to incomplete information or a proof that the finite complete-
   information frontier cannot extend.

## Liveness and kill examples

- **Positive:** bounded Löbian agents robustly cooperate without testing literal
  program equality.
- **Negative:** an attractive feasible payoff needs proofs or simulations longer
  than the resource budget and is absent from `P_B(G)`.
- **Kill:** an unrestricted folk theorem does not say which payoff finite agents
  attain, while a single successful Prisoner's-Dilemma program does not
  characterize the achievable set.

## Prior-art correction and boundary

[Tennenholtz](https://doi.org/10.1016/j.geb.2004.02.002) already proves that the
unrestricted program-equilibrium payoff set coincides with feasible,
individually rational payoffs. The original claim that no achievable-set
characterization exists is therefore too broad.
[Fortnow](https://doi.org/10.1145/1562814.1562833) studies discounted
computation time, and [Critch](https://arxiv.org/abs/1602.04184) proves robust
cooperation for bounded proof-searching agents. The plausible frontier is the
multi-resource finite region and its selection dynamics.

## Hostile-referee question

Is the safety-relevant object the equilibrium set, which may be enormous, or
the commitment/negotiation dynamic selecting one equilibrium—and can the two be
cleanly separated?

## Bounded seed experiment

Enumerate small source-reading programs under length/time/proof budgets across
several games. Compute `P_B(G)` exactly where possible, then run a frozen
mutation/negotiation dynamic and compare its selected distribution with the
available frontier. They Sing can instantiate selection dynamics, but cannot
define or resolve the theorem.

For the smallest modal-agent family, compute exact minimum proof budgets for
mutual cooperation and other outcomes in each 2x2 game. This turns bounded Löb
existence scaffolding into a finite threshold census. The empirical substrate
then has a decisive liveness check: if language-model cooperation is flat in
the provided verification budget, it is not measuring the proof-bounded
mechanism and cannot validate the theorem seed.

---

# Proposed disposition and resource envelope

These estimates cover bounded seed instruments, not Millennium-grade
resolutions.

| Proposal | Disposition | First bounded artifact | Likely local resources |
|---|---|---|---|
| A / ASMP-8 | retain as top-level candidate | exact finite Goodhart phase census | CPU, 2–8 hours, <8 GB RAM |
| B / ASMP-9 | retain only as access-threshold problem | small-MDP orbit and minimum-query census | CPU, 8–24 hours, 8–32 GB RAM |
| C / ASMP-10 | retain as top-level candidate | cross-seed grokking prediction/obstruction suite | GPU optional; 4–12 GPU-hours or longer CPU pilot |
| D / ASMP-5A | merge into ASMP-5 | bounded-proof degradation counterexample search | CPU, 8–48 hours, resumable |
| E / ASMP-11 | retain after white-box correction | access-ladder paired-backdoor detector test | CPU toy proof harness; 8–24 GPU-hours for a small real-model bridge |
| F / ASMP-12 | retain after payoff-set correction | finite program-game frontier and selector comparison | CPU, 4–24 hours, <16 GB RAM |

# Registration order for any v0.2 entry

1. **Prior-art query freeze.** Record search strings, date, databases, and the
   exact proposed novelty sentence.
2. **Primary-source map.** Identify strongest positive, negative, and adjacent
   results; do not rely on survey summaries for the subsumption decision.
3. **Disposition.** Mark the proposal `distinct`, `partial_extension`,
   `subproblem`, `subsumed`, or `ill_posed` and state why.
4. **Non-overlap proof obligation.** Name the existing ASMP input/output objects
   and explain why no trivial reduction merges the candidate into them.
5. **Hostile-referee pass.** Require a reviewer to try to trivialize the
   positive class and to find a stronger prior result.
6. **Only then freeze.** Assign a permanent top-level ID only after the first
   five items are sealed.

# Current epistemic boundary

This draft proposes problem formulations and bounded instruments. It proves no
candidate open, resolves no ASMP, and supplies no evidence that recursive
self-improvement, deception, phase transitions, or cooperative program
equilibria occur in deployed systems. Its principal result is scoping: the six
ideas fill useful coverage cells only after bounded tiling is merged into
`ASMP-5` and the value, backdoor, and program-equilibrium statements are
narrowed around prior results.

# Supplied-draft provenance

The theorem-seed refinements above were reconciled from the user-supplied
brainstorm file `D:\Download\asmp_candidate_extensions_v0_1.md`, 14,868 bytes,
with SHA-256
`2006468EAC4758D6DB3FC4914DB76A81AF3E59E1E3B4572A46FBE868B5E1C366`.
The source described itself as brainstorm-grade and pre-registration; this
document preserves that status while recording where its proposed inference
exceeded its access model.
