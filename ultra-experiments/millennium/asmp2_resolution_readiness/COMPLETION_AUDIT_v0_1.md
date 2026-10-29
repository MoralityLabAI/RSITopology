# ASMP-2 resolution-readiness completion audit

## Outcome

The admissible user-level terminal condition is met by a convincing
harness-based stopping argument. The mathematical problem itself remains
unresolved.

```text
decision = stop_full_resolution_attempt_pending_successor_definition
problem_resolved = false
stop_is_supported = true
```

## Resolution-obligation audit

| Frozen v0.1 obligation | Current evidence | Adjudication |
| --- | --- | --- |
| Local semiparametric characterization | Existing crossed-shift fixture plus the new positive-Fisher smooth witness | Partial examples only; no bound definition of regular certificate, minimax radius, quotient norm, or conditioning modulus |
| Separate local-to-global theorem | General finite-source bump lemma and exact rational instance | Sharp no-free-lunch result for unrestricted smooth QMD continuation; no positive frontier can be stated until the continuation class and constants are bound |
| Minimax sample bounds | Source laws in the witness are exactly equal, giving an infinite-sample impossibility at fixed finite sources | Negative side only; v0.1 does not bind a sample-allocation or loss regime for a matching positive rate |
| Active environment design | Existing exhaustive 65,536-subset census rejects one myopic selector | Does not generalize; v0.1 binds no action space, cost, budget, objective, or tie rule |
| No-free-lunch converse | General finite-source bump lemma; exact QMD/full-support/non-inert instance | Established for unrestricted smooth continuation classes |
| Full positive resolution | No | Not achieved |
| Full negative resolution of the classification program | No | The v0.1 statement is not closed enough to identify the universal sentence that would need refutation |
| Evidence-backed reason to stop | Closure audit plus countermodel plus independent verifier | Achieved |

## Verification evidence

- New harness tests: `5 passed`.
- Independent result verifier: `12/12` checks passed.
- Existing crossed-shift regression suite: `7 passed`.
- Existing active-design regression suites: `14 passed`.
- `git diff --check`: passed.
- Repository-wide candidate-set validator: baseline failure,
  `receipt hash mismatch: README.md`. The README is tracked and unmodified by
  this work; its working-tree SHA-256 is
  `07378C8F690EE910733BD510CF115C284B5B5B198F3980D2C4038B7722BE566A`,
  while the frozen receipt expects
  `887896BC82CE9B1C839795055448CAD5B383D5B4B28483DCB8272F8901F2D994`.
  This unrelated sealed-byte mismatch is not repaired here.

## Artifact integrity

- `resolution_harness.py`:
  `7CCAFB49D28DBECD28EF66AC3C812ED4D2187BFF6D4E925DE811919510C89557`
- `verify_result.py`:
  `00DDEFDACB2DB89C520D29A2C1E5878E25A67B855993C03BBC9DAE73184E9464`
- `artifacts/result_v0_1.json`:
  `B9B3159ADF460ADD88541BB44B289D822C92ADACFD9C1294B3C650804F6C9359`
- `artifacts/verification_v0_1.json`:
  `A9ED95CD4A1E90B36FA683A46AB3CBED9DDF5F30621015C3B881BBDE1E821B0A`

## Claim boundary

The stop applies to a **full-resolution attempt against v0.1 as written**. It
does not say that local semiparametric certification is impossible, that no
quantitative continuation theorem exists, or that a successor ASMP-2 cannot
be solved. It says the successor must first bind the fifteen formal slots
listed in `STOPPING_ARGUMENT_v0_1.md`; otherwise further finite experiments
cannot be mapped to the five resolution obligations without changing the
problem after seeing the outcome.
