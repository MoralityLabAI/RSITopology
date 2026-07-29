# ASMP-9 general incomplete-menu theorem v0.56

Status: **prospectively verified candidate theorem**.

This successor asks whether the three-alternative v0.55 access trichotomy is
an accident of the denominator-six census.  The candidate theorem says it is
not: for every finite alternative universe of size at least three, unrestricted
positive completion of even one unqueried non-singleton menu prevents a
proper-domain dataset from certifying the full kernel as Luce or random
utility.

The proof has two parts:

1. a missing menu permits an explicit regularity-violating completion; and
2. the random-utility completion fiber through a positive Luce point has
   strictly larger dimension than the Luce completion fiber.

The development code checks affine ranks for `n = 3, 4, 5` and exhausts every
proper menu domain for `n = 3, 4`.  A separately frozen verifier adds a held-
out `n=6` affine-rank certificate, component-partition checks, constructive
witnesses, and the sharp `n=2` negative boundary.  Computation supports but
does not replace the arbitrary-`n` proof.

See:

- [RESULT_v0_56.md](RESULT_v0_56.md)
- [THEOREM_DRAFT_v0_56.md](THEOREM_DRAFT_v0_56.md)
- [PRIOR_ART_GATE_v0_56.md](PRIOR_ART_GATE_v0_56.md)
