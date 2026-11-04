# ASMP-9 conditional-fiber implementation repair v0.13.2

## Status

This amendment supersedes the resource-unavailable v0.13 and v0.13.1
execution attempts. It changes implementation only.

## Scientific invariants

The theorem, fresh registry, calibration formula, exact power band, ten gates,
success criterion, claim boundary, and 180-second/2-GiB CPU-only envelope are
unchanged.

## Additional permitted repair

For a consistently oriented `k`-cycle with equal trial count `n`, the frozen
theorem proves:

```text
D^T y=0 iff y=(z,...,z), z=0,...,n.
```

Version v0.13.2 constructs this fiber directly instead of enumerating the
ambient `(n+1)^k` grid. The direct and enumerated implementations must agree
on every burned cycle where exhaustive enumeration is tractable.
