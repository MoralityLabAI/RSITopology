# Reviewer packet v0.26

## Claim under review

An exact costed alternating quotient preserves the full additive public-history
capacity region. Finite deterministic quotients can use v0.25; finite
abstraction is sufficient but not necessary.

## Fast checks

1. Check the representative-history strategy transfer in `THEOREM.md`.
2. Verify that action types, state safety, vector costs, and successor class
   sets are matched in both directions.
3. Run `python run_verification.py` and require all ten gates.
4. Run `python verify_public_bisimulation_transfer.py`; it uses independent
   partition signatures, recursive Thue-Morse generation, and scalar Bellman
   values.
5. Run `python -m pytest -q test_public_bisimulation_transfer.py` and require
   ten passing focused tests.

## Falsification targets

- Produce a quotient play that cannot be represented by the back condition.
- Change a cost or state-safety bit without breaking the checker.
- Find a decorated-cover frontier that differs from its base quotient.
- Give a finite stationary unary quotient generating all Thue-Morse costs.
- Locate a claim applying v0.25 directly to nondeterministic quotient actions.
