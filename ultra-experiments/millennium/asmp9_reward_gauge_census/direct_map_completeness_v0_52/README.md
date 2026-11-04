# ASMP-9 direct-map completeness v0.52

This package tests the deterministic direct-map seam left by v0.51.

The candidate theorem is a classical Buehler-optimality corollary: sort any
valid direct upper confidence map by its own reported values, refine ties
arbitrarily, and its induced Buehler map is pointwise no larger. Consequently,
optimizing over every total outcome ordering is complete among deterministic
direct maps for every coordinatewise increasing objective.

Start with:

- `PRIOR_ART_GATE_v0_52.md`;
- `THEOREM_DRAFT_v0_52.md`;
- `direct_map_completeness.py`; and
- `test_direct_map_completeness.py`; and
- `DEVELOPMENT_RESULT_v0_52.md`.

Aggregate randomized coverage is deliberately excluded.
