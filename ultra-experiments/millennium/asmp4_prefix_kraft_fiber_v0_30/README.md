# ASMP-4 prefix Kraft fiber transfer v0.30

This package closes the sequential prefix-free cost gap left explicit in
v0.29. For a causal target-to-source tree factor, it proves

`P_target(T) <= P_source(T) + C(T)`,

where `C(T)` is the worst-path sum of the per-prefix rounded local successor
fibers `ceil(log2 m(p))`.

The rounding location matters. A deterministic image of a full ternary tree
costs two sequential binary bits per step, whereas the unrounded local-fiber
entropy is only `log2 3`; even one final ceiling is too small from `T >= 3`.
The terminal-bijective disclosure family separately shows that terminal fiber
one can hide an exact one-third bit per-step prefix-cost gap.

Evidence includes:

- all 332,928 binary causal morphisms through depth three in the central
  census;
- 512 regular-clone rows and 16,384 mixed schedules;
- an import-independent census of all 4,096 binary output maps on the full
  depth-two ternary tree;
- 30 independently constructed regular trees and 15,625 independent mixed
  recurrences;
- dyadic sparse, maximum-fiber, burst/limsup, and eight mutation boundaries.

Run the focused checks from this directory:

```powershell
python run_verification.py
python verify_prefix_kraft_fiber.py
python -m pytest -q
python -m ruff check .
```

See `THEOREM.md` for the proof and `PRIOR_ART_BOUNDARY_v0_30.md` for the scope
boundary.
