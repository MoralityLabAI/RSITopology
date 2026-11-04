# ASMP-7 boundary-degradation serialization amendment v0.2.1

## Scope

V0.2.1 repairs only the preregistered v0.2 receipt-serialization failure. It
does not change the mathematical model, grids, cap, exact test, descriptive
fit, gates, decision rule, or claim boundary in `PROTOCOL_v0_2.md`.

## Repair

Before importing the v0.2 runner, the successor wrapper calls
`sys.set_int_max_str_digits(0)` on Python versions that expose it. This permits
decimal serialization of trusted exact integer numerators and denominators
longer than CPython's default 4,300-digit conversion limit.

The relaxation applies only inside this bounded, local, non-networked exact
runner. No untrusted string is parsed as an integer. Exact fractions remain
decimal numerator/denominator strings, and every scientific decision remains
based on the same integer and `Fraction` arithmetic sealed in v0.2.

## Registration behavior

- V0.2 remains recorded as `unavailable_serialization_failure`.
- V0.2.1 uses a fresh registration and `artifacts_v0_2_1/` output directory.
- The v0.2 source, registration, and failure receipt are hash-bound inputs.
- Any further execution failure requires another versioned successor.

