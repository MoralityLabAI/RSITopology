# Risk-polytope access v0.40

This additive ASMP-9 successor turns the v0.39 alignment result into a general
finite object:

```text
decision-relative access sufficiency
  = upper risk-polytope containment.
```

It compiles exact deficiencies for every subset of a finite rational query
registry, reports the inclusion-minimal access antichain at every critical
tolerance, and checks the deterministic zero-one special case against
Minimum Test Cover.

Current state: `registered_confirmation_passed`.

The canonical outcome is [RESULT_v0_40.md](RESULT_v0_40.md). All ten gates
passed on 64 exact access rows plus three solver spot checks. The independent
verifier reproduced the full result and revalidated all fourteen sealed
inputs.
