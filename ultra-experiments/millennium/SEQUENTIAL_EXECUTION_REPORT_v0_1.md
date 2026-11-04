# ASMP sequential execution report v0.1

Date: 2026-07-19  
Branch: `feat/spectral-bundle-v0.3-bifiltration`

## Frozen order and terminal result

The registered sequence was executed once. Duplicate objective text in the harness was treated as transport noise, not a request for a second execution.

| Stage | Registration commit | Result commit | Decision | Next-stage effect |
|---|---|---|---|---|
| ASMP-2 crossed shift | `a22b177` | `7f02854` | pass | opened ASMP-4 |
| ASMP-4 two-port game | `04c44f5` | `5dbb700` | pass | opened ASMP-5 |
| ASMP-5 verifier drift | `ba4ba49` | `b006f3d` | unavailable: resource cap | stopped sequence |
| ASMP-3 | — | — | not run | blocked by frozen order |
| ASMP-1 CPU preflight | — | — | not run | blocked by frozen order |
| ASMP-1 GPU confirmation | — | — | not authorized | CPU preflight never opened |
| ASMP-6 / ASMP-7 | — | — | deferred | formal repairs still required |

## ASMP-2

All registered runner gates and all 20 independent verification checks passed. The result is an analytically forced exact finite construction (`instrument_valid_forced_construction`), not a general theorem.

## ASMP-4

All 108 registered finite-game cells were evaluated using exact rational arithmetic. All feasible witnesses replayed over the complete initial collar and disturbance tree; sensor-symbol relabeling preserved feasibility. At the load-bearing cell `(T=2, c=1/2, a_z=3/2)`, `(r,w)=(2,2)` was feasible while `(0,2)`, `(2,0)`, and `(0,0)` were infeasible. Twenty independent checks reproduced the phase map. The evidence class is `exact_registered_architecture_phase_map`, not an asymptotic data-rate theorem.

## ASMP-5

The sealed exact census exceeded its 180-second wall ceiling. The wrapper timed out after 184.1 seconds; the surviving matching process was terminated, no scientific result or partial registered receipt had been emitted, and no partial outcome was read. The deterministic status is `unavailable_resource_cap_stop_sequence`. This provides no evidence for or against verifier-drift separation.

## Audit notes

- The tracked worktree was clean after the terminal result commit.
- Independent ASMP-2 and ASMP-4 verification artifacts replayed successfully.
- Structural suites pass under their registered separate invocations: ASMP-2 7/7, ASMP-4 7/7, ASMP-5 8/8.
- A combined one-process pytest collection is not supported because the three standalone directories each expose a top-level module named `run`; Python module caching causes cross-directory import collisions. No sealed file was changed after discovering this packaging limitation.
- The branch was six commits ahead of its remote before this report commit.

## Required next decision

Do not resume at ASMP-3. A continuation requires a versioned ASMP-5 successor protocol with a justified exact-search optimization or a larger explicit resource ceiling, committed before another outcome is generated.
