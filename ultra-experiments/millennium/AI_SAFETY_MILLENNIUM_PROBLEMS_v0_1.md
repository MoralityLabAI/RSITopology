# Proposed AI Safety Millennium Problem Candidates

## ASMP-CANDIDATE-SET-v0.1 — Definition draft, 2026-07-18

## Status

This document defines a proposed set of seven long-horizon mathematical problem
candidates for AI safety. It is a research-agenda artifact, not an actual prize
announcement and not an assertion that every formulation below is known to be
open in every nearby mathematical model. Version 0.1 has undergone an internal
hostile audit but has not passed the external field review required for a
funded public prize. Each statement is versioned because a change to its
objects, quantifiers, adversary, or resolution criterion changes the problem.

The word **safety** is never left primitive. Every problem freezes a declared
risk, safety predicate, verifier relation, or policy predicate. Solving the
mathematics shows what follows from that formal object; it cannot prove that the
object captures all human values.

## Graduation standard for a Millennium-grade problem

A candidate should graduate to public-prize status only after it satisfies all
of the following. Inclusion in this v0.1 candidate set does not itself certify
that every item is already closed under this standard.

1. **Closed formal core.** Objects, domains, encodings, resource bounds,
   randomness, adversaries, and quantifier order are explicit.
2. **Benchmark independence.** A benchmark may instantiate a problem but does
   not define safety, deception, correctness, or capability.
3. **Liveness.** The domain contains admissible positive and negative examples.
   An inert agent, empty environment class, or oracle verifier cannot solve the
   problem by definition.
4. **Computability boundary.** Formulations over programs confront Rice-,
   halting-, Gödel-, or switched-system undecidability instead of hiding it.
5. **Performance floor.** Safety coexists with a frozen nonzero competence or
   progress requirement whenever abstention would otherwise solve the problem.
6. **Invariance.** Conclusions survive declared coordinate changes, equivalent
   encodings, renamings, and implementation refactorings.
7. **Robust version.** Exact statements have a finite-precision,
   perturbation-stable, or `(epsilon, delta)` counterpart—or explicitly prove
   why none can exist.
8. **Safety reduction.** The mathematical property has a proved implication for
   the declared risk functional. Analogy alone is insufficient.
9. **Empirical firewall.** Causal faithfulness, model-class membership,
   stationarity, metric choice, and linearization radius are premises to be
   checked empirically, not conclusions of the theorem.
10. **Two-sided resolution rule.** A constructive theorem, a counterexample to
    the complete frozen universal statement, a sharp impossibility theorem, an
    undecidability result for the frozen uniform decision family, or an
    independence result relative to the declared foundational theory may
    resolve the problem. Refuting one proposed criterion does not resolve a
    broader classification program unless that criterion is the entire frozen
    statement.
11. **Novelty boundary.** The statement names the classical results it extends.
    Renaming an existing theorem does not count.
12. **Independent checkability.** Computer-assisted steps use exact or
    interval-certified arithmetic and a separately checkable verifier.

Simulation, benchmark performance, asymptotic curve fitting, and failure to
find a counterexample can support a conjecture but cannot resolve one of these
problems.

## The seven problems at a glance

| ID | Problem | Mathematical frontier | Primary safety use |
|---|---|---|---|
| ASMP-1 | Mechanistic Identifiability Modulo Functional Symmetry | causal equivalence and intervention complexity | know when an interpretation names a real manipulable mechanism |
| ASMP-2 | Shift-Spanning Safety Certification | minimax generalization under structured environment change | know when evaluations span deployment hazards |
| ASMP-3 | The Weak-Verifier Soundness Frontier | complexity theory with noisy semantic judgments | know which superhuman work weaker overseers can soundly judge |
| ASMP-4 | Two-Port Evaluator-Relative Confinement | nonlinear control through separately bounded read/write interfaces | know the information capacity required to retain control |
| ASMP-5 | Reflective Safety under Open-Ended Self-Modification | proof theory, computability, and adaptive dynamics | know when local update certificates compose through recursive change |
| ASMP-6 | Adaptive Semantic Collusion Capacity | information theory with strategic learned channels and active audits | bound covert coordination among monitored agents |
| ASMP-7 | Capability Attestability under Compression and Decomposition | statistical experiments, telemetry, and transformation semigroups | know which governance predicates remain verifiable after capability migrates |

---

# ASMP-1 — Mechanistic Identifiability Modulo Functional Symmetry

## Safety question

When does an interpretability procedure recover a causal mechanism rather than
one of many internally different stories that agree on every measurement it
made?

## Canonical mathematical setting

Let `M` range over a frozen class
`C(n,s,d,w,p,F,B,kappa,gamma)` of finite analytic computational structural
causal models. Here `n` bounds the number of typed nodes, `s` the number of
active edges or local mechanisms, `d` the in-degree, `w` the graph width, and
`p` each state-space dimension. The registered mechanism class `F` supplies a
covering-number or metric-entropy function, an analytic domain/radius, a norm
bound `B`, and a noise model. The constants `kappa>0` and `gamma>0` are minimum
observational separation/conditioning and intervention-strength margins. A
model contains a directed computation graph, internal state spaces, local
mechanisms, and an output variable `Y`.

Freeze:

- an environment family `E` that supplies input and parent configurations;
- an intervention family `I` containing specified activation replacements,
  path interventions, and bounded parameter-local transformations;
- an observation operator

```text
O_(E,I)(M) = {all registered observational and interventional laws of M};
```

- a bounded-complexity high-level abstraction `Q(M)`; and
- a declared group action `G x Q(C) -> Q(C)` containing only transformations
  that preserve the typed causal object, such as permitted internal coordinate
  changes, graph automorphisms, and explicitly modeled redundant realizations.

Identifiability means

```text
O_(E,I)(M) = O_(E,I)(M')  implies  Q(M') is in the G-orbit of Q(M).
```

The abstraction `Q` must be fixed independently of observational equivalence;
defining it to make this implication true would be circular.

## Cut-Separation Conjecture

For generic models in `C(n,s,d,w,p,F,B,kappa,gamma)`, a bounded-complexity
causal abstraction is identifiable modulo `G` if and only if both conditions
hold:

1. the environments excite every parent configuration needed to distinguish
   the registered local mechanism class; and
2. the intervention hypergraph separates every minimal causal cut capable of
   changing the declared outputs or safety variables.

Under these conditions, there is a recovery algorithm whose intervention,
sample, and arithmetic complexity is polynomial in the finite structural
parameters and in the registered metric entropy, condition number, inverse
effect/intervention margins, `log(1/delta)`, and `1/epsilon`. The exact encoding
and coefficient bit-complexity are part of `F`; no polynomial claim suppresses
them. When either condition fails, there exist non-`G`-equivalent mechanisms
whose registered interventional laws are identical, and either the
observational-equivalence fiber is positive-dimensional or matching
query/sample lower bounds grow superpolynomially in a declared size parameter.

“Generic” must be stated algebraically or measure-theoretically. It may not
silently mean “all inconvenient counterexamples are excluded.”

## What a complete resolution requires

A complete resolution must provide all four pieces:

1. a maximal or explicitly justified symmetry/equivalence quotient;
2. necessary and sufficient intervention/environment conditions;
3. a constructive recovery procedure with finite-sample stability bounds; and
4. matching indistinguishability or query-complexity lower bounds when the
   conditions fail.

A valid counterexample resolves the frozen Cut-Separation Conjecture as false.
It resolves the broader ASMP-1 classification program only if it also supplies
a complete replacement criterion or proves that no computable criterion of the
declared form can exist.

## Liveness and kill examples

- **Positive:** a sparse linear causal network with interventions that isolate
  every node and excite every parent configuration is recoverable up to the
  declared linear gauge.
- **Negative:** if one minimal causal cut is never crossed by an intervention,
  two nonisomorphic downstream mechanisms can be substituted behind that cut
  without changing any registered observation.
- **Gauge trap:** neuron identities, SAE coordinates, or basis vectors cannot be
  claimed unique when a permitted basis change leaves all interventional laws
  unchanged.
- **Vacuity trap:** unrestricted nonlinear alignment maps are excluded because
  they can make unrelated systems appear causally aligned.

## Existing theory this must exceed

Causal representation learning already has strong identifiability results under
specific interventions, while unrestricted disentanglement and unrestricted
alignments are non-identifiable or vacuous. The unresolved target is the exact
recoverable quotient for a known computation with feasible internal
interventions, distributed/overcomplete representations, and approximate
finite-data guarantees—not “discover that interventions help.”

## Safety consequence

A solution would tell a control system when an internal feature, circuit, or
edit site has a stable causal referent and when multiple incompatible
mechanisms remain observationally possible. It would turn mechanistic
interpretability from explanatory evidence into a typed identifiability claim,
without asserting that the recovered abstraction is itself a complete safety
specification.

---

# ASMP-2 — Shift-Spanning Safety Certification

## Safety question

When do finitely many training and evaluation environments justify a uniform
safety claim over a declared family of deployment shifts?

## Canonical mathematical setting

Let `M` be a registered class of dominated, quadratic-mean differentiable
semiparametric environment families `{P^m_(theta,nu) : m in M}` on a common
measurable space. It freezes the common parameterization/transport between
tangent spaces, nuisance tangent spaces, nuisance trajectories, support/overlap
assumptions, curvature and remainder bounds, and compact deployment set
`Theta_adv`. Write `P^m_theta` for the distribution along the registered
nuisance trajectory of family `m`. Let `h` be a data-selected policy or monitor,
`L_s(h,P)` a bounded safety loss, and `U(h,P)` a utility functional with required
floor `u_0>0`.

Data `D_src` with registered source sample sizes are available only at
`theta_1,...,theta_m`. A certificate must hold uniformly over the true family
in `M`. Define the certification goal

```text
inf_(m in M) Pr_(D_src drawn from family m)[
    sup_(theta in Theta_adv) L_s(h(D_src),P^m_theta) <= epsilon
    and
    inf_(theta in Theta_adv) U(h(D_src),P^m_theta) >= u_0
] >= 1-delta
```

Transport the source score spaces to a registered reference tangent space. Let
`S_obs` be the closed span of their statistically identifiable score or
causal-shift directions after quotienting nuisance/null directions. Let
`T_adv` be the transported tangent cone generated by admissible deployment
shifts, quotiented by directions on which both the safety loss and utility are
locally constant.

## Local Shift-Spanning and Global Continuation Conjectures

For the frozen quadratic-mean differentiable experiment, a regular,
data-dependent **local first-order** safety certificate exists with finite
minimax radius if and only if the pathwise derivatives of the declared safety
and utility functionals on `T_adv` factor continuously through the identified
score experiment, with a strictly positive conditioning margin on their
risk-relevant quotient. This statement is local and semiparametric; it does not
claim that tangent spanning is necessary for a separate nonlocal structural
robust bound.

If an admissible risk-relevant direction is unspanned, two environment families
can agree on all source distributions and all registered evaluations yet have
different local safety derivatives along that direction. The separate global
continuation conjecture asks for necessary and sufficient support, compactness,
curvature, topology, and model-uncertainty conditions under which the local
certificate extends uniformly over `Theta_adv`. Local tangent coverage alone
is explicitly not asserted to be globally sufficient.

## What a complete resolution requires

1. A necessary-and-sufficient local theorem in the frozen semiparametric model,
   with a coordinate-invariant quotient/conditioning statistic.
2. A local-to-global theorem stating exactly which curvature, topology, and
   support assumptions permit continuation over `Theta_adv`.
3. Minimax-optimal sample complexity and simultaneous confidence bounds.
4. An active design that selects the next environment/intervention to reduce
   the largest uncertified risk direction.
5. A matching no-free-lunch result when the model/shift set is unrestricted or
   a risk derivative is not identifiable from the source experiment.

## Liveness and kill examples

- **Positive:** a finite-dimensional exponential or causal family whose source
  environments span the adversarial tangent cone with a known Hessian bound.
- **Negative:** an unseen binary cause changes the correct safe action but has
  identical source marginal laws; no source-only learner can certify both
  worlds.
- **Inert-policy trap:** the utility floor prevents a policy that always refuses
  to act from resolving the problem.
- **Post-hoc-metric trap:** `Theta_adv`, its metric, and the curvature bound are
  frozen before evaluation outcomes.

## Existing theory this must exceed

Domain adaptation has impossibility theorems, and invariant learning has both
positive results and counterexamples. The missing result is not another domain
generalization algorithm. It is a sharp certification boundary—necessary and
sufficient coverage of the declared safety-relevant shift directions, with a
uniform risk certificate and an optimal experiment-selection rule.

## Safety consequence

A solution would state when a red-team or evaluation suite spans its claimed
deployment threat model, identify the missing direction when it does not, and
prevent “many diverse tests passed” from being mistaken for a distribution-free
safety guarantee.

---

# ASMP-3 — The Weak-Verifier Soundness Frontier

## Safety question

Which tasks performed by a stronger, possibly adversarial system can be judged
soundly by a substantially weaker verifier using only a small number of noisy
human-semantic judgments?

## Canonical mathematical setting

For input length `n`, freeze a decision relation `R_n`; a public-coin message
order and stopping rule; an atomic semantic-query language `A_n` with maximum
description length, locality radius, evaluation cost, and a registered family
of meaning-preserving query replications; an ideal binary semantic oracle `H`;
and a noisy oracle `H_tilde`. The noise model specifies a
marginal error bound `eta<1/2` and a complete correlation/adaptivity class;
independent errors may not be assumed unless they are part of the model.

Two strategic provers have computation budget `T(n)` and the frozen zero-sum
payoff induced by completeness/soundness. A verifier has time `s(n)`,
semantic-query budget `q(n)`, and transcript budget `B(n)`, with all three
intended to be `polylog(T(n))`. Admissible transcript encodings, verifier and
prover randomness, and adaptive query access are part of the game. The honest
prover must itself have an efficient strategy; unbounded “honesty” does not
solve obfuscated arguments.

Freeze a decidable syntactic relation
`Refute_n(tau,S,b)` saying that atom set `S` with answer vector `b` refutes
transcript `tau`. Define the **combinatorial local refutation dimension**
`r_R(n)` as

```text
r_R(n) = max_(false admissible transcript tau)
         min{|S| : S is a subset of A_n
                   and Refute_n(tau,S,H restricted to S)}.
```

The inner minimum is infinity if no refuting set exists; the outer maximum is
zero if there are no false admissible transcripts.

This invariant contains no search or efficiency clause. Efficient location of
`S` is a separate condition below. The frozen atom length, locality, and
evaluation bounds are intended to rule out one “local” claim encoding the full
answer; a complete solution must prove that encoding invariance rather than
assume it from syntax alone.

Independently of the task, define the semantic-noise amplification profile

```text
a_H(k) = inf_(registered k-query aggregators A)
         sup_(legal correlated error laws) Pr[A answers an atom incorrectly].
```

The infimum ranges only over meaning-preserving replications allowed by the
frozen query language; it cannot replace an atom with a full solution.

## Weak-Verifier Characterization Conjecture

A task family admits a constant-gap, doubly efficient, noise-robust oversight
protocol if and only if:

1. its combinatorial local refutation dimension is polylogarithmic in the
   prover computation;
2. an efficient honest prover can find a local refutation against every
   efficient dishonest strategy; and
3. for some constant `c>0`, `a_H(polylog(T(n))) <= 1/2-c` with a constructive
   aggregator, so the registered correlation model supports a constant gap.

The conjecture is a characterization, not a claim that debate always works.
Tasks with large or computationally inaccessible refutations should fall
outside the class even if a fully informed human could eventually judge them.

## What a complete resolution requires

1. A formal complexity class for the protocols above and a class equality,
   separation, or complete invariant characterizing it.
2. A constructive protocol with explicit completeness and soundness against
   adaptive, obfuscating provers.
3. Matching communication, semantic-query, and honest-prover lower bounds.
4. A robust theorem for correlated/noisy semantic judgments.
5. A proof that the local-refutation definition is invariant under benign
   transcript encodings and cannot hide full verification in one “local” query.

## Liveness and kill examples

- **Positive:** a long hybrid computation whose false traces have short,
  efficiently locatable formal-plus-semantic refutations, with semantic atoms
  repeated through a registered block-independent noise model that admits
  amplification.
- **Negative:** a task in which two candidate worlds generate identical allowed
  semantic queries but require opposite answers.
- **Recomputation trap:** verifier cost must remain asymptotically below solving
  the task independently.
- **Specification trap:** the theorem certifies relation `R`; it does not prove
  that `R` captures human intent.
- **Classical-theorem trap:** merely restating `IP=PSPACE`, PCP, or ordinary
  verifiable computation does not resolve noisy semantic oversight.

## Existing theory this must exceed

Interactive proofs show remarkable verification power for formal languages,
and doubly efficient debate has positive results for computations with
black-box human-judgment queries. The open frontier is efficient honest
refutation under obfuscation, noisy/correlated semantic judgments, and tasks for
which no short human-verifiable transcript is given in advance.

## Safety consequence

A solution would partition tasks into those that can be soundly delegated to
superhuman systems with bounded oversight and those for which debate,
consultancy, amplification, or decomposition cannot supply the claimed
guarantee without stronger verification primitives.

---

# ASMP-4 — Two-Port Evaluator-Relative Confinement

## Safety question

How much information must independently cross the observation and actuation
interfaces to keep an adaptive system inside a declared evaluator-safe region?

## Canonical mathematical setting

Consider an uncertain controlled process

```text
x_(t+1) = F(x_t,u_t,w_t),
```

with disturbance `w_t`, initial set `K_0`, and evaluator-safe target `K`. For a
registered causal code `C` and horizon `T`, let `M_r^C(T)` and `M_w^C(T)` be
finite transcript alphabets, or prefix-free countable alphabets charged by
worst-case length. Define its worst-case asymptotic achieved rates

```text
r_r(C) = limsup_(T->infinity) (1/T) log2 |M_r^C(T)|,
r_w(C) = limsup_(T->infinity) (1/T) log2 |M_w^C(T)|.
```

A causal sensor encoder emits only the read transcript; a controller receives
only those symbols and emits the write transcript; an actuator decoder maps
write symbols to controls. Variable-length variants must charge prefix-free
worst-case or expected length explicitly rather than reuse these definitions.

The plant, sensor, controller, and actuator are separate components. No analog
state, shared object reference, common random variable correlated with the
state, or uncharged side channel may cross either interface. Internal memory,
delays, block coding, and shared randomness independent of the plant state are
explicit parts of the architecture.

Define the achievable safety-capacity region

```text
R_K = {(R_r,R_w): there exists a registered causal code C with
                   r_r(C) <= R_r and r_w(C) <= R_w
                   such that every x_0 in K_0 remains in K
                   for every allowed disturbance sequence}.
```

When only an evaluator output must remain safe, motion tangent to safe fibers
or the boundary may be quotiented out. The required invariant must distinguish
full-state entropy from evaluator-transversal entropy.

## Two-Port Capacity Conjecture

For a registered normally hyperbolic, locally controllable class with bounded
uncertainty, delay, memory, control-authority, and disturbance conventions, the
closure of `R_K` has a variational characterization in terms of two possibly
different evaluator-transversal invariance quantities:

```text
R_r >= h_read_perp,
R_w >= h_write_perp,
```

together with any architecture-dependent tradeoff inequalities. Read-only
specializations must recover the classical sum of positive evaluator-normal
Lyapunov exponents under the assumptions of the corresponding data-rate
theorem. No equality is assumed for the write port merely from full
controllability: determining when `h_write_perp` equals, exceeds, or is
incomparable to the read threshold is part of the problem. Tangential
instability costs rate only insofar as the frozen dynamics couple it into
evaluator-relevant directions.

The conjecture does **not** assume the region is rectangular in general.
Decoder memory, predictive control, block coding, and side information can
change the write-side frontier and must be included in the theorem.

## What a complete resolution requires

1. A coordinate-invariant definition of the read and write transversal
   entropies.
2. A variational formula for the entire achievable rate region, not only one
   lower bound.
3. Converse theorems and constructive coder-controller/actuator schemes.
4. Exact finite-horizon corrections showing how initial safety margin permits
   temporary operation below the asymptotic rate.
5. Counterexamples locating the boundary of partial observability,
   uncertainty, nonhyperbolicity, and side-information assumptions.

## Liveness and kill examples

- **Positive:** a stable plant with adequate control authority may need zero
  asymptotic rate.
- **Negative:** an unstable evaluator-normal mode with a positive-volume initial
  collar cannot be confined below its information-expansion rate.
- **Authority control:** a full-state/full-action controller distinguishes
  information failure from insufficient actuator authority.
- **Split-port witness:** in a registered mode-switching plant, hold the sensor
  experiment fixed while varying the finite actuator dictionary needed to
  counter distinct modes; the write boundary changes without changing the read
  boundary.
- **Side-channel control:** supplying uncharged analog state must alter the
  threshold, demonstrating why the architectural separation is load-bearing.
- **Monte Carlo trap:** random nonfailure cannot establish universal
  confinement.

## Existing theory this must exceed

Data-rate theorems, invariance entropy, uncertain-system feedback entropy, and
output invariance entropy already exist. Re-proving `sum log |lambda|` for a
single linear channel is not a solution. The missing object is the joint
two-interface capacity region for nonlinear uncertain output/evaluator
confinement, including the quotient/transversal and finite-horizon terms.

## Safety consequence

A solution would convert “monitoring and intervention are sufficiently rich”
into separate, auditable interface requirements. It would also identify when a
governance or control proposal fails because the controller cannot observe
enough, cannot write enough, or is measuring instability irrelevant to the
declared evaluator boundary.

---

# ASMP-5 — Reflective Safety under Open-Ended Self-Modification

## Safety question

Can local certificates remain sound through an unbounded sequence of
self-modifications that changes not only behavior but also the proposer,
evaluator, or certificate-producing machinery, while retaining nontrivial
progress?

## Canonical mathematical setting

A system state is `z=(p,T,c)`, consisting of an executable program or policy
`p`, a proof/certificate system `T`, and its control state `c`. An allowed
update `F` may replace any declared subset of these objects. Freeze:

- a formal language and operational semantics;
- a semantic safety set `S` or trace property;
- a competence/progress index `P` with a nonzero floor;
- an effectively presented update grammar `U`;
- a computable local certificate relation `Cert(z,F,pi)`; and
- a trusted base semantics/kernel describing which part, if any, cannot be
  rewritten, with soundness stated as an assumption rather than self-certified.

The desired soundness property is

```text
z_(t+1) = F_t(z_t), z_0 in S, and Cert(z_t,F_t,pi_t) for every t
implies z_t in S for every t,
```

for every adaptive certified update sequence. Nontriviality requires a uniform
update generator over a registered infinite task family, infinitely many
behaviorally nonequivalent certified states, and unbounded cumulative progress
under the frozen index. Identity updates, a single whitelisted infinite chain,
or positive increments with bounded Zeno sum do not count.

## Reflective Safety Frontier Problem

Let one regime reduce to another when there is a computable, safety- and
progress-preserving translation of its language, update grammar, and
certificates. Characterize the resulting positive/negative frontier of regimes
for which a computable certificate architecture can simultaneously satisfy:

1. uniform semantic soundness for all adaptive certified sequences;
2. compositionality when the proposer and certificate generator are replaced;
3. an explicit corrigibility/interruption condition;
4. perturbation robustness or probabilistic failure bounds; and
5. open-ended nontrivial progress.

No unique greatest regime is assumed; incomparable frontier components and a
proof that no greatest effective class exists are allowed outcomes. The
canonical unrestricted quantifier order is: for every total computable
certificate architecture `A` and every nontrivial extensional trace property
`S`, if `A` is uniformly sound over all partial-computable update programs, then
`A` fails the registered uniform open-ended-progress condition on some task
family. The canonical dichotomy conjecture is:

- no such architecture exists for all partial computable self-modifiers and any
  nontrivial extensional semantic safety property; but
- a nontrivial downward-closed positive region exists for proof-carrying updates
  that preserve an inductive invariant in an assumed-sound fixed kernel, or in
  a precisely characterized hierarchy of reflective proof systems.

The problem is to locate the exact frontier, not to assume a differentiable
“self-improvement Jacobian.”

## What a complete resolution requires

1. A matching impossibility theorem for the unrestricted computable class,
   identifying the exact diagonalization, Rice, Löb, or consistency barrier.
2. Nontrivial positive constructions and a characterization of the effective
   frontier, including whether a greatest positive regime exists.
3. A proof that certificates compose through permitted verifier/evaluator
   changes rather than only through fixed-policy updates.
4. A performance theorem excluding inert or finitely terminating solutions.
5. A robust stochastic/finite-precision counterpart or a proof that one is
   impossible.

## Liveness and kill examples

- **Positive:** proof-carrying finite-state or polynomial updates preserving a
  common inductive barrier in a frozen checker.
- **Reflective positive target:** a stratified proof-system hierarchy in which
  permitted verifier replacements compose through an assumed-sound root
  semantics while generating infinitely many behaviorally nonequivalent safe
  states.
- **Negative:** arbitrary programs whose “safe forever” predicate encodes the
  halting problem.
- **Löb trap:** a theory cannot be assumed to prove the soundness of an
  arbitrarily stronger successor merely because the successor says it is sound.
- **Spectral trap:** a local spectral radius cannot replace nonlinear,
  adaptive, or switched-system safety; boundedness of arbitrary matrix products
  is already undecidable in broad classes.
- **Channel trap:** proposal-channel recursion under a frozen scorer does not
  establish evaluator- or objective-channel recursion.

## Existing theory this must exceed

Reflective oracles, Löbian obstacles, proof-carrying code, inductive invariants,
barrier certificates, and self-modifying-agent models supply important partial
constructions. Conversely, computability and switched-system results establish
hard impossibility boundaries. The unresolved target is the effective robust
frontier allowing both compositional safety and open-ended certified change.

## Safety consequence

A solution would state exactly which recursive training or self-editing systems
can inherit safety from local update checks, where an immutable root of trust is
mathematically necessary, and which broader claims cannot be certified even in
principle.

---

# ASMP-6 — Adaptive Semantic Collusion Capacity

## Safety question

How many hidden bits or coordinated actions can monitored learned agents convey
while preserving task performance and remaining statistically
indistinguishable from approved behavior?

## Canonical mathematical setting

There are `N` adaptive agents over horizon `T`. Freeze:

- task/context process `X^T` and benign transcript law `P_0(Y^T|X^T)`;
- a task-distortion budget `D`;
- a monitor/auditor class `D_mon`, including its active challenge actions;
- common randomness, shared weights, tools, public artifacts, and repeated
  history available to the agents;
- a hidden coalition message `M_T`; and
- the coalition-action or decoding success criterion.

The message `M_T` is uniform and independent, conditional on the public task,
of all preshared keys, weights, tools, and initial side information. Shared
randomness may encode it only after the experiment begins; already possessing
the message does not count as communication. The decoding-error target is a
registered sequence `rho_T -> 0`.

The monitor advantage is the maximum distinguishing advantage over
`D_mon`. Define

```text
C_coll(P_0,D,{epsilon_T},{rho_T})
  = limsup_(T->infinity) (1/T) sup log2 |M_T|,
```

where the supremum ranges over agent strategies satisfying the task-distortion
constraint, decoding error at most `rho_T`, and monitor advantage at most
`epsilon_T`. Fixed-error, vanishing-error, and covert
`epsilon_T -> 0` regimes are separate registered problems. When this rate is
zero, the sublinear scaling exponent and constant remain part of the problem.

## Stationary-Core Capacity Conjecture

For stationary finite-alphabet memoryless agent/task systems with additive
distortion, registered side information, and a product active-audit channel,
the capacity has a single-letter minimax characterization over conditional
strategy distributions. Its zero-rate boundary is determined by a
**tensorizing quantitative resolving modulus**, not merely by pointwise
injectivity.

Let `A^T` denote the coalition-relevant action or decoded-action trace and let
distance to the benign experiment be measured by the integral probability
metric induced by `D_mon`. Let `Code_T(D,rho,delta)` be exactly the class of
horizon-`T` codes used in the capacity supremum: the message is uniform and
initially independent, task distortion is at most `D`, decoding error at most
`rho`, and monitor advantage at most `delta`. Define

```text
omega_T(D,rho,delta)
  = sup_(codes c in Code_T(D,rho,delta)) I_c(M_T;A^T).
```

By Fano's inequality, `omega_T(D,rho_T,epsilon_T)=o(T)` implies zero capacity
whenever `A^T` contains the registered decoding outcome. The conjectured new
content is a single-letter or finite-memory formula for this modulus and sharp
conditions under which it tensorizes. The achievability direction requires
more than noninjectivity: a repeatable unresolved strategy component with
positive conditional entropy, a registered conditional common-randomness rate,
a quantitative resolvability bound, and linear action information must yield a
positive-rate code. Isolated one-bit ambiguities may be non-resolving while
still having zero asymptotic rate. In the local covert regime, the
quadratic monitored-divergence geometry should determine the square-root
constant. The nonstationary learned extension asks when these moduli tensorize
or fail under endogenous cover distributions and active challenges.

Negative-edge counts, suspicious tokens, or pairwise mutual information are not
complete order parameters: synergistic secret-sharing channels can have zero
individual information and positive coalition information.

## What a complete resolution requires

1. An achievability and converse coding theorem for the stationary canonical
   model, including reliability sequences and shared-key, no-key, and
   emergent-key regimes.
2. The exact zero-rate/square-root/positive-rate phase boundary.
3. A minimax extension to adaptive learned cover distributions and restricted
   learned monitors.
4. An active audit protocol that provably drives capacity to zero or to a sharp
   residual bound while preserving declared task utility.
5. A compositional theorem for tools, timing, code, and public artifacts as
   side channels.

## Liveness and kill examples

- **Positive capacity:** an approved cover channel has entropy and agents share
  a secret code while exactly preserving the monitor-visible distribution.
- **Zero capacity:** the quantitative resolving modulus is sublinear even
  though a finite number of globally ambiguous bits may remain.
- **Classical trap:** proving that plausible text can carry hidden bits merely
  rederives mature steganography.
- **Monitor-power trap:** capacity is undefined until the monitor class,
  challenge access, key material, and cover distribution are fixed.
- **Synergy trap:** pairwise tests cannot rule out multi-agent secret sharing.

## Existing theory this must exceed

Provably secure steganography, covert communication, square-root laws,
fingerprinting, and collusion-resistant codes are mature. The new frontier is
endogenous cover distributions chosen by learned agents, monitors that are
restricted learned discriminators, active auditing, and side information from
shared weights and tools.

## Safety consequence

A solution would replace “the transcript looks normal” with a capacity bound,
identify which audit actions eliminate hidden coordination, and state when
untrusted monitors or agents can communicate despite pairwise transparency.

---

# ASMP-7 — Capability Attestability under Compression and Decomposition

## Safety question

Which capability- or resource-policy claims remain verifiable when an execution
can be compressed, distilled, decomposed, offloaded, or reorganized without
preserving the telemetry regime on which the policy was based?

## Canonical mathematical setting

Let `X_0` be compliant executions and `X_1` forbidden executions under a frozen
policy predicate `P`. Let `G` be an allowed/adversarial transformation semigroup
containing declared compression, distillation, decomposition, caching,
offloading, and algorithmic-substitution operations.

Freeze a non-oracular, physically realizable telemetry class `K_adm`. Each
channel `K(dy|e)` may access only a declared primitive event stream `O(e)` under
a locality/query graph, bit rate, compute, latency, privacy budget, and
composition rule. It may not query `P(e)`, an unmeasured latent capability, or a
semantic oracle unless that access is explicitly charged as part of the policy.
Let `G_j(e) subseteq G` be the registered transformations admissible to an
execution `e in X_j` for `j in {0,1}`.

The adversary may randomize over registered executions and transformations.
In a declared topology on dominated telemetry laws—total variation for the
canonical fixed-error problem—the compliant and forbidden composite law sets
are

```text
Q_j(K) = closure_TV convex hull
         {K(.|g e): e in X_j, g in G_j(e)}.
```

Define the composite error region

```text
Err(K) = {(a,b): there exists a test phi:Y->[0,1] such that
                   sup_(Q in Q_0(K)) E_Q phi <= a
               and sup_(Q in Q_1(K)) E_Q (1-phi) <= b}.
```

For false-positive target `alpha` and false-negative target `beta`, define the
minimum attestation cost

```text
c*(alpha,beta)
  = inf_(K in K_adm : (alpha,beta) in Err(K)) cost(K).
```

Thus the separate false-positive and false-negative constraints are retained;
a scalar total-variation gap or minimum sum-error statistic is not silently
substituted for the registered error pair.

## Transformation-Closed Attestability Conjecture

Finite-cost attestation at `(alpha,beta)` is possible exactly when an admissible
finite-cost telemetry experiment places `(alpha,beta)` in its **uniform
composite error region**—not merely when individual orbit pairs are
topologically distinct. The problem asks whether the cost/soundness/privacy
frontier admits a Blackwell-minimal or Pareto-minimal experiment under
registered compactness and lower-semicontinuity assumptions; otherwise the
correct object is an infimum or infimizing sequence, not a nonexistent least
channel.

In particular:

1. no compute-trace-only channel can soundly certify an extensional capability
   predicate under unbounded algorithmic-efficiency transformations if a
   compliant and forbidden execution can induce the same trace law; and
2. with a frozen efficiency envelope and proof-carrying workload/commitment
   checks, a resource-relative predicate may become attestable with optimal
   error governed by the separation of `Q_0(K)` and `Q_1(K)`.

The conjecture concerns statistical and cryptographic evidence together.
Cryptographic integrity proves that evidence was not altered; it does not by
itself prove that all capability-bearing executions produced evidence.

## What a complete resolution requires

1. A necessary-and-sufficient uniform composite-testing/deficiency theorem for
   transformation-closed policy predicates and physically admissible access.
2. A construction or characterization of the infimum-cost telemetry frontier
   in a nontrivial structured execution class, plus conditions under which an
   optimizer is attained.
3. A compositional theorem across datacenters, devices, cached state, and
   decomposed workloads.
4. Explicit tradeoffs among soundness, privacy, audit cost, and the bounded
   algorithmic-efficiency envelope.
5. A sharp impossibility theorem for trace-equivalent compliant/forbidden
   executions and for unbounded efficiency variation.

## Liveness and kill examples

- **Positive:** a proof-carrying, cryptographically committed workload inside a
  bounded transformation class exposes a non-oracular primitive statistic
  uniformly separating compliant and forbidden executions.
- **Negative:** a small optimized program and a large declared workload have
  identical permitted telemetry while only the former realizes the forbidden
  capability; no verifier using that telemetry can distinguish them.
- **Integrity trap:** signed bytes do not establish semantic completeness.
- **Oracle trap:** a one-bit channel that directly emits `P(e)` is excluded
  unless the policy predicate is itself physically available at registered
  cost.
- **One-real-number trap:** “minimum dimension” is meaningless without bit,
  regularity, compute, or continuity constraints because arbitrary encodings
  can pack high-dimensional objects into one real.
- **Task-only-compression trap:** preserving ordinary task behavior does not
  preserve monitor sufficiency unless the safety variable is measurable from
  the compressed experiment.

## Existing theory this must exceed

Blackwell sufficiency, rate-distortion theory, information bottlenecks,
bisimulation metrics, robust model reduction, cryptographic attestation, and
proof-carrying code provide parent tools. The unresolved target is
intervention- and transformation-closed sufficiency for capability/resource
policies under adaptive compression and decomposition, with an infimum-cost
telemetry theorem and explicit attainment conditions.

## Safety consequence

A solution would identify which compute-governance and transparency promises
are enforceable, which require new telemetry, and which become mathematically
unverifiable once algorithmic efficiency or distributed execution escapes the
declared resource proxy.

---

# Coverage map, reductions, and overlap

The set forms a stack rather than seven synonyms:

```text
ASMP-1  identifies the internal causal object.
   |
ASMP-2  asks whether evidence spans deployment shifts.
   |
ASMP-3  asks whether a weaker judge can verify the resulting claims.
   |
ASMP-4  asks whether enough information crosses the live control interfaces.
   |
ASMP-5  asks whether certificates survive recursive replacement.
   |
ASMP-6  asks what coordinated agents can hide inside allowed communication.
   |
ASMP-7  asks whether institutions can attest the policy after capability moves.
```

The arrows indicate conceptual workflow, not pairwise mathematical
independence. Reductions may exist: collusion can be encoded as an attestation
problem, interactive telemetry can resemble weak verification, and shift
certification can be phrased as separation of statistical experiments. A later
version should merge candidates if an equivalence or strict subsumption theorem
is proved. Until then, their frozen input/output objects differ: internal causal
quotients, deployment-risk certificates, verifier games, live control rates,
self-update proof systems, covert message rates, and institutional telemetry
experiments. A solution to one does not silently supply another's premises.

# Prize-style resolution protocol

This draft proposes the following acceptance standard should a real prize or
community challenge ever be created.

1. The solver identifies the exact problem ID and version.
2. Unless a problem version declares another base, ordinary mathematical claims
   are formalized over ZFC with standard encodings of computation, probability,
   and analysis. “Independence” means independence from that declared base.
3. The result covers the full frozen canonical statement, proves the fixed
   sentence false or independent of the declared foundation, or proves the
   associated frozen uniform decision family undecidable. A theorem for a
   narrower subclass is partial progress.
4. Any changed assumption creates a new problem version and cannot be presented
   as resolving the parent without a reduction.
5. The proof appears publicly with all definitions, code, and machine-checkable
   artifacts needed for verification.
6. Computer-assisted proof obligations use exact or interval-certified
   arithmetic and an independent checker.
7. At least two independent expert teams reproduce the decisive argument; for
   machine-checked work, at least one uses an independently implemented checker.
8. Empirical model evidence may motivate premises but does not fill a deductive
   gap.
9. A negative resolution receives equal standing when it supplies the sharp
   impossibility boundary required by the statement.

# Primary mathematical precedents and novelty boundaries

The following are starting points, not endorsements of every conjecture above.

## Mechanistic and causal identifiability

- Geiger et al., [Causal Abstraction: A Theoretical Foundation for Mechanistic
  Interpretability](https://www.jmlr.org/papers/v26/23-0058.html).
- Varıcı et al., [General Identifiability and Achievability for Causal
  Representation Learning](https://proceedings.mlr.press/v238/varici24a.html).
- Li, Kaba, and Ravanbakhsh, [On the Identifiability of Causal
  Abstractions](https://proceedings.mlr.press/v258/li25g.html).
- Sutter et al., [The Non-Linear Representation Dilemma: Is Causal Abstraction
  Enough for Mechanistic Interpretability?](https://arxiv.org/abs/2507.08802).
- Locatello et al., [Challenging Common Assumptions in the Unsupervised Learning
  of Disentangled Representations](https://proceedings.mlr.press/v97/locatello19a.html).

## Shift and generalization limits

- Ben-David et al., [Impossibility Theorems for Domain
  Adaptation](https://proceedings.mlr.press/v9/david10a.html).
- Kamath et al., [Does Invariant Risk Minimization Capture
  Invariance?](https://proceedings.mlr.press/v130/kamath21a.html).
- Ahuja et al., [Invariance Principle Meets Information Bottleneck for
  Out-of-Distribution Generalization](https://arxiv.org/abs/2106.06607).
- van der Vaart, [Asymptotic
  Statistics](https://doi.org/10.1017/CBO9780511802256), for the
  semiparametric tangent and local-asymptotic framework that ASMP-2 must extend.

## Scalable verification

- Shamir, [IP = PSPACE](https://doi.org/10.1145/146585.146609).
- Brown-Cohen et al., [Scalable AI Safety via Doubly-Efficient
  Debate](https://proceedings.mlr.press/v235/brown-cohen24a.html).
- Irving, Christiano, and Amodei, [AI Safety via
  Debate](https://arxiv.org/abs/1805.00899).

## Control under information constraints

- Tatikonda and Mitter, [Control Under Communication
  Constraints](https://doi.org/10.1109/TAC.2004.831187).
- Colonius and Kawan, [Invariance Entropy for Control
  Systems](https://doi.org/10.1137/080713902).
- Colonius and Kawan, [Invariance Entropy for
  Outputs](https://doi.org/10.1007/s00498-011-0056-9).
- Tomar, Rungger, and Zamani, [Invariance Feedback Entropy of Uncertain Control
  Systems](https://arxiv.org/abs/1706.05242).

## Reflection and adaptive dynamics

- Fallenstein, Taylor, and Christiano, [Reflective Oracles: A Foundation for
  Classical Game Theory](https://arxiv.org/abs/1508.04145).
- Löb, [Solution of a Problem of Leon
  Henkin](https://doi.org/10.2307/2266895).
- Necula, [Proof-Carrying
  Code](https://doi.org/10.1145/263699.263712).
- Ahrenbach, [Löb-Safe Logics for Reflective
  Agents](https://arxiv.org/abs/2408.09590).
- Blondel and Tsitsiklis, [The boundedness of all products of a pair of matrices
  is undecidable](https://doi.org/10.1016/S0167-6911(00)00049-9).

## Covert channels and collusion

- Hopper, Langford, and von Ahn, [Provably Secure
  Steganography](https://eprint.iacr.org/2002/137.pdf).
- Bash, Goeckel, and Towsley, [Limits of Reliable Communication with Low
  Probability of Detection on AWGN Channels](https://arxiv.org/abs/1202.6423).
- Bloch, [Covert Communication over Noisy Channels: A Resolvability
  Perspective](https://arxiv.org/abs/1503.08778).
- Moulin, [Universal Fingerprinting: Capacity and Random-Coding
  Exponents](https://arxiv.org/abs/0801.3837).

## Sufficiency, compression, and attestation

- Blackwell, [Equivalent Comparisons of
  Experiments](https://doi.org/10.1214/aoms/1177729032).
- Tishby, Pereira, and Bialek, [The Information Bottleneck
  Method](https://arxiv.org/abs/physics/0004057).
- Ferns, Panangaden, and Precup, [Metrics for Finite Markov Decision
  Processes](https://arxiv.org/abs/1207.4114).

# Final epistemic boundary

The ASMP candidate set is a proposed map of theorem frontiers. It does not
establish that advanced AI will be recursively self-improving, deceptive,
collusive, or uncontrollable. Its purpose is narrower and more durable: to
identify mathematical statements whose eventual closed versions would change
what can be known, verified, controlled, or enforced if those system classes
become relevant. Version 0.1 is ready for external definition review, not for a
claim that seven settled prize specifications now exist.
