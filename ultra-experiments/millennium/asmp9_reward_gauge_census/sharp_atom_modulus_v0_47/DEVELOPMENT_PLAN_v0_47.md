# ASMP-9 v0.47 development plan

## Load-bearing question

How much of the v0.46 robust deficiency is unavoidable under uniform
calibration coverage, rather than slack from method-of-types constants or an
independent-generator relaxation?

## Candidate exact instrument

Use the mandatory-atom theorem in `THEOREM_DRAFT_v0_47.md` on a frozen finite
grid of shared BSC parameters.  Precompute the exact full-adaptive
four-class risk once per channel point, then exhaust positive integer sample
allocations by the exact all-zero likelihood test

```text
product_q (1-p_q)^n_q > alpha.
```

This produces a lower and upper decision-deficiency modulus with the same
value.

## Development grid

The first, burned grid is:

```text
{0, 1/10, 1/5, 3/10, 2/5, 1/2}^3.
```

It contains 216 shared channels.  It is used only to test liveness, runtime,
allocation behavior, and boundary equality.  No development optimum is
claim-eligible.

The run completed and failed the registration gate as documented in
`DEVELOPMENT_RESULT_v0_47.md`: the coarse grid produced a zero root-group
modulus, hundreds of tied allocations, and six exact alpha-boundary
incidences.

## Prospective confirmation candidate

The second burned nonuniform grid concentrated around the exact zero-count
boundaries was:

```text
{0,.02,.04,.05,.06,.08,.10,.12,.13,.14,.15}^3.
```

The confirmation should use fixed v0.46-optimum and uniform allocations as
the primary comparison; the full allocation surface is descriptive because a
finite parameter grid naturally produces plateaus.  Before registration,
freeze:

- the disjoint total sample budget;
- deterministic confidence procedures as the estimand class;
- the strict `P(X=0)>alpha` rule;
- a no-equality or explicit-boundary gate;
- exact full-adaptive risk at every grid point;
- classification and root-group allocation predictions;
- the v0.46 method-of-types coupled upper and rectangle as nonsharp
  comparators;
- a positive binary/root control with an analytic exact answer; and
- a negative control where parameter radius does not determine deficiency.

The targeted burned check in
`DEVELOPMENT_TARGETED_RESULT_v0_47.md` passed all four liveness conditions and
found a pairwise four-class allocation-ranking reversal.  The next action is
therefore a disjoint `N=72` registration, not another development-grid search.
The confirmation must include the nonvacuous Buehler interpretation based on
the frozen total-error statistic.

## Stop rule

Do not register a confirmation if:

- the mandatory region is constant over all allocations;
- every decision problem selects the same allocation;
- the exact modulus is identically zero because the grid is too coarse;
- boundary equality makes the strict confidence rule ambiguous; or
- exact channel-risk computation exceeds the frozen resource envelope.

## Claim boundary

This is development-only.  Even a successful confirmation would close one
finite confidence-modulus obligation, not general minimax value
identifiability or ASMP-9.
