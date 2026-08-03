# ASMP-5 inductive rooted-verifier result v0.3

## Verdict

`all_depth_rooted_safety_with_arbitrary_time_liveness`

The depth-eight positive control from v0.2 is now replaced by an induction for
the exact same four-bit checker grammar.  The import-independent verifier
replayed 45 registered graph cells with zero mismatches and reproduced the
safe liveness cycle.

## Task result

The root checker is binary `0011`: it accepts both proof classes for a safe
next behavior and neither proof class for a hazardous next behavior.  Under
`root_refinement`, every accepted transition requires the proposed next
checker to be an acceptance-set subset of that root.

The all-depth argument is therefore:

1. the installed checker initially equals the root;
2. every accepted successor checker is a subset of the root; and
3. every root subset rejects both proof classes when the next behavior has its
   hazard bit set.

Thus no accepted finite path reaches a hazardous behavior, at any checker
mutation radius.  For every behavior width at least two, retaining the root
checker and alternating coordinate one gives a certified safe two-cycle.
Repeating that cycle supplies arbitrary execution time, so the safety result
is not obtained by deadlock.  It does not supply infinitely many distinct
states.

The matched unrooted rules remain separated.  At any width at least two and
radius at least one, a safe first step installs checker `0111`; a second step
then flips the hazard coordinate, which that checker accepts.  Both
`self_endorsement` and `pairwise_agreement` therefore reach unsafety at exactly
depth two.  Radius zero is the clean no-drift control.

## Metric robustness

All five frozen probe families passed:

- adding or permuting nonhazard coordinates preserves the verdict;
- granting the root one hazard-acceptance bit creates a depth-one failure;
- the rooted induction is invariant to horizon extension and checker radius;
- the matched unrooted failure remains live; and
- the rooted safe two-cycle rules out a deadlock-only certificate.

## Measurement reliability

The theorem compiler produced 45 cells over widths `{2,3,4,6,8}`, radii
`{0,1,2}`, and three rules.  A standalone verifier that does not import the
compiler explicitly enumerated the reachable graph through horizon six.  It
found zero symbolic/replay mismatches, zero rooted subset-invariant failures,
and replayed the liveness cycle.

## Claim support and operation

The evidence supports an all-depth safety and arbitrary-time liveness claim
only for the frozen transparent grammar.  The operational decision is to stop
spending compute on deeper enumeration of this toy rooted positive control.
The next informative ASMP-5 work must allow root replacement, checker-learning
error, or a richer progress requirement.

This does not establish open-ended reflective safety, safety of learned
verifiers, infinite distinct-state progress, or a resolution of ASMP-5.

## Artifact integrity

| Artifact | SHA-256 |
|---|---|
| `artifacts_v0_3/result_v0_3.json` | `d916dc8b1fb74e2ecdc192607a7350782800b746c18e591458c203b8b94cd361` |
| `artifacts_v0_3/verification_v0_3.json` | `4ba1bd9161efadde6e83aa6d6e74f5c75537a0511816b5368ef413bcf2a9e1c7` |

Dedicated tests: `6 passed`.
