# ASMP-9 decision-directed sample-allocation protocol v0.45

## Status

This protocol freezes the disjoint `N=60` confirmation after a burned
development census at `N=54`. Development outputs are design evidence only
and cannot satisfy a confirmation gate.

## Frozen scientific object

- Four targets.
- Three deterministic-center binary queries in order
  `(root,left,right)`.
- Horizon two.
- One shared symmetric flip parameter per query.
- Known-target calibration error indicators pooled across targets within a
  query.
- Total acquisition budget `N=60`.
- Positive integer counts for every query.
- Familywise level `alpha=0.05`.
- Binary method-of-types toll

  ```text
  kappa(n) = ceil_1e-12(log(3(n+1)/0.05)/n).
  ```

- Policy-specific KL occupancy, outward Pinsker radii, and exact robust
  directed deficiency inherited from v0.44.

The complete allocation universe is the 1,711 positive compositions of 60
into three labelled query counts.

## Decision problems

1. `4_class_identification`: four-target zero-one loss.
2. `root_group`: zero-one loss for `{0,1}` versus `{2,3}`.
3. `all_query_serial_control`: a matched information objective whose policy
   uses each query exactly once.

## Frozen predictions

The safe constructive bounds predict:

```text
classification optimum : (26,17,17)
root-group optimum      : (58,1,1)
serial-control optimum  : (20,20,20)
```

The exact LP, not the constructive formula, decides the first two scientific
outcomes. The classification formula is allowed to be conservative but is
never allowed to underbound the exact endpoint.

## Exact lower benchmark

For each distinct count used by the optimal and uniform allocations, compute
the exact equal-prior testing error between

```text
Bin(n,1/2-d) and Bin(n,1/2+d)
```

over `d=j/200`. The largest `d` with Bayes error strictly greater than
`1/20` is a certified lower bound on a uniformly valid Bernoulli confidence
radius at that count. Equality does not count as an obstruction.

The lower benchmark must be reported beside the constructive result. It is not
a gate requiring the two to match.

## Gates

All gates are deterministic.

| Gate | Frozen requirement |
|---|---|
| `P0` | exactly 21 preregistration tests pass |
| `S0` | protocol, theorem, prior-art, source, test, audit, runner, verifier, environment, and inherited-source hashes match registration |
| `U0` | exactly 1,711 positive allocations per decision problem; totals and query order exact |
| `K0` | all 60 method-of-types tolls are positive, outward rational, and strictly decreasing |
| `E0` | exact LP evaluates all 3,422 problem/allocation pairs |
| `B0` | constructive bound underbounds the exact LP zero times |
| `A0` | four-class exact optimum is unique `(26,17,17)` and strictly improves on uniform by more than 1% relatively |
| `D0` | root-group exact optimum is unique `(58,1,1)` and strictly improves on uniform by more than 35% relatively |
| `C0` | matched serial control has unique uniform optimum `(20,20,20)` |
| `L0` | every reported two-point row has Bayes error above `1/20` and its next grid point has error at most `1/20` |
| `R0` | optimum allocations for the two losses differ |
| `RESOURCE` | at most 420 seconds wall time, 1.25 GiB peak aggregate working set, and four worker processes |

If a source or environment hash fails, status is
`invalid_provenance`. If exact and constructive arithmetic disagree through an
underbound, status is `theorem_or_implementation_failure`. If provenance and
arithmetic are valid but any scientific prediction gate fails, status is
`decision_directed_allocation_not_established`. Only all gates passing returns
`decision_directed_sample_allocation_established`.

## Reproducibility

The confirmation writes:

- the exact formula-universe audit;
- the summarized optimum/control/lower-bound result;
- a run receipt with all input and output hashes;
- an independent replay result; and
- a release manifest.

The exact row universe is summarized by a canonical row-list SHA-256 per
decision problem. Independent replay must reproduce both hashes and every
scientific field.

## Claim boundary

The confirmation concerns one finite iid shared-parameter calibration grammar.
It does not show that target-specific cells can always be pooled, establish a
general optimal-design or minimax theorem, make exponential policy compilation
efficient, validate a real preference channel, or resolve ASMP-9.
