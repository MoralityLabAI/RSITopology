# Completion audit v0.23

## Proved

- Exact same-step region `[2,infinity) x [2,infinity)` inherited from v0.22.
- Empty region for every positive integer observation delay under arbitrary
  current modes and safety from the first write.
- Capacity, controller memory, and plant-independent shared randomness cannot
  repair the common-history collision.
- Charged current preview restores the same-step region.
- A charged seed for constant `q` gives exact region
  `[1,infinity) x [1,infinity)`.
- Exact finite counts, 84 central adversary rows, 756 independent adversary
  rows, and five mutation rejections pass in two implementations.

## Verification boundary

The predecessor inventory contains 23 packages and 264 tests. This package
adds 10 focused tests, so the expanded chain contains 274 tests. The explicit
24-package regression passed all 274 tests in 296.96 seconds with Python
bytecode and pytest caching disabled to accommodate a full host drive.

## Not claimed

This is not an impossibility for predictable current modes, charged preview,
post-calibration safety, overlapping robust-control sets, or a global nonlinear
plant. The theorem freezes a precise timing and disturbance contract.
