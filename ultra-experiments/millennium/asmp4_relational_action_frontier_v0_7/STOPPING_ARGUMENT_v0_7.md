# ASMP-4 evidence-backed stopping argument v0.7

## Decision

The v0.7 theorem removes nonunique safe actions as a plausible objection to
the v0.6 stopping case.  On one fixed normally-hyperbolic relational plant,
three coherent sensor registries yield three different exact regions,
including a genuine architecture-dependent tradeoff.  More mathematics
inside any one registry cannot select a sensor registry omitted by the
canonical source.

## What the new harness tried

The v0.6 package used a unique safe action in each mode, so its full-reset
regions were rectangles.  V0.7 replaces that map by a safe-action
correspondence and permits arbitrary public-history selection between a
three-cell sensor and the raw four-cell sensor.  This is precisely the setting
where a read/write tradeoff could have invalidated a simple corner argument.

It does create a tradeoff, but one with a complete solution.  The exact region
is

~~~text
r>=log2 3, w>=1,
theta*r+(1-theta)*w>=log2 3, theta=log2(3/2).
~~~

A concave-moment induction proves the converse for every horizon and every
registered adaptive tree; public schedules attain the whole boundary.

## Harness strength

The bounded harness is used as a falsifier and regression certificate, not as
the infinite proof.  Two different implementations reproduce:

- all five safe local controller schemes;
- all 2,800 nonempty three-action relations through four modes;
- all 24,221 feasible relation/partition cells;
- the exact minimality result: 72 four-mode tradeoff relations and no smaller
  witness;
- 84,672 adaptive candidate trees and 1,872 undominated states at horizon
  three; and
- every finite Pareto count pair through horizon three.

The symbolic moment factor is exactly three for both boundary schemes and
`7/2` for every other raw assignment.  Thus the exhaustive data and the
all-horizon theorem test the same invariant by different routes.

## Same plant, three branches

With all computed partitions, the sufficient `d/e` statistic gives exact
region `[1,infinity) x [1,infinity)`.  With the two-partition adaptive grammar,
the exact region is the nonrectangular wedge.  With forced raw sensing, the
exact region is `[2,infinity) x [1,infinity)`.  Plant, evaluator, uncertainty,
control authority, safety relation, and metric do not change.

The canonical v0.1 source requires architecture choices to be registered but
does not define the admitted sensor grammar.  A harness can classify every
declared branch, but it cannot select a sensor registry on the author's
behalf.

## Robustness checks

The fork survives the source's prefix-free worst-case option: finite complete
transcript codes incur less than one extra bit, which vanishes per time step.
It also survives state-independent shared randomness under the conventional
zero-error accounting rules.  The rational embedding has unstable normal
multiplier `3/2`, nonzero normal control derivative at every safe registered
pair, and exact full reset.

State-dependent randomized observation kernels also fail to select or improve
a branch under support-cardinality accounting.  The support-derandomization
theorem selects a safe deterministic subtree with no larger port languages,
and two implementations find no counterexample across 53,108 four-mode
support kernels through four labels.

## Productive reopening conditions

Reopen the canonical lane if the problem supplies one of the following:

- a normative definition requiring every registered sensor class to contain
  all causal sufficient-statistic computations;
- a fixed restricted sensor grammar for which the variational region is being
  requested;
- a positive-error or noisy-channel convention replacing universal
  confinement; or
- an external proof audit identifying an error in the moment converse,
  rational embedding, or predecessor registration models.

Absent one of those inputs, additional state or horizon enumeration can
improve regression coverage but cannot resolve the missing quantifier.

The v0.8 successor confirms that “zero error” is itself a load-bearing
quantifier: countable disturbances collapse the almost-sure reading to a
common seed, while an uncountable diagonal separates it from support safety.
That stochastic branch requires an additional canonical probability-order
decision rather than weakening this stopping argument.
