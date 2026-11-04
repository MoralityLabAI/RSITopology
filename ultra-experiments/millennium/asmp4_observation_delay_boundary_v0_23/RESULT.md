# Result v0.23

The v0.22 zero-delay encoder collapse does not extend continuously to delayed
observation. On the registered plant, delay zero has exact region
`[2,infinity) x [2,infinity)`, while every positive integer delay has empty
region when `q_t` is arbitrary and no current preview is available. The
obstruction is informational rather than a bandwidth shortage: the two
current-mode branches require safe-control intervals separated by six even
when the delayed histories are identical.

A charged current-mode preview restores `[2,infinity) x [2,infinity)`. If the
mode is instead constant and announced by a charged seed before safety starts,
the predictable regime has exact region `[1,infinity) x [1,infinity)`.

The harness verifies 84 central delayed-history collisions and 756 independently
enumerated branch/state rows, exact finite collar counts, two resource seals,
and five rejected mutations. The import-independent implementation agrees.

This result requires arbitrary current `q`, safety from the first write, and no
charged preview in the impossible architecture. It does not cover predictable
disturbances, a calibration phase before safety, or plants whose robust-control
sets overlap.

The complete 24-package chain passes all 274 tests in 296.96 seconds.

The v0.24 successor embeds this timing fork in a weighted support-functional
formula: the delayed empty region has infinite support value, while the
same-step and preview rectangles have finite constant support. That theorem is
exact for reset-block-generated regions and does not alter this timing claim.
