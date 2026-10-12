# ASMP-9 v0.30 development note

## Burned fixtures

Development used:

- a three-state, two-feature, horizon-three deterministic MDP;
- three consequence levels `(-2,0,3)`;
- separate horizon, action-set, transition, and feature perturbations;
- three-by-three calibrated, unknown-scale, and interaction value tables;
- one incomplete table;
- a sharp approximate residual at `epsilon=2/11`;
- a four-by-five exact constraint-rank check;
- two unknown-coefficient rescalings; and
- a joint v0.28 eligibility check.

Those exact fixtures are burned.

## Fresh-run separation

Any prospective protocol must change the MDP, feature dimension, horizon,
consequence levels, value tables, approximation radius, constraint-table
dimensions, unknown coefficient, and rescaling factors.

No fresh structural classification, semantic classification, constraint rank,
offset-bias maximum, population law, or combined eligibility verdict has been
generated.

## Scientific role

The run will validate an exact finite implementation of classical
decomposition and separability facts. It cannot establish the semantic value
of a real consequence or resolve ASMP-9.
