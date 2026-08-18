# Reviewer packet v0.34

## Review order

1. Check that `z` contains only charged public belief and registered memories,
   never hidden plant state for free.
2. Verify that connectedness of the finite safe overlap nerve follows from
   connectedness of the compact public component.
3. Check the path concatenation proof and the separate sums for time, read
   cost, and write cost.
4. Confirm that the final local segment resets all registered private memory.
5. Apply the resulting constant bounds to v0.33's safe-closing hypotheses.
6. Inspect the noncompact ladder, disconnected nerve, unsafe-overlap, hidden-
   mode, and private-memory counterboundaries.
7. Run the central and independent graph censuses.

## Load-bearing distinctions

- public-information controllability versus hidden-state controllability;
- safe-core overlap versus ambient geometric overlap;
- local existence versus compact uniform bounds;
- state return versus full registered memory reset; and
- separate read/write connector costs versus one scalar surrogate.

## Remaining attack

The next theorem must start from a formal normally hyperbolic nonlinear plant,
sensor, disturbance, and actuator registration and construct the local public
connector certificates used here.  Merely citing physical local accessibility
does not discharge observation, finite-cost realization, safety collar, or
memory synchronization.
