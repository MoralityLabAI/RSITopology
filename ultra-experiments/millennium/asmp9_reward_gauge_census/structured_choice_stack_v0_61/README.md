# ASMP-9 structured-choice stack v0.61

This directory prospectively verifies the conditional theorem stack developed
in versions v0.57 through v0.60:

1. bounded contextual log-odds degree and nested-menu access;
2. margin-promised finite-sample tier certification;
3. fixed Huber contamination;
4. recorded pre-response menu selection and outcome-dependent recording.

The earlier development cells are burned.  Version v0.61 uses new universe
sizes, degrees, rational paths, simplex grids, sampling cells, and selection
bounds frozen in `verification_cells_v0_61.json`.

The verification is evidence for the finite implementations and the displayed
proof handoffs.  The arbitrary-size statements remain mathematical proofs,
not consequences of finite enumeration.  Passing does not establish that a
real demonstrator satisfies bounded context degree, a separation promise,
fixed contamination, stable conditional response, or any of the registered
selection models.  It does not resolve ASMP-9.

The intended chronology is:

1. commit the protocol, proof audit, cells, verifier sources, and registration
   writer;
2. run `register_verification_v0_61.py` and commit the write-once registration;
3. only then run `verify_stack_v0_61.py`;
4. publish the write-once result and release receipt in a later commit.

