# ASMP-9 bond-design successor v0.18

This additive successor asks whether the minimal bad boundary supports from
v0.17 admit an exact graph-theoretic characterization.

The candidate answer is:

> The inclusion-minimal boundary supports that destroy full conditional-fiber
> quotient rank are exactly the bonds of the graph obtained by deleting the
> original bridges, component by component.

If correct, this replaces an exponential ternary-status definition by a
classical cut object. The resulting asymptotic allocation problem is the
classical design problem of distributing a unit edge budget to maximize the
minimum cut of each cyclic-core component. The intended ASMP-9 contribution is
the reduction from conditional reward-gauge access to that object, not a
novelty claim for max-min cut design.

Current status: **development theorem and independent finite checks, not yet
registered and not claim-eligible**.

Files:

- `FORMULATION_DRAFT_v0_18.md`: candidate theorem and proof.
- `PRIOR_ART_GATE_v0_18.md`: attribution and novelty boundary.
- `DEVELOPMENT_NOTE_v0_18.md`: burned checks and the pre-freeze registry
  correction.
- `bond_design.py`: independent bond and cactus utilities.
- `development_check.py`: burned development comparisons against v0.17.
- `test_bond_design.py`: deterministic unit tests.

The sealed v0.17 directory is not modified.
