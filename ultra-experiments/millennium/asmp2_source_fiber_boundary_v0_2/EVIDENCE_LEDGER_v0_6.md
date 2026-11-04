# ASMP-2 candidate-resolution evidence ledger

## Verified artifacts

- Source-fiber/QMD result SHA-256:
  `4CA74700E0162D034F484C19BF1406A61218AE3E7110C2FAC0E37F3AE3A0E2F0`
- Independent source-fiber verification SHA-256:
  `4D2E1DCDDA8D2B741D27F377715BE3E32138B3397140AEF56A29309CBD3A72E7`
- Safety-deficiency result SHA-256:
  `8487B5984B20AC04B69F24B1B630FC092940CAA297674723743D54E0803F696B`
- Independent deficiency verification SHA-256:
  `566A9125E440611B81A02361231519A10231D52364399A1EFCEA0C187ACD0743`

## Test evidence

Run in their own directories because the older suites use colliding flat
module names such as `run.py`:

| Suite | Result |
| --- | ---: |
| Existing crossed-shift | 7 passed |
| Existing active-design versions | 14 passed |
| New source-fiber, deficiency, population/finite LP-dual, Lipschitz, and local-counterexample suite | 30 passed |
| **Total** | **51 passed** |

Independent artifact verifiers:

- source-fiber/global/local packet: `13/13`;
- finite-sample safety-deficiency packet: `6/6`.

The exact population-fiber LP sub-suite covers all `438` nonempty good-action
hypergraphs with one to three worlds and two to three actions. The noisy finite
experiment LP additionally covers all `81` binary two-world experiment/good-set
combinations and matches exact product-experiment majority values.

## Claims proved

- exact source-fiber necessary-and-sufficient criterion;
- exact primal/dual adversarial certificate for finite fibers;
- exact constructive Markov-kernel/least-favorable-prior LP for finite noisy
  source experiments;
- individually feasible opposite-action smooth QMD no-free-lunch pair;
- exact all-sample minimax success `1/2`;
- density iff global determination for continuous, bump-rich classes;
- finite randomized active-design lower bound without positive margin on
  domains admitting arbitrarily large bump packings;
- exact McShane/Whitney positive Lipschitz continuation criterion;
- exact frozen midpoint active-design control;
- literal refutation of factorization-only local safety sufficiency; and
- decision-specific deficiency reduction for sample complexity and design,
  with an explicit attainment/strict-boundary qualification.

## Claims not proved

- a new theorem beyond established Blackwell/Le Cam, semiparametric, optimal
  recovery, and optimal-design theory;
- a computable closed form for arbitrary infinite semiparametric classes;
- measurable-selection results for every nonfinite action/model space;
- independent expert-team reproduction; or
- community acceptance that operational safety deficiency satisfies the
  intended ASMP-2 novelty standard.

## Completion adjudication

The mathematical evidence supports a candidate negative resolution or
withdrawal of v0.1 as under-specified/classically reducible. It does not support
marking the repository's community-level `resolved` gate true without external
adjudication.
