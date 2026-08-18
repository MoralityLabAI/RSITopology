# Reviewer packet v0.13

## Claim to attack

For the stated bounded-authority plant and positive-volume collar, the exact full-collar computed and forced-raw regions are respectively `[2,infinity) x [2,infinity)` and `[3,infinity) x [2,infinity)`. For initial normal radius `rho`, the exact finite-horizon normal count is `ceil(rho*2^T)`.

## Short proof map

1. `q` has two control-relevant fibers but four raw labels.
2. Normal expansion by 2 makes one fixed word cover initial diameter at most `2/2^T`.
3. A dyadic branch policy attains the full-collar bound.
4. Equal-cell centering attains `ceil(rho*2^T)` for arbitrary positive `rho`.
5. Separation 8 between `q` fibers makes their write languages disjoint.
6. The raw registry is forced to retain the two labels inside each `q` fiber.

## Executable evidence

- `positive_volume_collar.py`: central exact construction, converse bookkeeping, mutations, seals, and frozen claim.
- `verify_positive_volume_collar.py`: import-independent geometry, enumeration, interval covers, converses, claim audit, and document audit.
- `test_positive_volume_collar.py`: 10 focused gates.

## High-value attacks

- Find a single control word that safely covers more than `2/2^T` initial normal length.
- Find a collision between two different `q`-fiber words despite separation 8.
- Exhibit a `rho,T` where fewer than `ceil(rho*2^T)` cells suffice or where the centering construction exits the collar.
- Show that the authority interval fails for a centering or branch control.
- Challenge the exact timing/registry convention rather than silently substituting another one.

## Deliberate nonclaims

The package does not establish perturbation/noise robustness. It does not select a canonical sensor registry for the underspecified ASMP-4 statement. It does not supply the full variational classification. External expert review is absent.

Those limitations are now the proper stopping boundary: the earlier zero-dimensional and zero-volume objections no longer apply to this registered example.
