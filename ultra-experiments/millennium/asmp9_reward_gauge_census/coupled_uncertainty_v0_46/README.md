# ASMP-9 v0.46: coupled shared-channel uncertainty

Version v0.45 optimized a confidence-valid rectangular relaxation of an
adaptive risk polytope. Version v0.46 asks the next resolution-directed
question: what changes when one uncertain channel parameter must move every
policy risk jointly?

The experiment keeps the v0.45 four-target, three-query, horizon-two decision
tree and replaces independent generator perturbations by the exact image of
three shared binary-symmetric flip rates. It:

- derives the exact likelihood region after zero observed calibration errors;
- uses Blackwell ordering to place the worst channel at the upper corner;
- compiles all horizon-two adaptive policy risks as degree-two polynomials;
- solves the four-target minimax game with exact rational certificates;
- compares the coupled endpoint with the inherited rectangular relaxation;
- repeats the integer allocation census on a disjoint total budget; and
- includes a product-family control where rectangular uncertainty is exact.

The `N=60` coupled calculation was used during development and is burned.
The claim-eligible confirmation uses `N=66` only after the protocol,
implementation, tests, prior-art boundary, environment, runner, and verifier
are committed and hash-registered.

This remains a finite synthetic decision experiment. It is not a general
nonrectangular robust-control theorem, a real preference-channel validation,
or a resolution of ASMP-9.

