# ASMP-9 correlated gauge access protocol v0.39

## Registration state

`prospective_confirmation_not_yet_executed`

The confirmation is not run until this protocol, its machine-readable twin,
the source, the reused v0.38 solver, the environment lock, and the exact
confirmation universe are hash-sealed in a pushed registration commit.

## Question

When the representative selected from a decision-equivalent reward gauge
orbit is statistically correlated with the target value class, how much
target information does observing that representative choice carry; when can
it replace a missing target query; and what happens when the choice is
randomized by intervention?

## Frozen reward and decision grammar

- targets and policies: `{0,1,2}`;
- normalized policy regret: zero for the matching policy, one otherwise;
- reward representatives:
  `r(theta,xi)=e_theta+xi*(1,1,1)`;
- constant reward shift is the only licensed gauge; and
- `xi` is observed as a binary gauge-selection query.

Gauge equivalence is a statement about decisions under each representative.
It is not assumed to imply target independence of `P(xi|theta)`.

## Primary estimands

1. The registered decision-relative deficiency from a constant experiment to
   the observed gauge-selection experiment.
2. Ordinary total-variation deficiency for the same comparison.
3. Relative and ordinary deficiency of retained access `(q1,q_gauge)` against
   reference access `(q0,q1)`.

For a probability vector `p_theta=P(xi=1|theta)`, define the leakage radius:

```text
ell(p) = (max_theta p_theta - min_theta p_theta)/2.
```

## Disjoint confirmation universe

Leakage vectors:

```text
(7/9,2/9,4/9)
(1/6,5/6,1/2)
(4/11,4/11,4/11)  [flat control]
```

Stochastic intervention probabilities:

```text
lambda in {2/7,5/9}.
```

Symmetric access strengths:

```text
(high,low) in {
  (6/7,1/7),
  (7/10,3/10),
  (11/16,5/16),
  (9/14,5/14)
}.
```

For every strength, the gauge assignment is one of:

```text
q0, complement(q0), q1, q2, constant(1/2).
```

The burned strengths `(2/3,1/3)`, `(3/4,1/4)`, `(4/5,1/5)`, and
`(3/5,2/5)` are excluded. The exploratory `(5/7,2/7)` transverse cell is also
excluded.

## Frozen predictions

1. Observational gauge leakage has exact decision-relative and ordinary
   radius `ell(p)`; both reverse deficiencies are zero.
2. `do(xi~Bernoulli(lambda))` makes every target row identical and both
   leakage radii zero.
3. With reference `(q0,q1)` and retained query `q1`:
   - `q_gauge=q0` or its complement gives deficiency zero;
   - `q_gauge=q1` gives deficiency `(high-low)/2`;
   - target-independent `q_gauge` gives `(high-low)/2`; and
   - `q_gauge=q2` gives `high*low*(high-low)` on every registered cell.
4. The assignments `q0`, `q1`, and `q2` have equal leakage radius but three
   distinct substitution deficiencies.

## Gates

- **P0 — preflight:** all eleven registered tests pass before registration.
- **S0 — seal:** every registered source, protocol, environment, and reused
  solver hash matches before outcomes are computed.
- **R0 — universe:** exactly 3 leakage, 2 intervention, and 20 alignment rows
  are returned, with exact set equality.
- **L0 — leakage theorem:** ordinary and decision-relative values equal the
  half-range formula, with zero reverse deficiency.
- **I0 — intervention erasure:** both randomized-intervention rows have zero
  leakage.
- **A0 — aligned substitution:** direct and complemented `q0` assignments
  have zero deficiency.
- **Q0 — missing-query threshold:** redundant `q1` and constant assignment
  both equal the half-gap threshold.
- **T0 — transverse branch:** `q2` equals `high*low*(high-low)` in both
  estimands.
- **U0 — scalar insufficiency:** equal leakage radius coexists with three
  distinct access values at every strength.
- **RESOURCE:** elapsed time and peak working set stay within the sealed
  ceilings.

Every gate is conjunctive. Thresholds are not revised after registration.

## Exactness and resources

SciPy/HiGHS proposes an active set, while the inherited v0.38 solver accepts
an optimum only after exact rational primal feasibility, nonnegative exact
dual feasibility, and equality of primal and dual objectives.

- CPU only;
- one process;
- one BLAS thread;
- no network;
- wall ceiling: 600 seconds; and
- peak working-set ceiling: 1 GiB.

## Claim boundary

A passing run establishes an exact access distinction only for this finite
three-target gauge/query grammar. It is a classical decision-theoretic
specialization. It does not establish a new Blackwell, Le Cam, Torgersen,
Goel–DeGroot, or causal-inference theorem; general reward identifiability;
that real reward-model training chooses gauge representatives by this
mechanism; real-transformer evidence; or resolution of ASMP-9.
