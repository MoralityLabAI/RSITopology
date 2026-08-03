# ASMP-5 rooted-verifier induction protocol v0.3

## Frozen object

- behavior is a width-`w` bit vector with hazard coordinate zero;
- a checker is a four-bit acceptance table indexed by
  `(hazard, proof_class)`;
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
theorem compiler; it is not the basis of the all-depth induction.

## Robustness probes

- invariance: permuting nonhazard behavior coordinates preserves the verdict;
- sensitivity: granting the root one hazard acceptance bit produces a
  depth-one unsafe transition;
- monotonicity: the rooted invariant is closed under arbitrary horizon
  extension;
- anti-gaming: the unrooted two-step witness is live rather than suppressed;
- clean control: the rooted system has an explicit safe two-cycle and is not
  certified by deadlock.

## Conclusion layers

- **Task result:** the four theorem targets for the frozen grammar.
- **Measurement reliability:** agreement with an import-independent finite
  graph replay on the registered grid.
- **Claim support:** an all-depth certificate for one exact rooted rule.
- **Operational decision:** retire deeper brute-force expansion of this toy
  positive control and move to replaceable-root or learned-checker robustness.

## Claim boundary

This package does not establish infinite distinct-state progress, safety of a
replaceable root, robustness to checker-learning error, or any resolution of
ASMP-5.  The nonrooted witness is a transparent regression fixture, not a
claim that all self-modifying systems fail in two steps.
