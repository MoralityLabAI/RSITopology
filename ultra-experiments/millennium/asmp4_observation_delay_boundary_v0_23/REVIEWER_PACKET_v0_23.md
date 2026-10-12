# Reviewer packet v0.23

## Claim under review

The current mode must be available before the current safety write. For the
registered collar, the threshold is sharp: delay zero is feasible, every
positive integer delay is impossible for arbitrary modes, charged preview
restores feasibility, and a pre-safety constant-mode seed reduces the corner.

## Fast checks

1. Verify the affine safe intervals and their constant gap of six in
   `THEOREM.md`.
2. Run `python run_verification.py` and require all ten gates.
3. Run `python verify_observation_delay_boundary.py`; it does not import the
   central module and uses a larger branch enumeration.
4. Run `python -m pytest -q test_observation_delay_boundary.py` and require ten
   passing focused tests.
5. Check both sealed SHA-256 resources and the exact JSON contract/claim.

## Falsification targets

- Exhibit a single control safe for both `q_t=0` and `q_t=8` at a common
  collar point.
- Produce a positive-delay policy whose first write depends on the unseen
  current mode without adding a charged preview channel.
- Break the preview witness `u=q-2n` within the registered authority bounds.
- Beat rate one in the constant-mode seeded case while covering the expanding
  normal direction.
- Find a hidden calibration, predictability, randomness, or timing assumption
  not represented in the frozen contract.
