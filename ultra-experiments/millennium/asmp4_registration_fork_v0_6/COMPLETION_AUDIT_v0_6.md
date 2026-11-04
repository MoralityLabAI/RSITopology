# ASMP-4 canonical registration audit v0.6

## Audit decision

The v0.2/v0.3 relay theorem is a complete conditional theorem for serial code
classes closed under both normal forms. It is not an unconditional resolution
across every sensor grammar compatible with the broader phrase “registered
causal code.” The v0.6 fork proves that this distinction changes the canonical
terminal-language region, not merely an implementation detail.

This reading is anchored in the source text: the conjecture ranges over a
registered class, permits architecture-dependent tradeoffs, and requires
architecture choices to be explicit, but does not specify upstream computation
closure for the sensor grammar.

## Requirement evidence

| Obligation | Evidence | Finding |
| --- | --- | --- |
| Hold the plant fixed | Both branches use the same four safe modes, `BAD`, two actions, arbitrary next-mode disturbance, initial set, and safety predicate. | Exact |
| Hold authority and side information fixed | Both use the same two actuator controls and have no controller/actuator observation, random seed, or timing channel. | Exact |
| Use the canonical metric | Both charge `log2` of the complete realized transcript-language size. | Exact |
| Isolate one registration choice | Only the admitted sensor partition class changes: arbitrary computation versus the forced singleton partition. | Exact |
| Audit the literal canonical quantifier | Central and import-independent source parsers find all eight relevant architecture clauses, no clause selecting either sensor-computation closure, and two exact completions satisfying the same explicit obligations. | Reproduced |
| Replace asserted compliance with source models | Central and independent implementations extract 13 canonical obligations, construct both registry predicates and port maps, replay all mode words through horizon six, and verify every obligation in each model. | Reproduced |
| Audit global registration semantics | The full normative Markdown contains 31 uses of `registered` but zero code-domain definitions; the machine index is non-normative, ungraduated, and adds no ASMP-4 sensor grammar. | Reproduced |
| Prove both complete finite regions | Required-action and data-processing converses match explicit constructions at every horizon. | Proven |
| Verify the sensor grammar census | Central and independent implementations enumerate all 15 four-mode partitions and every block-to-action map, finding four safe partitions and four safe encoder/controller pairs. | Reproduced |
| Exhaust the registry lattice | All 32,767 nonempty partition registries split exactly into 2,047 infeasible and 30,720 feasible cases; all 245,760 cover edges are monotone and 26,624 are strict. | Reproduced |
| Generalize registry counts | The Stirling/Bell formula gives every infeasible count, exact corner count, and strict-edge count; independent implementations verify all 18 action shapes and 75 action partitions through five modes. | Proven and reproduced |
| Verify realized languages | Every one of `4^T` disturbance paths is replayed through `T=8`; counts are `4^T/2^T` versus `2^T/2^T`. | Reproduced |
| Connect the fork to evaluator-transversal dynamics | The exact rational embedding has normal multiplier `3/2`, tangent reset derivative zero, normal input derivative one, and unique safe controls `(0,0,1,1)`. | Proven and replayed |
| Parameterize the sensor grammar | Theorem 4 proves the exact `(log2 kappa,log2 m)` corner for every finite full-reset mode plant and arbitrary history-dependent selection from a registered partition grammar. | Proven |
| Audit the general formula | Independent generators enumerate all action/sensor refinement pairs through five modes (`1,3,12,60,358`) and 340 threshold-grammar cells. | Reproduced |
| Permit constrained mode dynamics | Theorem 5 characterizes feasibility by action-homogeneity of every reachable sensor-subset belief and gives exact finite label-language and asymptotic spectral regions. | Proven |
| Exhaust the finite graph seam | Central and independent implementations cover 60,134 graph/initial/transducer/action cases through three modes, with 37,430 feasible cases and 12,060 direct-language comparisons. | Reproduced |
| Classify transient safety depth | The same 60,134 cases have exact first-failure histogram `10642,8406,3110,534,12`; the 12 maximal cases are safe through horizon four and fail at five. | Reproduced |
| Give a non-full-reset entropy fixture | The golden-mean graph has exact Fibonacci read counts, entropy `log2 phi`, zero write entropy, and a zero-rate computed-sensor alternative. | Proven and reproduced |
| Permit history-adaptive constrained grammars | Theorem 6 gives the exact finite belief-state Bellman recurrence and the corresponding read/write rectangle at every horizon. | Proven |
| Close the infinite adaptive seam | Greatest-fixed-point viability plus the prescribed-initial-state entropy-game theorem gives an optimal stationary belief policy and exact corner `(log2 rho_I,h_g)` for every finite registered graph. The borrowed positional theorem is explicitly credited. | Proven by exact reduction to prior theorem |
| Rule out a transient adaptation artifact | A stationary belief policy on a strongly connected, aperiodic three-mode graph has adaptive counts `F_(T+1)` versus `2^T` for the best feasible fixed grammar, giving corners `(log2 phi,log2 phi)` and `(1,log2 phi)`. | Proven and independently reproduced |
| Exhaust the bounded adaptive seam | Central and import-independent implementations agree on all 120,050 three-mode graph/initial/action/two-partition grammar cases at horizon four: 99,524 adaptive-feasible and infinitely viable, zero finite-only false positives, 1,572 adaptive-only, and 4,863 strict fixed-to-adaptive improvements. | Reproduced |
| Exhaust the adaptive grammar lattice | All 372,155 nonempty grammars and 960,400 cover edges are checked. Finite value and viability are monotone; 104,556 edges improve strictly, while 12 singleton grammars expose an exact horizon-four-to-five transient boundary. | Reproduced |
| Preserve the v0.3 theorem | The computed branch is upstream-closed; the raw branch explicitly is not. No contradiction is claimed inside v0.3 premises. | Firewalled |

## Canonical completion position

The five canonical deliverables now separate as follows:

1. Coordinate invariance and evaluator quotients have a conditional
   operational definition in v0.2/v0.3.
2. The entire region is diagonal for normal-form-closed classes, but v0.6
   proves there is no registration-independent region across admissible sensor
   grammars unless the grammar quantifier is fixed.
3. Both v0.3 and v0.6 have exact converses and constructions in their written
   scopes.
4. v0.2 supplies exact scalar and box finite-horizon corrections.
5. v0.2-v0.6 now locate observation, authority, timing, metric, syntax,
   adaptation, and computation-closure boundaries.

Theorem 4 now supplies a registration-parameterized formula for the full-reset
finite-mode class. The remaining request for one formula over a general
“registered normally hyperbolic class” is under-specified until both the plant
class and its code grammar are declared; no harness can infer which class the
problem intended.

## Verification inventory

The v0.6 central payload checks twenty-one gates: complete partition census,
exhaustive path replay, both exact regions, unchanged architecture invariants,
the normal-form seam, the rational evaluator-transversal embedding, and the
general sensor-grammar formula, plus the constrained-graph census and golden-
mean entropy fork, the adaptive aperiodic grammar gap, the exhaustive adaptive
three-mode census, the infinite-viability/positional certificate, and the
canonical registration-quantifier audit, and its 13-case mutation-sensitivity
guard, the executable two-model registry certificate, and the global normative-
scope audit, the complete registry-lattice census, and its general Stirling/Bell
counting formula, the complete adaptive grammar-lattice census, and the exact
fixed-transducer failure-depth classification. The
independent verifier reconstructs
these objects without importing the central harness and checks the theorem,
claim, source quantifier, prior-art boundary, and predecessor firewalls.

The integrated run passes 81 tests across seven ASMP-4 generations, all 11
current central/independent audit programs, and the byte-identical frozen v0.1
receipt replay.
