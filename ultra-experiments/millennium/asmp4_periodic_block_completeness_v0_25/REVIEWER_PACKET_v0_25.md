# Reviewer packet v0.25

## Claim under review

Finite public additive schedulers have a union-of-cycle-polytopes capacity
region. Periodic completeness holds within each reachable cyclic SCC, while
irreversible SCC forks remain disjunctive.

## Fast checks

1. Verify the eventual-SCC and cycle-decomposition proof in `THEOREM.md`.
2. Run `python run_verification.py` and require all ten gates.
3. Run `python verify_periodic_block_completeness.py`; it uses mutual
   reachability and exhaustive edge products rather than central Tarjan/DFS.
4. Run `python -m pytest -q test_periodic_block_completeness.py` and require ten
   passing focused tests.
5. Confirm `(2,2)` is accepted by the convexified fork supports but belongs to
   neither true component quadrant.
6. Read `PRIOR_ART_BOUNDARY_v0_25.md` before assessing novelty.

## Falsification targets

- Give an infinite finite-graph walk that changes SCC infinitely often.
- Find a closed-walk mean outside the convex hull of its simple-cycle means.
- Prevent periodic approximation inside a strongly connected finite graph
  while retaining bounded additive connectors.
- Place `(2,2)` inside either irreversible-fork component quadrant.
- Locate an implicit claim that every nonlinear registration has finite public
  additive scheduler state.
