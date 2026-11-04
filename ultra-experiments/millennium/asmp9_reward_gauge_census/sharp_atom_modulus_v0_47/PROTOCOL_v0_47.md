# ASMP-9 sharp atom-modulus protocol v0.47

## Status and development disclosure

This protocol freezes the disjoint `N=72` confirmation. Two earlier runs are
burned and cannot satisfy a confirmation gate:

1. a full `N=66` census on the coarse six-level grid; and
2. a targeted `N=66` comparison on the final eleven-level grid.

The targeted run found a pairwise allocation-ranking reversal. The present
protocol tests that prediction at a new total budget with allocations fixed
before any `N=72` decision-risk outcome is evaluated.

## Frozen confidence estimand

Let `Theta` be the registered finite shared-channel grid and let `T` be the
total number of calibration errors. For deterministic, nondecreasing direct
upper confidence bounds with uniform coverage `1-alpha`, use

```text
U(t) = max {d(theta) : P_theta(T <= t) > alpha}.
```

This is the finite Buehler bound under the frozen ordering. At `t=0`, the
event is the unique all-zero count vector and

```text
P_p(T=0) = product_q (1-p_q)^n_q.
```

Therefore

```text
U(0)
  = max {d(p) : product_q (1-p_q)^n_q > 1/20}.
```

The same set is mandatory in every deterministic honest confidence set at
that atom, and a spike confidence set attains it. The lower and upper moduli
must consequently agree exactly.

## Frozen universe

- Four latent targets and queries `(root,left,right)`.
- Horizon two and all 3,748 symbolic deterministic adaptive policies.
- One independent calibration cell per query, with one shared symmetric flip
  rate in each cell.
- Zero observed known-target calibration errors.
- `alpha=1/20`.
- Total budget `N=72`.
- Exact parameter grid

  ```text
  {0,.02,.04,.05,.06,.08,.10,.12,.13,.14,.15}^3.
  ```

- Exactly 1,331 shared-channel parameters.
- Four fixed comparisons:

  ```text
  four-class directed : (30,21,21)
  root-directed       : (70,1,1)
  uniform             : (24,24,24)
  ```

The fixed allocations are extrapolations from the registered v0.46 `N=66`
optima, not optimizers selected on `N=72` outcomes. A global sharp-modulus
allocation census is outside the primary claim.

## Decision risks

1. `four_class_identification`: exact minimax zero-one risk of the complete
   horizon-two adaptive experiment.
2. `root_group`: exact risk `d(p)=p_root`.

Four-class risks are evaluated only for the union of parameters mandatory for
the two fixed classification designs, plus registered controls. Every one of
the 1,331 parameters remains in the confidence universe and coverage check.

## Frozen comparators

At every fixed design report:

1. the exact sharp atom modulus;
2. the v0.46 method-of-types coupled endpoint, evaluated at the same
   allocation; and
3. the inherited v0.45 independent-generator rectangular endpoint, evaluated
   by the exact robust-deficiency LP at the same allocation.

The comparators are upper constructions, not candidate lower bounds.

## Frozen predictions

1. Every sharp atom lower equals its matching upper and is nonzero.
2. Four-class ranking reversal persists:

   ```text
   sharp(uniform) < sharp((30,21,21)).
   ```

3. Root-directed sampling remains beneficial:

   ```text
   sharp((70,1,1)) < sharp(uniform).
   ```

4. The v0.46 method-of-types coupled endpoint is strictly above the sharp
   modulus in all four comparisons.
5. The independent-generator rectangle is strictly above the v0.46 coupled
   endpoint in all four comparisons.

## Controls

- `analytic_root`: the root-group risk table must equal `p_root`, and every
  reported root witness must attain the stated maximum.
- `radius_insufficiency`: the two channels

  ```text
  (.10,0,0) and (.10,.10,.10)
  ```

  share `L_infinity` radius `.10` but have exact four-class risks `.10` and
  `.19`. Thus parameter radius alone cannot determine decision deficiency.
- `boundary`: no registered fixed design may have a parameter with
  `P_p(T=0)=alpha`. The strict confidence boundary is otherwise declared
  unavailable rather than silently rounded.
- `minimum_statistic`: the exact total-error CDF must begin at the registered
  all-zero probability and end at one.

## Deterministic gates

| Gate | Requirement |
|---|---|
| `P0` | exactly 15 dedicated tests pass |
| `S0` | every sealed source, theorem, protocol, prior-art, environment, runner, verifier, and inherited dependency hash matches |
| `U0` | `N=72`, exact query/design/grid universe, 1,331 unique parameters |
| `E0` | exactly 3,748 symbolic adaptive policies |
| `B0` | zero alpha-boundary equalities at every fixed design |
| `C0` | all four mandatory-set lower/upper pairs match exactly and their spike coverage is at least `19/20` over the full grid |
| `L0` | all four sharp moduli are strictly positive |
| `A0` | both frozen allocation comparisons have the predicted strict ordering |
| `K0` | method-of-types coupled upper is strictly above the sharp modulus in all four rows |
| `R0` | exact rectangle is strictly above the method-of-types coupled upper in all four rows |
| `N0` | radius-insufficiency control equals `.10` versus `.19` at common radius `.10` |
| `T0` | total-error minimum-atom identities and analytic root witnesses check exactly |
| `RESOURCE` | wall time at most 180 seconds, aggregate working set at most 1 GiB, at most four classification workers |

`P0`, `S0`, `U0`, `E0`, `B0`, `C0`, `N0`, and `T0` are instrument-validity
gates. Any failure returns `invalid_sharp_atom_instrument`. With a valid
instrument, failure of a scientific prediction returns
`sharp_atom_prediction_not_established`. Only all gates passing returns
`sharp_atom_modulus_established_allocation_ranking_changed`.

## Reproducibility

The run writes canonical exact-risk rows, comparator rows, the summarized
result, and source/hash/resource receipts. An independent verifier recomputes
the complete scientific payload and requires byte-equivalent canonical JSON.
Artifacts are compare-or-fail and the release manifest is built only after
verification.

## Claim boundary

The theorem is classical finite confidence theory specialized to one
registered all-zero atom, one frozen statistic, one finite shared-BSC grid,
and two finite decision problems. A successful result establishes a sharp
conditional decision modulus and diagnoses allocation-dependent slack in the
earlier upper construction. It does not establish a globally optimal
statistic, randomized-confidence optimality, continuous-channel minimax
rates, strategic response, real preference access, or resolution of ASMP-9.
