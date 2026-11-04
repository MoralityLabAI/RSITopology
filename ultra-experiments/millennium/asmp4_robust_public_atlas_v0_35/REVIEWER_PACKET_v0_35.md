# Reviewer packet v0.35

## Claim to review

A compact cover by robust fixed-reset public connector basins produces uniform
time and separate read/write closing costs.  Under strict Lipschitz safety and
reset margins, this instantiates v0.33 safe closing.

## Exact fixture

- Plant: `x_next=2*x+u+x^2/4+w`.
- Safe core: `[-1,1]`.
- Reset cell: `[-1/8,1/8]`.
- Disturbance: `|w|<=1/128`.
- Source cells: 33 cells of radius `1/32`.
- Actuator words: 33 distinct one-step actions.
- Port costs: six read bits and six write bits.
- Robust error: `11/128 < 1/8`.

The independent implementation expands the nonlinear successor algebraically
instead of importing or calling the central implementation.  Both enumerate
3,171 admissible state/error/disturbance rows.

## Questions for hostile review

1. Does the error induction use the universal disturbance quantifier at every
   connector step?
2. Are the source-cell label and actuator word separately charged?
3. Does the dictionary include duration and reset-relevant actuator memory?
4. Are strict safe and terminal margins present?
5. Does a registered bi-Lipschitz conjugacy transport atlas existence without
   falsely preserving its numerical radii?
6. Is the fixed-reset result kept distinct from v0.34's all-pairs premise?

## Scope boundary

The package assumes robust nominal pointwise connector words with registered
public labeling and action authority.  It does not derive them from the full
canonical normally hyperbolic phrase.  It constructs a fixed-reset atlas, not
an all-pairs atlas, and does not assert minimality of the six-bit bounds.

## Reproduction

Run `run_verification.py`, `verify_robust_public_atlas.py`, and the focused
pytest file with bytecode and pytest caching disabled.  The claim artifact SHA
is `9B29D66AEA46B1586E2CDEF7CA9C8203BCA71E1753232CCB9FD59A85425C195E`.
