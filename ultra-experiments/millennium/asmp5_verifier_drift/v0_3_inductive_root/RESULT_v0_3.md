# ASMP-5 inductive rooted-verifier result v0.3

## Verdict

`all_depth_rooted_safety_with_arbitrary_time_liveness`

The depth-eight positive control from v0.2 is now replaced by an induction for
the exact same four-bit checker grammar.  The primary compiler derived its
inductive step from the actual transition relation.  The import-independent
verifier replayed 45 registered graph cells with zero mismatches, reconstructed
the transition digest and one-step closure, and reproduced the safe liveness
cycle.  A final synthesis receipt binds all three evidence layers.

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

The compiler exhaustively checked the width-two safe/hazard templates, every
root-subset current checker, both behavior coordinates, all 16 successor
checkers, and every distinct radius regime `{0,1,2,3,4}`.  All 1,280 one-step
closure candidates preserved the invariant.  Width two is sufficient because
the transition rule distinguishes only the hazard coordinate, the proof class,
and whether the flipped coordinate is hazardous or nonhazardous.

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

- exhaustively permuting representative nonhazard coordinates preserves the
  actual transition relation;
- granting the root one hazard-acceptance bit creates a depth-one failure;
- the rooted induction is invariant to horizon extension and checker radius;
- the matched unrooted failure remains live; and
- the rooted safe two-cycle rules out a deadlock-only certificate.

## Measurement reliability

The theorem compiler produced 45 cells over widths `{2,3,4,6,8}`, radii
`{0,1,2}`, and three rules.  It also hashed a complete 10,240-row rooted
transition truth table over the width-two template and radii `{0,1,2,3,4}`;
1,088 rows were accepting.  A standalone verifier that does not import the
compiler explicitly enumerated the reachable graph through horizon six,
reconstructed the same truth-table digest, and independently checked all 1,280
inductive closure candidates.  It found zero symbolic/replay mismatches and
zero rooted subset-invariant failures.  Dedicated regression tests reject
negative and high-bit checker values and prove that an allow-all mutation of
the primary transition function fails both the primary gates and independent
digest comparison.

## Claim support and operation

The evidence supports an all-depth safety and arbitrary-time liveness claim
only for the frozen transparent grammar.  The operational decision is to stop
spending compute on deeper enumeration of this toy rooted positive control.
The next informative ASMP-5 work must allow root replacement, checker-learning
error, or a richer progress requirement.

The primary artifact deliberately reports independent replay as pending.  The
authoritative combined verdict is the synthesis receipt: it binds the protocol,
primary result, verification artifact, and executable source files by SHA-256
and records the final task result, measurement reliability, claim support,
operational decision, and metric-robustness layers.

This does not establish open-ended reflective safety, safety of learned
verifiers, infinite distinct-state progress, or a resolution of ASMP-5.

## Artifact integrity

| Artifact | SHA-256 |
|---|---|
| `artifacts_v0_3/result_v0_3.json` | `a3e96165b58027a98edf17ce5cd007e283ae65059af7ef8f9e36a471da028f8a` |
| `artifacts_v0_3/verification_v0_3.json` | `4a0b8a7bd9c06dd3c10ccadbbd03660ce4a4630254d7454f51d6f4cbbceb6d5e` |
| `artifacts_v0_3/synthesis_receipt_v0_3.json` | `11cb0b249a7688877e3d508cdd438d9e6ce67dd0f5bfe8943e9d8fee93655047` |

Dedicated tests: `12 passed`.
