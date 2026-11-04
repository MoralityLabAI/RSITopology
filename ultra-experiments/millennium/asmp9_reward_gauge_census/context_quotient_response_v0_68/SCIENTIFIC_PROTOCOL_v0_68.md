# ASMP-9 context-quotient scientific protocol v0.68

Status: **scientific design frozen; execution unregistered and unauthorized**.

The machine-readable authority is `protocol_v0_68.json`. This document explains
the choices frozen there.

## Primary object

Each nuisance block is one fixed `(scenario, display order, tensor shape)`.
Arbitrary common score offsets inside a block are quotiented out. Every
scientific endpoint is a zero-sum contrast inside one such block.

The independent unit is a scenario. The two targets and two display orders are
four repeated measurements. They are not counted as four independent trials.

## Fresh scenarios

The manifest contains 12 new behavior families, each with one construction and
one confirmation scenario. No v0.67 scenario, scenario ID, option, situation,
or reason string is reused.

Every semantic input is run twice as a singleton forward. Each split therefore
contains:

```text
12 scenarios
22 semantic inputs per scenario
2 exact repeats
= 528 score records.
```

## Primary endpoint

For target direction `d`, content-minus-label specificity in display order `o`
is

```text
specificity(c,o,t)
  = d(t) * [score(c,o,content_t) - score(c,o,label_t)].
```

The score-lattice guard is frozen at `1/64`, the observed resolution of the
burned v0.67 score channel, plus a separately computed analytic float guard.

A scenario satisfies the practical coverage rule only if specificity is
strictly above that combined epsilon for both target directions in both
display orders.

The `10/12` rule is a practical coverage floor, not a binomial significance
calculation. Statistical evidence uses a scenario-level exact randomization:

```text
for each of the 2^12 sign assignments:
  swap content and label together for all four measurements in each
  sign-flipped scenario;
  compute the mean specificity within each scenario;
  take the mean of those twelve scenario means.
```

The exact one-sided p-value is the fraction of all 4,096 assignments whose
mean-of-scenario-means statistic is at least the observed statistic. The
scenario-level mean changes sign exactly under a content/label swap; the
worst-direction statistic is retained as a separate practical robustness
condition. `L0` requires:

- at least 10 of 12 practical-coverage successes;
- observed median worst-direction specificity above endpoint epsilon; and
- exact randomization `p <= 0.05`.

This keeps targets and display orders inside their scenario cluster and avoids
assuming that a four-inequality scenario-success event has null probability
one half.

This finite-registry statement does not turn the twelve scenarios into a
random sample of human values or deployment contexts.

## Instrument gates

- `N0`: every byte-identical singleton repeat must be exactly equal.
- `Q0`: every endpoint must annihilate the registered nuisance design.
- `S0`: a synthetic common-mode shift must vanish, while an arm-by-order
  interaction must survive.
- `L0`: the practical coverage, worst-direction margin, and exact clustered
  sign-flip conditions all pass.
- `G0`: the expanded two-order specificity intervals have one common
  intersection.

`G0` is deliberately separable. Its failure yields a valid
`local_response_family_established_context_conditioned` result when the local
gates pass. It does not retroactively invalidate the local contrasts.

## Confirmation authorization

Construction can authorize the local confirmation lane only after `N0`, `Q0`,
`S0`, and `L0` pass. Construction can authorize the global lane only if `G0`
also passes.

Confirmation uses the same three-part `L0` rule without refitting. A global
confirmation additionally requires every confirmation interval to intersect
the exact construction intersection sealed before confirmation inference.

The old v0.67 confirmation split remains closed and is excluded from this
universe.

## Execution hold

This protocol does not yet bind a model runner or environment. No inference is
authorized until an execution registration hashes:

- the exact runner and analyzer;
- the deterministic 528-record job list and order;
- model and tokenizer bytes;
- environment and resource limits;
- tests and prereveal validator; and
- this protocol and scenario manifest.

## Claim boundary

A positive result would establish only that one model expresses
nuisance-quotiented, order-transportable context-local response contrasts on a
finite frozen registry. A positive `G0` would establish compatibility with one
shared magnitude, not identify a value. The protocol cannot establish moral
truth, human preference, a persistent model value, a reward-shaping orbit,
recursive self-improvement, or resolve ASMP-9.
