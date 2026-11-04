# ASMP-3 resource-scope harness stop certificate v2.17

## Decision

Stop extending the current unique-marker resource grids after v2.16.  Resume
only after a new formal task/protocol class or a concrete non-marker family is
registered.

## Exhausted marker lanes

| Lane | Exact evidence | Further grid rows? |
| --- | --- | --- |
| Honest black-box Find | `N` exact queries; randomized value `q_find/N` | no claim change |
| One-message Check | `Kq>=N` and exact bit frontier | subsumed |
| Arbitrary rounds | transcript compression; exact `min(1,Kq/N)` | no claim change |
| Adaptive queries | 97,062 trees; symbolic all-zero-path lemma | no claim change |
| Public-coin bounded soundness | exact `s+(1-s)min(1,Kq/N)` | no claim change |
| Finite public seeds | exact balancing floor; 25,523 exhaustive families | no claim change |
| Target gap | exact integer transcript threshold | no claim change |

Each formula is symbolic in `N`, `K`, `q`, and where applicable `s`.  More
values can test implementations but cannot enlarge the quantifiers.

## Why the cross-task continuation is not currently a theorem statement

The canonical v0.1 document asks the solver to *provide* a formal complexity
class.  It does not already supply the reductions, advice model, structural
side-information rules, cross-task encoding invariants, or uniform resource
measure needed to state a universal matching lower bound.

These choices alter the truth of a resource theorem.  For example, structured
side information can collapse marker search; a stronger semantic macro can
collapse query cost; and an unrestricted encoding can hide a full solution in
one atom.  V2.0 proves why those are class/interface choices, not harmless
presentation details.

A local harness cannot choose among them without creating a nonnormative
successor.  Therefore the missing cross-task result is definition-dependent,
not evidence that the existing finite grid is too small.

## Legitimate resume events

Resume for any of:

1. a frozen cross-task class with reduction and resource invariance rules;
2. a concrete structured non-marker task family whose theorem is not implied by
   the marker frontier;
3. an authoritative normative interface adoption;
4. a new task-specific non-black-box structure theorem; or
5. attributable external reproduction.

Absent one of these events, stopping the marker grid is mathematically
justified.  This certificate does not claim unrestricted ASMP-3 is solved.
