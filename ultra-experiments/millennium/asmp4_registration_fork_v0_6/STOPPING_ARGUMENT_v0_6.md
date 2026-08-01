# ASMP-4 evidence-backed stopping argument v0.6

## Decision

Stop treating more local enumeration as a route to one unconditional canonical
ASMP-4 region. The current evidence proves two different exact regions under
two sensor registrations while holding every plant-side and metric choice
fixed. Selecting between them is a specification decision.

## Canonical wording cross-check

The source statement defines `R_K` by existence of a “registered causal code,”
then formulates its conjecture for a “registered normally hyperbolic, locally
controllable class” and expressly permits architecture-dependent tradeoff
inequalities. It also requires memory, delay, and related architecture choices
to be explicit. It never declares that every registered sensor grammar is
closed under replacing its emitted observation by an arbitrary sufficient
statistic.

That missing closure declaration is exactly the premise separated by the v0.6
fork. If arbitrary causal sensor computation is admitted, the upstream normal
form applies. If registration fixes a raw transducer, that replacement is not
an admissible code. Both readings respect the stated component separation and
charged transcript metric. The stopping conclusion therefore follows from a
literal missing class quantifier in
`../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md`, not from an unrelated alternative
metric or plant.

Central and import-independent parsers enforce this reading mechanically: all
eight relevant source clauses must remain present, neither closure-selection
phrase may appear, and the two completions must retain distinct verified
regions. Thirteen adversarial mutations delete each required clause, insert
each recognized closure selector, or collapse the region witnesses; every one
must reverse the audit verdict. Documentation drift therefore fails the
harness.

The compliance premise is also executable rather than asserted. Two
independent model builders extract 13 obligations from the canonical setting,
instantiate the registry predicate, sensor, controller, actuator, explicit
zero-memory/zero-delay architecture, and absence of side channels, then replay
all mode words. Both models satisfy all 13 obligations. Their existential
regions differ solely because the canonical source never defines the domain
selected by the word `registered`.

This absence is global, not an artifact of reading one subsection. The entire
normative Markdown contains 31 uses of `registered` and zero definitions of
the causal-code registry. Its machine-readable companion declares itself non-
normative, points back to that Markdown, marks the candidate set as an
ungraduated definition draft, and adds no code-domain field to ASMP-4. The
problem's own graduation standard requires domains and quantifier order to be
explicit, so the missing registry predicate is a specification defect by the
document's stated standard.

Nor is the conclusion peculiar to two isolated registry choices. The complete
15-partition lattice has 32,767 nonempty registries and three distinct feasible
read corners, plus 2,047 infeasible registries. Every one of its 245,760 cover
edges is monotone and 26,624 are strict. Consequently an unspecified registry
predicate leaves a large, exactly classified family of possible answers.

For every finite full-reset action-fiber shape, the ambiguity has a closed
Stirling/Bell classification rather than only a bounded census. The formula
counts all infeasible registries, every exact read corner, and every strict
inclusion edge; it is independently checked through five modes, including
`2^52`-registry lattices. More enumeration cannot select one member of this
parameterized family.

The same monotonic structure survives constrained dynamics and adaptive
belief policies. A complete three-mode census checks 372,155 nonempty grammars
and 960,400 inclusion edges, with no finite-value or viability reversal. It
also finds the precise transient seam: 12 singleton grammars work through
horizon four and fail at five. These cases refine the theorem's finite/infinite
boundary but cannot choose the unspecified canonical grammar.

The transient seam is itself closed in the fixed-transducer universe through
three modes: all 60,134 cases are classified by first failure, the maximum
finite-safe prefix has length four, and an explicit constant-sensor witness
fails exactly at horizon five. Thus finite-horizon artifacts are recorded
precisely rather than used to support the registration stopping claim.

## Harness certificate

The registration fork is not inferred from a few budget cells:

1. all 15 partitions of the four sensor modes and every block-to-action map
   are enumerated;
2. exactly four partitions are safe, with the unique coarsest sufficient
   partition `{0,1}|{2,3}`;
3. all `4^T` disturbance paths are directly replayed through horizon eight;
4. analytic lower bounds and matching constructions prove the counts for every
   horizon;
5. a rational unstable evaluator-normal embedding is replayed exactly, with
   normal multiplier `3/2`, tangent reset derivative zero, and unit control
   derivative;
6. an independent implementation reproduces the census, language counts, and
   embedding; and
7. every prior ASMP-4 verifier and the frozen receipt replay remains green.

Theorem 4 additionally closes the whole finite full-reset family: for any
registered sensor-partition grammar, the exact corner is determined by the
smallest admitted partition refining the required-action fibers. Independent
censuses cover every action/sensor partition pair through five modes.

Theorem 5 closes the fixed-transducer constrained finite-mode family as well.
Its exact subset observer decides causal feasibility and computes both language
entropies. Exhaustion through three modes covers 60,134 cases, and the golden-
mean fixture supplies a non-full-reset algebraic entropy boundary.

Theorem 6 closes both finite and infinite horizons for history-adaptive
partition grammars on constrained finite graphs. It combines an exact belief-
state Bellman recurrence, greatest-fixed-point viability, and the prescribed-
initial-state entropy-game positional theorem to give corner
`(log2 rho_I,h_g)` attained by a stationary belief policy. Its strongly
connected, aperiodic fixture has Fibonacci adaptive growth, strictly below the
binary growth of the best fixed grammar. Thus neither transience nor
periodicity explains the adaptive gap.
Two independent censuses additionally agree on all 120,050 three-mode,
two-partition grammar cases at horizon four, including 1,572 adaptive-only
feasible cases and 4,863 strict finite-horizon improvements. All 99,524 finite-
feasible cases pass the independent infinite-viability fixed point as well.

## Why another harness cannot choose the branch

In the computed-sensor registration, the sensor may move the controller’s
deterministic grouping upstream, so the v0.3 diagonal normal form applies. In
the forced-raw registration, the same grouping is forbidden at the sensor, and
the exact read threshold doubles. Both are coherent deterministic serial
architectures with no side channel.

Increasing horizon, state count, probability resolution, or prefix-code depth
inside either branch can improve regression coverage but cannot establish that
the other branch was not intended. The missing bit is not mathematical data;
it is the quantifier over admitted sensor grammars.

## Conditions for productive continuation

Reopen the canonical lane when one of the following is supplied:

- the problem declares that every registered sensor may implement arbitrary
  causal computation by its emission deadline;
- the problem permits fixed or computationally restricted transducers and asks
  for a theorem parameterized beyond the full-reset, fixed-transducer, and
  adaptive finite-graph classes now covered by Theorems 4-6;
- a normally hyperbolic plant class and its exact observation/control grammar
  are registered for an explicit dynamical variational formula; or
- an external review finds an error in either normal-form construction or the
  registration-fork converse.

Until then, the defensible repository position is:

- **resolved conditionally:** exact diagonal region for bilateral
  normal-form-closed serial classes;
- **resolved boundary:** exact unequal region for the forced-raw fixture; and
- **not well-posed as one number or region:** the registration-independent
  canonical request.
