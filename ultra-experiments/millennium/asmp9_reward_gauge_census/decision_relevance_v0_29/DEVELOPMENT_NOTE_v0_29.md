# ASMP-9 v0.29 development note

## Burned fixtures

Development used:

- three fixed-horizon three-feature occupancies with a constant gauge;
- a varying-horizon invalid-gauge control;
- one three-coordinate gauge projection;
- a two-policy sharpness witness at magnitude `3/7`;
- one strict-margin three-policy cell;
- one fixed-regret scale fork with scales `1/4` and `3`; and
- one dependent-gauge rejection.

Those exact cells are burned.

## Fresh-run separation

The prospective protocol changes reward magnitudes, horizons, scale factors,
policy counts, threshold, and sharpness magnitude. It adds a separate
measurement-to-decision composition cell.

No fresh gate output, selected policy, regret, quotient distance, margin
certificate, or scale-threshold classification was generated before
registration.

## Scientific role

The run checks an exact finite implementation of classical inequalities. It
does not establish that learned reward error is small, that reward regret is a
complete safety metric, or that ASMP-9 is resolved.
