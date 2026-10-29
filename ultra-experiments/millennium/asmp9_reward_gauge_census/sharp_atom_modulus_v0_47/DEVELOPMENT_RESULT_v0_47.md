# ASMP-9 v0.47 burned development result

## Verdict

**`coarse_grid_not_admissible_for_confirmation`**

The mandatory-atom theorem and exact decision-risk pipeline are operational,
but the registered development stop conditions reject the six-level grid as a
confirmation design.

This is a development result.  It was not prospectively registered, is not
claim-eligible, and cannot satisfy a v0.47 scientific gate.

## Burned design

- Shared BSC grid:

  ```text
  {0,1/10,1/5,3/10,2/5,1/2}^3.
  ```

- 216 exact channel points.
- Four-class risk from the complete 3,748-policy horizon-two experiment.
- Root-group risk `p_root`.
- Total budget `N=66`.
- All 2,080 positive integer allocations.
- Uniform coverage level `1-alpha=0.95`.
- Four CPU workers.

## Exact findings

| Decision problem | Sharp atom modulus optimum | Number of optimizing allocations | Uniform modulus |
|---|---:|---:|---:|
| four-class identification | `1/10` | 323 | `1/10` |
| root-group loss | `0` | 666 | `1/10` |

The classification modulus is nonzero and the two decision problems have
different optimizer sets.  Those facts are insufficient for registration:

1. the root-group optimum is identically zero because the first nonzero grid
   point is too coarse relative to the zero-error likelihood boundary;
2. hundreds of allocations tie, so the grid cannot resolve the allocation
   surface; and
3. six allocation/parameter incidences satisfy
   `P_p(X=0)=alpha` exactly.

The strict confidence theorem handles equality correctly, but a confirmation
must either exclude such equality prospectively or register it as a distinct
boundary stratum.

The run took `318.380` seconds.  Exact artifact hashes are:

```text
development result:
d41f441c4c7e2d26b6fcc2f3645fe742206b2ce2d6748020ffdc9007e10cf316

four-class channel-risk table:
021cbeabfc71b99e64e5cf2839738e8c93a5d83384ab3d47666d69996d085281

four-class allocation rows:
2bf075633df636e766a169105c8372f000fa0918f1172843c01a3d00852ffbb7

root-group allocation rows:
62f90123bb376c6b0a137e6453f0ac323bc3871d55f36429c59278731070fa0d
```

## What survives

The theorem-level instrument did not fail:

```text
mandatory set
  = {p : P_p(X=0)>alpha}

sharp atom modulus
  = max_{p in mandatory set} exact decision risk(p).
```

For every allocation and both decision problems, the mandatory-set lower and
spike-confidence upper matched exactly.  The failure is resolution of the
parameter grid, not validity of the modulus.

## Successor design

Do not register the already proposed broad eleven-level grid without another
burned check.  First:

1. concentrate rational levels around the analytic zero-count boundaries
   `1-alpha^(1/n)` for the allocations of interest;
2. treat the exact v0.46 optimum and uniform designs as primary fixed points,
   rather than requiring a unique optimizer from a discretized step surface;
3. keep a complete allocation census as descriptive;
4. report `P(X=0)=alpha` as a separate exact boundary class; and
5. precompute each channel risk once and cache survival powers before scaling
   the grid.

The prospective target remains a matching decision-deficiency modulus, not an
allocation win.

## Claim boundary

This result says only that one coarse finite grid is inadequate for a
confirmation.  It is not evidence for or against a continuous minimax modulus,
real preference identification, or ASMP-9.
