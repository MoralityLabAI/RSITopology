# ASMP-4 adversarial stopping theorem v0.10

## Question

Does the v0.9 stopping conclusion survive the strongest immediate scope
objection: the v0.8 stochastic diagonal is not a normally-hyperbolic positive-
conjecture witness?

Yes.  The stochastic witness is not a premise of the sensor-only minimal
stopping theorem below.

## 1. Canonical scope partition

Canonical ASMP-4 has three logically different layers.

1. The general mathematical setting defines an uncertain process, the two
   component interfaces, universal disturbance safety, and `R_K`.
2. The positive Two-Port Capacity Conjecture is restricted to a registered
   normally hyperbolic, locally controllable class with bounded conventions.
3. Completion requirement 5 explicitly requests counterexamples at the
   boundaries of partial observability, uncertainty, nonhyperbolicity, and side
   information.

The v0.8 polynomial diagonal is a smooth counterexample in the general setting
and exposes an omitted stochastic quantifier.  It does not claim an NHIM
classification.  V0.10 preserves that firewall rather than silently promoting
the example into the positive subclass.

## 2. Primary rational NHIM witness

The primary witness is the v0.6 same-plant sensor fork.  It fixes the plant,
evaluator, authority, channels, complete-transcript metric, and safety rule.
Only the registered sensor/computation domain changes.

For modes `0,1,2,3`, the required safe actions are `0,0,1,1`.  The computed
registry admits the action-fiber sensor `(0,0,1,1)`, whereas the raw registry
requires `(0,1,2,3)`.  Arbitrary full reset makes every mode word possible.  At
every horizon `T`, exact transcript counts are

~~~text
computed read = 2^T,  raw read = 4^T,  write = 2^T.
~~~

Consequently their closed regions are respectively

~~~text
[1,infinity) x [1,infinity),
[2,infinity) x [1,infinity).
~~~

The rational embedding is

~~~text
n_next=(3/2)n+u-q(z),  z_next=w,
q(z)=(12+13z-z^3)/24,
z in {-3,-1,1,3},  q(z) in {0,0,1,1}.
~~~

The normal multiplier is `3/2`, the tangent reset derivative is zero, and the
normal control derivative is one.  Thus the fixture has the required unstable
evaluator-normal direction, dominated tangent reset, and local normal control.
More explicitly,

~~~text
K=K_0={0} x {-3,-1,1,3}
~~~

is a compact zero-dimensional invariant manifold under the registered correct
control and every bounded disturbance reset.  All 16 `(z,w)` pairs return to
`K`; the other binary control sends the normal coordinate to `-1` or `1` and
therefore leaves `K`.  This also makes the unique-safe-control and bounded-
uncertainty conventions explicit.

The v0.6 central and independent model builders verify 13 of 13 explicit
architecture obligations for both registries, including component separation,
no side channel, universal safety, and exact transcript languages.

## 3. Sensor-only minimal stopping theorem

**Theorem.** The canonical ASMP-4 text does not determine a unique capacity
region unless it normatively fixes the registered sensor/computation domain.

**Proof.** The normative Markdown and non-normative machine index select
neither upstream-computation closure nor forced raw transduction.  The two
completions above use the same rational NHIM/local-control plant, satisfy every
explicit applicable architecture obligation, and have different exact closed
regions.  If two completions of an undefined domain predicate satisfy the
explicit clauses but assign different values to the target, those clauses do
not determine a unique target.  Therefore the canonical target is semantically
underdetermined.  QED.

This proof has no probability, randomness, uncountable-disturbance, or v0.8
premise.  Deleting the stochastic lane leaves every premise true.

## 4. Adversarial objections

The executable audit resolves twelve challenges: NHIM scope, same-plant
identity, architecture compliance, finite-versus-asymptotic scope, machine-
index normativity, union-of-registries semantics, rectangular-witness scope,
enumeration-versus-proof scope, deletion of v0.8, thin-initial-set scope, and
the robust-version graduation rule.  The union objection does
not choose a canonical answer: taking a union is itself another completion of
the undefined registry-domain predicate.

The thin-set objection is scope-limited rather than ignored.  The canonical
setting names `K_0` without requiring positive volume; the positive-volume
collar occurs only as a liveness example.  The global robust-version rule
remains a condition for graduation and a full resolution, and the machine
index explicitly says that graduation is unsatisfied.  This package therefore
uses the exact thin fixture only for the semantic stopping diagnosis and does
not promote it to a robust full classification.

Finally, the coordinate-artifact objection is rejected exhaustively.  The
harness applies all `24*2*2*24=2,304` relabelings of modes, actions, computed
read symbols, and raw read symbols.  It replays every mode word through horizon
three—193,536 words per registry—and obtains zero safety or language-count
failures.  The `(1,1)` and `(2,1)` corners are therefore invariant under these
declared finite coordinate changes.

## 5. Disposition

The theorem supports stopping further local capacity enumeration.  More exact
regions inside another chosen registry cannot determine which registry the
canonical source intended.  Productive work resumes on a normative selector,
an attributable error in the primary witness, or a genuinely new registered
class that changes the completion analysis.

It is a negative well-posedness/stopping result, not a full canonical solution
of the five requested mathematical classification tasks.
