# ULTRA-MATH Collaboration Protocol v0.1

## Purpose

The collaboration is adversarial by design. Agents exchange frozen artifacts,
not persuasive narratives. A claim has an immutable identifier and version;
changing its universe, quantifiers, hypotheses, metric, or conclusion creates a
new version and preserves the predecessor.

## Roles

- **Proposer:** states the claim, applications, examples, nonexamples, and
  expected falsifier. The proposer cannot award theorem status.
- **Prover:** independently restates the claim, exposes a dependency graph, and
  discharges proof obligations without widening the conclusion.
- **Challenger:** searches for quantifier errors, forced conclusions,
  counterexamples, numerical instability, coordinate dependence, and rival
  explanations. A successful objection includes a checkable kill certificate.
- **Referee:** reruns decisive checks and adjudicates frozen artifacts. The
  referee may accept, reject, narrow, or request a new version, but cannot
  silently repair a submitted claim.

Roles rotate between claims. The same agent may not both propose and referee a
claim version.

## Lifecycle

```text
seed -> formalized -> live/nontrivial -> proof_candidate|evidence_candidate
     -> under_attack -> refereed -> frozen
```

A failed liveness check terminates at `forced_or_vacuous`. Failure to find a
counterexample never upgrades a claim.

## Required claim packet

1. Formal and plain-language statements.
2. Universe, quantifier order, hypotheses, conclusion, norms, precision model,
   and exceptional cases.
3. Definitions and theorem-dependency ledger.
4. **Liveness certificate:** one admissible case where the conclusion holds
   and one where it fails. If failure is impossible under the hypotheses, the
   result is forced and cannot be reported as a discovery.
5. Proof obligations, including smallest dimension, zero/rank-deficient cases,
   boundaries, and symmetries.
6. Small examples and smallest known counterexamples.
7. Permitted conclusion and prohibited paraphrases.
8. For computation: exact domain or sampling frame, arithmetic, seeds,
   tolerances, code/data hashes, resource receipt, and an independent checker.

## Challenger checklist

The challenger audits these independently:

- typing, definitions, and quantifier order;
- liveness and hidden geometric forcing;
- degenerate, boundary, symmetry, and smallest-dimension cases;
- circular or incorrect dependencies;
- exact versus floating-point steps;
- coordinate, scale, and gauge dependence;
- claim wording versus the actual estimand;
- synthetic-to-real, local-to-global, and linear-to-nonlinear extrapolation;
- whether a baseline is held fixed strongly enough to isolate the proposed
  object; and
- whether the proposed bound is numerically nonvacuous on its target domain.

Findings are `fatal`, `scope_narrowing`, `repairable`, or `nonissue`. Numerical
kill certificates must verify the hypotheses and failed conclusion with exact
arithmetic, interval bounds, or a stated tolerance justified independently of
the observed effect.

## Referee decisions

The referee emits exactly one evidence label and an instrument status. It must
distinguish:

- an invalid instrument;
- an instrument-valid but inconclusive result;
- a refuted claim; and
- a result forced by construction.

Earlier component results survive a later component's provenance failure when
their instruments are independently sealed. A composite conclusion cannot pass
when any required component is invalid or unavailable.

## Hard claim boundaries

- A finite numerical search is not a universal proof unless coverage is
  exhaustive and arithmetic is exact or rigorously bounded.
- A synthetic separation validates the instrument, not its occurrence in a
  transformer.
- A local Jacobian is not a differentiable model self-editor.
- A monitor score is not a safety certificate unless the link to the declared
  risk functional is separately proved or measured.
- A mathematical risk flag is evidence for audit or abstention, not authority
  to perform a capability-enhancing edit.
