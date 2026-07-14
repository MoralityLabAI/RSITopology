# Edit sectioning v0.3: calibrated boundary result

Version 0.3 tests the sectioning bet rather than only the sectioning pipeline. The planted edit-identity boundary is shifted away from the fixed holonomy boundary by offsets `[-2,-1,0,1,2]`. Every offset uses the same angular observation and evaluation path.

For patch bias `B^2`, `N=8` cells, and `J=2` patches, the exact expected patch-minus-independent utility is

`(1-J/N) sigma^2/n - B^2 = 0.75 sigma^2/n - B^2`.

The empirical 180-cell crossover surface agreed with the analytic sign on every cell sufficiently far from zero, and every cell lay within three standard errors of its analytic expectation.

## Recoupled control

At offset `0`, noise `sigma=0.8`, and one observation per cell, the patch plan retained the v0.2 advantage:

- patch minus independent 95% CI: `[0.4752, 0.5258]`;
- patch minus global 95% CI: `[0.5284, 0.5482]`.

## Derived decoupled defect regimes

The gate cell for each nonzero offset was selected before outcomes by maximizing registered `sigma^2/n` subject to the analytic variance advantage being at most one tenth of planted bias.

| Offset | Sigma | n | Analytic effect | Empirical effect | 95% CI |
|---:|---:|---:|---:|---:|---:|
| -2 | 0.8 | 16 | -0.2784 | -0.2795 | [-0.2810, -0.2779] |
| -1 | 0.8 | 32 | -0.2163 | -0.2168 | [-0.2175, -0.2161] |
| 1 | 0.8 | 32 | -0.2163 | -0.2168 | [-0.2175, -0.2160] |
| 2 | 0.8 | 16 | -0.2784 | -0.2795 | [-0.2809, -0.2781] |

Thus the instrument wins when its pooling partition matches edit identity and loses decisively when the registered bias dominates its variance benefit. It did not manufacture an unconditional sectioning advantage.

The connector audit also passed: an unmeasured plaquette between two measured patches reported `touched_patch_count=2`, `boundary_impact=2`, and audit rank 1.

Registered capacity rank is 8 in every arm, while active signed-coordinate counts are global 1, patch 2, and independent 8. Only total squared norm is physically matched exactly; inactive padding is not effective-rank equivalence.

This remains CPU-synthetic calibration, not transformer edit evidence.

