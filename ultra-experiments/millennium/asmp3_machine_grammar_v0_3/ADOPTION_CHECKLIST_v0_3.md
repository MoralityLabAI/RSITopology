# ASMP-3-MACHINE-v0.3 adoption checklist

An adopting authority or external reviewer should decide each item explicitly:

1. Accept canonical JSON rather than another byte codec.
2. Accept `WV-IR-v0.3` and its bit-cost gas model for all quantified protocol
   programs.
3. Accept `U_TM_v1` as the embedded standard machine numbering.
4. Accept the 23 component signatures and total FAULT behavior.
5. Accept rational history-conditional noise kernels as the complete noise
   representation.
6. Accept the declared prover/verifier information projections.
7. Select `FIX`, finite-catalog `ADM`, or retain both as separate decision sets.
8. Confirm that builtins are environment macros, not protocol privileges.
9. Confirm that the v2.21 compiler image is inside the unrestricted domain.
10. Reproduce the codec, parser, compiler hashes, reference IR receipts, and
    NONHALT/coupling proofs independently.

Changing items 2--9 creates a different problem version. Cosmetic
reimplementations preserving canonical bytes and semantics are benign.
