# ASMP bounded round-robin workshop v0.1

## Purpose

This packet uses one proposer per ASMP candidate and exactly one independent
neighboring review per proposal. It is a scoped ULTRA exercise, not a theorem
claim, preregistration, or authorization to launch capability-enhancing work.

Each proposal is limited to one smallest decisive experiment and one optional
scale-up. Every experiment must name the mathematical estimand, falsifier,
controls, evidence class, and resource ceiling. Simulation may test an
instrument or conjecture on a bounded class; it cannot resolve an ASMP by
itself.

## Round-robin map

| Proposal | Reviewer |
|---|---|
| ASMP-1 | ASMP-7 proposer |
| ASMP-2 | ASMP-1 proposer |
| ASMP-3 | ASMP-2 proposer |
| ASMP-4 | ASMP-3 proposer |
| ASMP-5 | ASMP-4 proposer |
| ASMP-6 | ASMP-5 proposer |
| ASMP-7 | ASMP-6 proposer |

No proposal receives more than one workshop review. The consolidated report
may resolve formatting or accounting inconsistencies but may not silently
repair a mathematical objection.

## Required proposal fields

1. Narrow subproblem and why it advances the canonical ASMP.
2. Mathematical object and frozen hypothesis.
3. Smallest decisive experiment, controls, and kill criteria.
4. Evidence class: exact/certified, exhaustive-discretized, synthetic
   empirical, or real-model empirical.
5. Pilot and full resource estimates: wall time, CPU cores, RAM, disk, GPU
   model/VRAM and GPU-hours if any.
6. Named repository consumer and reusable artifact.
7. Claim boundary and one reason not to run it.

## Outputs

- `ASMP-1_PROPOSAL.md` through `ASMP-7_PROPOSAL.md`
- `ASMP-1_REVIEW.md` through `ASMP-7_REVIEW.md`
- `CONSOLIDATED_RESOURCE_REPORT.md`
