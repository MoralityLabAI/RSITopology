# ASMP-9 sharp interior availability protocol v0.15

## Status

This protocol prospectively freezes a fresh exact finite verification of the
v0.15 equal-count theorem. All development values in
`DEVELOPMENT_CENSUS_v0_15.json` are burned and cannot satisfy a gate.

## Frozen registry

The theorem registry is the Cartesian product

```text
k in {11,13,16}
n in {9,11,14}
epsilon in {1/16,3/20,3/10,7/20}.
```

The threshold registry is

```text
k in {11,13,16}
epsilon in {1/16,3/20,3/10,7/20}
delta in {1/8,1/16,1/40,1/200}.
```

The negative boundary uses the same fresh cycle lengths with
`epsilon=0` and `n in {9,14}`.

The unequal-allocation falsification registry is

```text
k in {6,7}
epsilon in {1/8,5/16}
total trials N in {k,k+1,...,k+7}.
```

Every quantity is computed with exact rational arithmetic. The unequal-count
registry tests only a finite conjecture and is not evidence for a general
balancing theorem.

## Gates

- `G0_registration_binding`: the execution head is the registration commit,
  the tracked tree is clean, the implementation commit is its ancestor, and
  every sealed file hash matches.
- `G1_registry_completeness`: exactly 36 theorem cells, 48 threshold cells,
  6 zero-interior cells, and 32 allocation cells are present, with no
  duplicates.
- `G2_exact_minimax_formula`: the closed form equals exhaustive endpoint
  enumeration in every theorem cell.
- `G3_balanced_endpoint_witness`: every exhaustive minimizer has the endpoint
  count or counts nearest `k/2`, and no other minimizer occurs.
- `G4_bound_and_drift_controls`: every sharp minimum dominates the v0.14
  conservative lower bound and is strictly below the one-low drift control.
- `G5_exact_trial_threshold`: every selected `n_star` meets its target and its
  predecessor does not.
- `G6_zero_interior_control`: every `epsilon=0` cell has zero worst-case
  availability.
- `G7_finite_allocation_falsification`: the balanced integer allocation is an
  optimizer in every fresh finite allocation cell. Passing this gate does not
  establish the unbounded balancing conjecture.
- `G8_resource_and_scope`: the CPU-only run finishes within 30 seconds and
  512 MiB, records exact output hashes, and preserves the claim boundary.

Every gate is binding for the joint registered verdict. Component results
remain legible: failure of `G7` refutes the finite balancing conjecture but
does not invalidate the analytic equal-count theorem.

## Resources

```text
CPU only
maximum wall time: 30 seconds
maximum peak resident memory: 512 MiB
GPU prohibited
```

## Claim boundary

A passing run verifies fresh exact instances of the analytic equal-count
minimax identity and trial threshold, and fails to falsify balancing on one
finite unequal-count registry. It cannot establish the general allocation
conjecture, model human or language-model preferences, solve general IRL, or
resolve ASMP-9.
