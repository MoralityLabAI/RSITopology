# Counterexample to factorization-only local safety sufficiency

## Literal clause under test

ASMP-2 v0.1 says that a regular data-dependent local first-order safety
certificate exists with finite minimax radius **if and only if** the pathwise
derivatives of safety and utility factor continuously through the identified
score experiment with a positive conditioning margin.

The “if” direction is false unless robust policy feasibility and a safety
margin are additional premises.

## Exact model

Let

```text
theta in [-1/2,1/2],
X ~ Bernoulli(1/2+theta/4),
A = {-1,+1},
L(a,theta) = 1/2+a theta/4,
U(a,theta) = 1,
epsilon = 1/2,
u_0 = 4/5.
```

The registered policy class contains the two deterministic actions; external
policy randomization is not registered.

At the source reference `theta=0`:

- the observation family is dominated and QMD with common full support;
- Fisher information is exactly `1/4`;
- the risk derivatives are `-1/4` and `+1/4`;
- each derivative factors through the observation-probability derivative
  `1/4`, with factors `-1` and `+1`; and
- utility is constant above the floor.

Thus the stated factorization and positive-conditioning premises hold.

But each action has worst local-ball risk

```text
sup_(|theta|<=1/2) L(a,theta) = 5/8 > 1/2.
```

Whichever deterministic action a data-dependent procedure outputs, the event
in the canonical certification goal is false. No sample size or estimator can
repair the absence of a robustly feasible action.

## Interpretation

This does not refute adjoint-score theory. It shows that regular estimability
of each risk derivative is different from existence of a policy satisfying a
uniform inequality. A sufficient local safety theorem needs at least:

1. a nonempty robust good-action set at the reference experiment; and
2. a positive margin or a separately typed one-sided/nonregular boundary
   analysis.

If randomized policies are intended, their inclusion and the functional's
behavior under mixing must be frozen. In this particular affine example an
unregistered half-half mixture cancels the risk derivative, illustrating why
the action grammar is load-bearing.

## Resolution consequence

The literal local iff in v0.1 is refuted by a dominated QMD model with positive
utility and positive information. Repairing it requires new feasibility,
margin, and policy-randomization assumptions, which the set's own versioning
rule treats as a new problem version.

The broader classification program is not automatically resolved by this
counterexample; `RESOLUTION_AUDIT_v0_2.md` tracks that distinction.
