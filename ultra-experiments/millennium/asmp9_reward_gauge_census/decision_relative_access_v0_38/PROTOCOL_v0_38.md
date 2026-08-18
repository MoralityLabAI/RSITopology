# ASMP-9 decision-relative access protocol v0.38

## Registration state

`prospective_confirmation_not_yet_executed`

This protocol becomes binding only when its file hash, the source hashes, the
environment lock, and the exact confirmation grid are committed and pushed
in a registration record before `run_confirmation()` is called.

## Question

In one finite three-class reward grammar, what query access is necessary and
sufficient to transfer every full-access policy-regret rule up to a declared
additive target-risk tolerance?

The primary estimand is the target-relative deficiency `delta_D` defined in
[`DEFINITION_AUDIT_v0_38.md`](DEFINITION_AUDIT_v0_38.md). Secondary
comparators are the optimized value gap `G_D` and ordinary deficiency on the
expanded target-by-nuisance experiment.

## Frozen reward grammar

- three target/decision classes;
- three deterministic policies with occupancy vectors `e_0,e_1,e_2`;
- reward representatives `r_theta=e_theta`;
- one nuisance bit selecting `r_theta` or
  `r_theta+(1,1,1)`;
- constant shift as the only licensed gauge;
- normalized policy regret equal to zero on the matching policy and one on
  the other two policies; and
- rational probabilities throughout.

## Frozen query grammar

For `0 <= low < high <= 1`:

```text
q_target_0: P(1|theta) = (high,low,low)
q_target_1: P(1|theta) = (low,high,low)
q_gauge_shift: output = nuisance bit.
```

All query outputs are conditionally independent given `(theta,xi)`. Full
access contains all three queries.

The nuisance law is target-independent and takes two registered forms:

```text
P(xi=1|theta) = 1/2  for every theta
P(xi=1|theta) = 2/3  for every theta.
```

The second row checks that gauge nullity is due to target independence, not
the special symmetry of a fair bit.

## Confirmation grid

The three confirmation strengths are:

```text
(high,low) in {(5/7,2/7), (7/8,1/8), (5/8,3/8)}.
```

Crossing them with the two nuisance laws gives six cells. The four burned
development strengths

```text
(2/3,1/3), (3/4,1/4), (4/5,1/5), (3/5,2/5)
```

are excluded.

## Frozen predictions

For `gap=high-low`:

1. deleting either target query has
   `delta_D = gap/2`;
2. the target-query pair has `delta_D=0` relative to full access;
3. appending or dropping the marginalized gauge observation has ordinary
   target-experiment deficiency zero;
4. gauge-only access has the same `delta_D` as no access;
5. omitting the gauge observation has expanded-parameter deficiency `1/2`;
6. no access has `delta_D > gap/2` on every registered cell.

Consequently:

- below tolerance `gap/2`, both target queries are necessary;
- at tolerance `gap/2`, either one target query is inclusion-minimal; and
- the gauge query is never part of an inclusion-minimal target-relative
  access family.

## Gates

- **P0 — definition and solver fidelity:** the preflight suite reproduces the
  Blackwell anchors, the equal-minimax/positive-relative witness, the nuisance
  marginalization witness, exact primal-dual feasibility, and the burned
  half-gap cases.
- **S0 — seal integrity:** the executor must match the registration,
  protocol, source, and environment hashes before evaluating any confirmation
  cell.
- **R0 — exact census:** exactly six registered rows are returned, with no
  missing, duplicate, or extra `(high,low,nuisance-law)` cells.
- **T0 — deletion theorem:** both one-target-query deficiencies equal
  `gap/2` in every cell.
- **G0 — gauge null:** the target-query pair is equivalent to full marginal
  access in both directions, and gauge-only access equals no access.
- **E0 — expanded separation:** target-query access without gauge access has
  expanded-parameter deficiency exactly `1/2`.
- **A0 — boundary nonvacuity:** no-access deficiency is strictly greater than
  `gap/2` in every cell.

All gates are conjunctive. Any failed or unavailable gate yields
`registered_gate_failed`; thresholds are not revised after execution.

## Exactness and resource ceiling

SciPy/HiGHS may propose an active constraint set. Every accepted optimum is
reconstructed in exact rational arithmetic and must have:

- a feasible exact primal;
- a feasible nonnegative exact dual; and
- identical primal and dual objective values.

The executor is CPU-only. The frozen ceilings are:

- wall time: 600 seconds;
- peak working set: 1 GiB;
- no network;
- one process; and
- no unregistered parallel reduction.

Crossing a ceiling invalidates the run rather than changing the grid.

## Reporting

The result must report all exact fractions, gate states, code/protocol/
registration hashes, elapsed time, environment identity, and the distinction
among `G_D`, `delta_D`, and expanded deficiency.

## Claim boundary

A passing run establishes the exact threshold only for this finite symmetric
reward/query/nuisance grammar. The comparison theorem is classical. The run
does not establish general reward identifiability, robustness to correlated
or strategic nuisance, a human-value model, a real-transformer result, or
resolution of ASMP-9.

