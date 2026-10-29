# ASMP-9 discounted-shaping development note v0.6

## Status

Unregistered development result. The cells below are burned and must not be
used as fresh verification cells.

## Structural result

For `0<gamma<1`, the discounted shaping operator is a constant-gain incidence
matrix. Its rank is:

```text
|V| - number_of_balanced_weak_components,
```

and the shaping-invariant reward quotient has dimension:

```text
|E| - |V| + number_of_balanced_weak_components.
```

A component is balanced exactly when its orientation admits an integer height
increasing by one on every edge.

The trajectory calculation gives a separate access result: a finite comparison
is shaping-invariant exactly when the two discounted boundary signatures
match. Same start and endpoint are insufficient if horizons differ.

## Development checks

- 16 tests pass.
- Exact rational rank matches the gain-graph formula for every oriented simple
  graph through four vertices at `gamma in {1/2,2/3}`.
- The `gamma=1` endpoint matches ordinary incidence rank on the same universe.
- All 59,049 oriented simple graphs on five vertices were classified by
  balance and quotient dimension as a development census.
- Only 3,991 of those five-vertex graphs have every weak component balanced;
  the balanced fraction is about `0.0676`.
- The five-vertex discounted quotient-dimension counts are:

  ```text
  dimension 0: 10,815
  dimension 1: 14,790
  dimension 2: 15,780
  dimension 3: 11,520
  dimension 4:  5,120
  dimension 5:  1,024
  ```

- One thousand seeded rational-potential trajectories satisfy the telescoping
  identity exactly.
- Equal-length same-endpoint routes preserve one quotient direction; adding a
  different-length shortcut makes the component unbalanced and removes it.

## Interpretation

Discounting does not merely perturb the ordinary cycle basis. It can delete one
shaping-invariant dimension from every unbalanced weak component. A directed
cycle has ordinary cycle rank one but discounted quotient dimension zero.

The usable finite-trajectory object is therefore a matched-boundary route
difference, not a generic graph loop.

## Claim boundary

This is classical gain-graph and potential-shaping mathematics specialized to
the ASMP-9 access grammar. It is not policy-based IRL, a finite-sample
preference result, or a novelty claim.
