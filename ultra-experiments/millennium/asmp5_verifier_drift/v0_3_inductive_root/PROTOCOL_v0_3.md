# ASMP-5 rooted-verifier induction protocol v0.3

## Frozen object

- behavior is an integer in `0..2^w-1` interpreted as a width-`w` bit vector,
  with bit zero designated as the hazard coordinate;
- a checker is a four-bit acceptance table indexed by
  `(hazard, proof_class)`;
- checker values are integers in the closed domain `0..15`; values with a
  negative sign or any higher bit are outside the grammar and are rejected;
- the root checker is binary `0011`, accepting both proof classes exactly when
  the proposed behavior is nonhazardous;
- one step flips one behavior bit and changes the installed checker within a
  declared Hamming radius; and
- the rooted rule accepts only when the active checker accepts and the next
  checker is an acceptance-set subset of the root.

## Theorem targets

1. Every checker reachable under the adaptive rooted rule is a subset of the
   root checker.
2. Every behavior reachable under that rule is nonhazardous at every finite
   depth.
3. At width at least two, retaining the root checker while alternating one
   nonhazard coordinate gives an arbitrarily long certified safe execution.
4. At width at least two and checker radius at least one, both unrooted rules
   admit an unsafe behavior at exactly depth two.

## Independent replay grid

The standalone verifier exhausts widths `{2,3,4,6,8}`, radii `{0,1,2}`, all
three certificate rules, and horizons through six.  The grid checks the
theorem compiler; it is not the basis of the all-depth induction.  The
all-depth basis is a separate exhaustive one-step closure over the width-two
safe/hazard templates, all 16 current and successor checker values, and radii
`{0,1,2,3,4}`.  Those radii cover every distinct Hamming-distance regime in a
four-bit checker grammar.  The primary compiler hashes all 10,240 rows of that
rooted transition truth table, and the standalone verifier independently
reconstructs both the closure and its digest.

## Robustness probes

- invariance: permuting nonhazard behavior coordinates preserves the verdict;
- sensitivity: granting the root one hazard acceptance bit produces a
  depth-one unsafe transition;
- monotonicity: the rooted invariant is closed under arbitrary horizon
  extension in every distinct four-bit checker-radius regime;
- anti-gaming: the unrooted two-step witness is live rather than suppressed;
- clean control: the rooted system has an explicit safe two-cycle and is not
  certified by deadlock.

## Conclusion layers

- **Task result:** the four theorem targets for the frozen grammar.
- **Measurement reliability:** agreement with an import-independent finite
  graph replay, one-step closure, and transition-relation digest.
- **Claim support:** an all-depth certificate for one exact rooted rule.
- **Operational decision:** retire deeper brute-force expansion of this toy
  positive control and move to replaceable-root or learned-checker robustness.

The final synthesis receipt binds the protocol, primary result, and independent
verification, plus the primary and verifier source files, by SHA-256. Its five
conclusion layers are the authoritative combined verdict; the primary result
alone remains pending independent replay.

## Claim boundary

This package does not establish infinite distinct-state progress, safety of a
replaceable root, robustness to checker-learning error, or any resolution of
ASMP-5.  The nonrooted witness is a transparent regression fixture, not a
claim that all self-modifying systems fail in two steps.
