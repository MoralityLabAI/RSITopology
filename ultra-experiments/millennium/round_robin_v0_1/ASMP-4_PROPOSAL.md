# ASMP-4 proposal: certified two-port transversal safety game

## Narrow subproblem

Measure the finite-horizon achievable region of one frozen evaluator-relative
control architecture while independently budgeting sensor-to-controller reads
and controller-to-actuator writes. The current confinement suite plants the same
volume obstruction and aligned-box construction on both ports; it validates the
mechanism but does not optimize the joint frontier. This experiment asks whether
evaluator-tangent instability becomes rate-relevant only through registered
tangent-to-normal coupling, and whether surplus capacity on one port can
compensate for a deficit on the other.

## Mathematical object and frozen hypothesis

Use the rational triangular plant

```text
n[t+1] = (3/2)n[t] + c*z[t] + u[t] + w[t]
z[t+1] = a_z*z[t]
```

with evaluator-safe set `|n| <= 1`, initial box
`|n|,|z| <= 1/4`, `a_z in {6/5,3/2}`, disturbance
`w[t] in {-1/32,+1/32}`, coupling
`c in {0,1/32,1/8,1/2}`, and horizon `T`. Motion in `z` is unrestricted.
Sensor partitions and actuator codewords come from sealed rational, ordered
families. A deterministic causal controller may retain finite memory but sees
only read symbols and emits only write symbols. For cumulative budgets
`(B_r,B_w)`, define

```text
V_T(B_r,B_w;c) = fraction of registered initial cells from which some
                 admissible causal code keeps |n[t]| <= 1 for every t<=T
                 and every registered disturbance path.
```

Backward safety-game synthesis returns the exact optimum within this frozen
finite architecture, using rational interval containment; it does not claim
optimality over arbitrary measurable encoders.

Frozen hypotheses: (H1) at `c=0`, the evaluator-only frontier is invariant to
`a_z` and agrees with the scalar normal-coordinate finite-horizon formula up to
registered integer-bit rounding; (H2) increasing nonzero `c` weakly shrinks the
region and produces at least one cell whose status changes by `T=8`; (H3) a
below-frontier read or write budget cannot be rescued merely by increasing the
other budget, unless an explicitly registered architecture-dependent tradeoff
is found by the exact solver.

## Smallest decisive experiment

Seal the plant, ordered partition family, action dictionary, memory bound,
budget-allocation rule, rational arithmetic, solver source, and tie-breaking
before solving. Sweep `T={2,4,6,8}`, `B_r,B_w={0,...,12}`, both `a_z`, and all
four couplings. Emit the exact viability fraction, feasibility certificate or
counterstrategy for every cell, and separate lower-bound, constructive, and
solver-optimal labels.

Controls:

1. stable normal mode (`a_n=4/5`) must admit zero-rate confinement;
2. full-state/full-action control must pass, separating information from
   authority failure;
3. an analog-state side channel must improve at least one deliberately
   under-budget cell;
4. symbol relabeling must leave the frontier unchanged;
5. deliberate controller references to state, plant, decoder, RNG, or callback
   must be rejected; and
6. exhaustive policy enumeration at `T<=3` must equal the backward solver.

The instrument is killed by any side-channel acceptance, rational replay
mismatch, missing liveness arm, solver/enumeration disagreement, or failure of
the `c=0` scalar calibration. H1 is refuted by a certified mismatch; H2 is
refuted if no registered feasibility or viability cell changes anywhere in the
exhaustive coupled grid; H3 is refuted by a solver-certified asymmetric
compensation cell.
Otherwise the relevant claim is `not_established`.

Evidence class: exact/certified within the registered finite architecture.
Any continuous-plant extrapolation remains a conjecture. **Controller failure
above threshold is not theorem evidence unless optimality is certified.**

## Optional scale-up

Replace the ordered scalar sensor family with a complete finite partition
grammar on a `33 x 33` rational cell complex and synthesize policies by
QBF/SAT, then repeat at `T<=12` with block allocations that realize quarter-bit
average rates. This tests whether the pilot frontier was imposed by ordered
partitions and estimates the `1/T` coasting correction. Infeasibility is called
certified only when the complete grammar is exhausted; timeout cells remain
`undetermined`.

## Resources

| Run | Wall time | CPU | RAM | Disk | GPU |
|---|---:|---:|---:|---:|---:|
| Pilot rational game | 4-12 min | 4 cores | <=2 GB | <=250 MB | none; 0 GPU-hours |
| Full ordered-family census | 45-120 min | 12 cores | <=8 GB | <=4 GB | none; 0 GPU-hours |
| Optional complete-partition scale-up | 4-12 h resumable | 16 cores | <=24 GB | <=20 GB | none; 0 GPU-hours |

## Consumer, artifact, and reason not to run

Consumer: the Confinement Width manuscript and HRMmmm interface-budget gate.
Reusable artifact: `two_port_transversal_game.py`, a sealed protocol, rational
certificates/counterstrategies, and a read-rate x write-rate phase diagram with
finite-horizon persistence receipts.

Reason not to run: the finite architecture may only re-express classical
invariance-entropy facts, while ordered partitions could make the observed
frontier rectangular by construction. A prior-art check or proof of the scalar
case may therefore buy more mathematical progress than the optional census.
