# ASMP-2 active-design census v0.2.1

Version 0.2 exceeded its frozen wall-time cap before emitting an outcome. This additive amendment changes only the exhaustive projector implementation.

- The runner obtains each subset projector from the subset with its least-significant selected environment removed.
- The verifier independently obtains it from the subset with its most-significant selected environment removed.
- Both must produce the same complete quantized census digest.
- The parent universe, score definition, selectors, seeds, thresholds, tie contract, and claim boundary are byte-bound to protocol v0.2.

No v0.2 file is modified.

