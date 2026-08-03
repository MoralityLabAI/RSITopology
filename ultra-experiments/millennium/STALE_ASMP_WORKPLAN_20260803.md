# Stale ASMP work plan - 2026-08-03

## Scope

This is a coordination record, not a scientific result or a change to any
frozen ASMP statement.  "Stale" means that no substantive, path-bound commit
landed during the rolling seven-day window ending 2026-08-03.  The repository
had roughly 415 commits during that window, so a nine-to-fourteen-day gap is a
useful scheduling signal; it is not a statement about research importance.

## Activity audit

| Area | Last substantive work | Scheduling disposition |
|---|---|---|
| ASMP-1 | 2026-08-01 (`29761c2`) | recent; no assignment |
| ASMP-2 | 2026-08-01 (`acf209d`) | recent; no assignment |
| ASMP-3 | 2026-08-03 (`c6f4b4c`) | recent; no assignment |
| ASMP-4 | 2026-08-03 (`41cc46f`) | recent; stopped under its own certificate |
| ASMP-5 | 2026-07-21 (`34ce008`) | queued: inductive safety/liveness certificate |
| ASMP-6 | 2026-07-21 (`b6975ba`) | queued: multiletter covertness boundary |
| ASMP-7 | 2026-07-21 (`42cc417`) | active: meter-coverage robustness |
| ASMP-8 | 2026-07-25 (`410e10c`) | queued: adaptive deterministic audit reuse |
| ASMP-9 | 2026-08-01 (`e612e51`) | recent; no assignment |
| ASMP-10 | 2026-07-22 (`3d3c36a`) | active: norm-bounded prefix obstruction |
| ASMP-11 | 2026-07-21 (`9841880`) | active: intermediate-width crossover bounds |
| ASMP-12 | 2026-07-20 (`fd6117d`) | queued: explicit constructible survival object |

ASMP-5A is also inactive over the window, but remains a subproblem of ASMP-5
and is lower priority than the seven top-level areas above.

## Review and claim discipline

Every new package must keep these conclusions distinct:

1. metric robustness under frozen invariance, sensitivity, monotonicity,
   anti-gaming, and clean-control probes;
2. the exact finite task result;
3. measurement or certificate reliability;
4. support for the declared bounded claim; and
5. the operational decision to continue, repair, stop, or escalate.

The first-wave critique ring is ASMP-10 reviewing ASMP-11, ASMP-11 reviewing
ASMP-7, and ASMP-7 reviewing ASMP-10.  Reviews target committed hashes.  An
owner responds in a new commit rather than amending the reviewed checkpoint.

## Repository discipline

Agents own disjoint new directories.  Shared summaries remain coordinator-
owned.  Staging and commits are serialized and name explicit paths; broad
staging commands are prohibited.  The pre-existing untracked `work/` directory
contains ASMP-4/9 artifacts and is outside this plan.
