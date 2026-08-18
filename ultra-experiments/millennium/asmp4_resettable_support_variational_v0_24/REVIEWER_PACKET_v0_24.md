# Reviewer packet v0.24

## Claim under review

Safe reset blocks define normalized two-port rate points. Their concatenations
generate the closed upward convex hull, and the lower support family
`h(lambda)` reconstructs that whole region exactly.

## Fast checks

1. Check that transcript counts multiply under the registered reset rule.
2. Check the separating-hyperplane proof uses only nonnegative normals because
   the budget region is upward.
3. Run `python run_verification.py` and require all ten gates.
4. Run `python verify_resettable_support_variational.py`; it independently
   builds finite hulls and exhausts 1,022 schedule words.
5. Run `python -m pytest -q test_resettable_support_variational.py` and require
   ten passing focused tests.

## Falsification targets

- Find a reset-concatenable count pair whose composition is not bounded by
  coordinatewise multiplication.
- Exhibit an outside point that satisfies every nonnegative support inequality.
- Show that `h` is not concave for a finite block-rate set.
- Make the v0.7 false corner satisfy the critical `log2(3/2)` inequality.
- Identify a claim that promotes the block region to the full region without
  the separately stated periodic block completeness condition.
