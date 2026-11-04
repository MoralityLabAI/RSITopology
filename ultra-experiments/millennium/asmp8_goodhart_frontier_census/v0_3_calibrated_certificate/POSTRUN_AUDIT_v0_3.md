# ASMP-8 v0.3a post-run audit

## Registered outcome

The frozen verdict is:

```text
calibrated_certificate_valid_but_vacuous
```

This is a composite protocol label. The result was not globally vacuous:
44.767% of truly positive diffuse-error policy/replicate cells were certified
at `m=512`, versus 0% under the registered Pinsker comparator. The label was
triggered specifically by failure of `G5_optimizer_transfer`: no top-spike
policy was certified in any diffuse-error replicate.

## What passed

- All nine calibration conditions had zero simultaneous `L1/L2` radius
  failures across 4,096 replicates. The maximum one-sided 95% exact binomial
  upper bound was 0.000731.
- No registered positive certificate was false-safe when the norm instrument
  was valid.
- Registered diffuse-error non-vacuity at `m=512` was 44.767%.
- Gibbs, best-of-n, and scrambled-Gibbs each had at least one policy certified
  in every `m=512` diffuse-error replicate.
- Coverage was nondecreasing with audit sample size in every error family.
- The rare-tail control was live: proxy-only produced 73,728 false-safe cells
  and movement-free RMSE produced 22,847. The registered certificate produced
  none conditional on valid radii.

## What failed

Every diffuse-error top-spike policy had zero certification probability at
`m=512`. For `alpha=0.1`, the coordinates were:

```text
proxy gain          = 0.05
L1 dual movement    = 6.30
L2 dual movement    = 0.793725...
L-infinity movement = 0.196875
```

The larger-alpha rows scale these gain and movement coordinates together, so
the same critical-radius ratios recur along the path. The actual diffuse
weighted-L2 error was about 0.03508, below the top-spike L2 critical radius of
about 0.0630, so an oracle-radius certificate would be positive. The
distribution-free Hoeffding second-moment radius at `m=512` remained too
loose. This localizes the failure to calibration efficiency under concentrated
policy movement, not to the v0.2 dual identity.

## Verification

The independent verifier replayed the complete scientific core and all three
CSV artifacts byte-for-byte. All registered source and artifact hashes match.
All 16 ASMP-8 tests pass.

## Next justified experiment

A successor may compare prospectively registered calibration instruments
(empirical Bernstein, stratified tail audits, or exact finite-population
sampling) on the same burned registry. It must not tune a method to make the
top-spike gate pass. The correct estimand is the audit cost required to certify
a concentrated policy shift at fixed soundness, with failure to certify
retained as an allowed outcome.

## Claim boundary

This is a finite synthetic calibration result. It does not establish that a
learned reward model has a valid uncertainty set, that top-spike optimization
is unsafe in general, or that ASMP-8 is resolved.
