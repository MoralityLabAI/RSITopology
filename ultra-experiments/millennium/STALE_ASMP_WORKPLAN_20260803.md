# Stale ASMP work plan - 2026-08-03

Closeout status: **complete**.

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
| ASMP-3 | 2026-08-03 (`822bc85`) | recent; no assignment |
| ASMP-4 | 2026-08-03 (`41cc46f`) | recent; stopped under its own certificate |
| ASMP-5 | 2026-08-03 (`61a2f80`) | complete: inductive rooted safety/liveness certificate |
| ASMP-6 | 2026-08-03 (`fe1f381`) | complete: balanced-cover parity frontier |
| ASMP-7 | 2026-08-03 (`d3b6187`) | complete: meter-coverage robustness |
| ASMP-8 | 2026-08-03 (`29a3fde`) | complete: adaptive deterministic-audit reuse |
| ASMP-9 | 2026-08-01 (`e612e51`) | recent; no assignment |
| ASMP-10 | 2026-08-03 (`46f4df8`) | complete: norm-bounded prefix obstruction |
| ASMP-11 | 2026-08-03 (`7d509e6`) | complete: hardened intermediate-width crossover bundle |
| ASMP-12 | 2026-08-03 (`db7939d`) | complete: explicit constructible survival object |

ASMP-5A is also inactive over the window, but remains a subproblem of ASMP-5
and is lower priority than the seven top-level areas above.

## Completed successor packages

| Area | Package | Bounded outcome |
|---|---|---|
| ASMP-5 | `asmp5_verifier_drift/v0_3_inductive_root` | Exact transition-derived induction establishes all-depth rooted safety plus a repeatable safe two-cycle in the frozen checker grammar. |
| ASMP-6 | `asmp6_semantic_collusion_frontier/v0_2_balanced_cover` | For two equiprobable messages under a uniform `m`-symbol averaged cover, perfect one-shot decoding occurs exactly for even `m`; odd `m` has Bayes error `1/(2m)`. |
| ASMP-7 | `asmp7_attestability_frontier/coverage_robustness_v0_3` | The 96-cell exact grid shows selective suppression weakens or destroys attestability relative to policy-independent missingness; no deployment claim is made. |
| ASMP-8 | `asmp8_goodhart_frontier_census/v0_6_adaptive_reuse` | The movement-weighted pointwise certificate stays sound over 1,399,680 cells and 729 adaptive traces; the matched plug-in selector yields false declarations. |
| ASMP-10 | `asmp10_capability_transition/prefix_obstruction/bounded_analytic_v0_2` | Exact Hermite-kernel and L1/L-infinity dual arguments establish the frozen, source-defined bounded-polynomial envelope only; this is not a learned-system or full ASMP-10 result. |
| ASMP-11 | `asmp11_access_ladder/covering_frontier_v0_2_1` release `v0.2.1.2` | The registered transparent-parity grid establishes a finite intermediate-width crossover surface over 48 covering cells, 144 cost cells, and 18 brackets; RAM compliance remains explicitly unmeasured. |
| ASMP-12 | `asmp12_program_equilibrium/v0_3_constructible_survival` release `v0.3.1` | Builds the exact finite survival correspondence for the registered three-program source-table universe; it is not a mixed-strategy, unrestricted-program, or homology claim. |

## Cross-critique disposition

Every package received an independent review. Where a review found defects,
the owner answered them in new commits; reviewed commits were not amended.

| Area | Adversarial finding | Disposition |
|---|---|---|
| ASMP-5 | The first theorem gate was hard-coded and the independent checker domain leaked. | `61a2f80` derives closure from the actual transition table, binds all checker/behavior/root domains, replays coordinate permutations, and rejects an allow-all mutation. |
| ASMP-6 | The verifier covered artifacts only through `m=9`, while equal-prior/uniform semantics and conclusions were insufficiently bound. | `7575721` and `fe1f381` replay all `m=2..31` cells, the continuous small cases and dual through `m=63`, and bind source, protocol, artifacts, and conclusions. |
| ASMP-7 | Semantic-layer and gate mutations could survive, and the fixed-mask scope was ambiguous. | `91c9f47` and `d3b6187` enforce the exact protocol and complete payload, all-cell cross-model gates, exact bundle binding, and the declared fixed-mask boundary. |
| ASMP-8 | Universal summaries, adaptive counts, and gates could be forged without full replay. | `78ac61e` and `29a3fde` independently replay every pointwise cell and adaptive trace, including witnesses, digests, probes, gates, and conclusion layers. |
| ASMP-10 | The reviewer found no actionable mathematical or evidence defect after exact primal/dual and scope checks. | The substantive `46f4df8` package was retained; `b325739` only normalized trailing blank lines. |
| ASMP-11 | Reviews found vacuous registration maps, count-only grids, weak operation/resource evidence, identity-probe inflation, and no authoritative synthesis. | The linear chain `1b1bcd8` -> `2fcc764` -> `3de336a` -> `facacbb` -> `7d509e6` freezes exact sources, registers first, commits primary evidence, independently replays it, then fresh-replays verification inside a five-layer synthesis. |
| ASMP-12 | Counts-only verification accepted duplicate catalogs, missing/duplicate adjacencies, forged events, and relabeled relations. | `5f62f33`, `fc7310a`, and `db7939d` enforce the exact machine manifest, ordered 512-entry catalog, complete relations/events, source checkpoint, and evidence root. |

## Final validation

The finalized packages were tested in separate Python processes because this
repository intentionally has repeated flat module names such as `run.py` and
`verify_independent.py`; collecting all packages into one interpreter causes
module-cache collisions and is not a valid regression mode.

| Area | Focused tests |
|---|---:|
| ASMP-5 | 12 passed |
| ASMP-6 | 24 passed |
| ASMP-7 | 10 passed |
| ASMP-8 | 15 passed |
| ASMP-10 | 8 passed |
| ASMP-11 | 27 passed |
| ASMP-12 | 10 passed |
| **Total** | **106 passed** |

ASMP-11 additionally passed B0-B7, independent V0-V12, a second fresh replay
inside synthesis, exact source/blob/hash closure, and a read-only post-run
audit of the committed 11-file artifact set. Its earlier v0.2.1.1 bundle is
byte-unchanged. The superseded untracked `RESULT_v0_2_1.md` and
`artifacts_v0_2_1/` remain excluded from every commit.

## Review and claim discipline

Every new package must keep these conclusions distinct:

1. metric robustness under frozen invariance, sensitivity, monotonicity,
   anti-gaming, and clean-control probes;
2. the exact finite task result;
3. measurement or certificate reliability;
4. support for the declared bounded claim; and
5. the operational decision to continue, repair, stop, or escalate.

The critique ring and follow-on adversarial reviews targeted committed hashes.
Repairs were promoted only after independent replay or a clean reviewer
verdict. The finite results above do not resolve their parent ASMPs unless a
package states that narrower claim explicitly.

## Repository discipline

Agents own disjoint new directories.  Shared summaries remain coordinator-
owned.  Staging and commits are serialized and name explicit paths; broad
staging commands are prohibited.  The pre-existing untracked `work/` directory
contains ASMP-4/9 artifacts and is outside this plan.
