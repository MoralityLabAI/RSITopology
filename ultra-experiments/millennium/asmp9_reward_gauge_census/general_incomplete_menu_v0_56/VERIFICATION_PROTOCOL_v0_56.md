# ASMP-9 general incomplete-menu verification protocol v0.56

## Status

This protocol prospectively freezes an independent finite verification of the
arbitrary-`n` proof ingredients in `THEOREM_DRAFT_v0_56.md`.  Development
checks are burned and non-claim-eligible.

Passing supports the candidate theorem's exact proof.  Finite computation does
not by itself prove an arbitrary-`n` statement; the adjacent-swap/Möbius and
dimension arguments remain the mathematical proof.

## Candidate theorem

For every finite alternative universe with `n>=3`, complete probability-vector
access on a proper subset of the non-singleton menus has this tier ambiguity
under unrestricted positive completion:

```text
no RUM completion             -> {N}
RUM but no Luce completion    -> {R,N}
Luce completion               -> {L,R,N}.
```

## Held-out verification targets

The independent verifier must not import `general_incomplete.py`.

### H0: source integrity

Every source hash in the prospective registration must match.

### T0: tests

All registered scientific and verifier tests must pass.

### A6: new affine-rank check

For `n=6`, the ambient stochastic-choice dimension is:

```text
6*2^5 - 2^6 + 1 = 129.
```

The 720 deterministic-ranking signatures, augmented by an affine constant,
must have exact rank 130.  A full-rank certificate modulo the registered prime
`1,000,003` is sufficient: modular rank 130 implies rational rank at least
130, while the matrix has only 130 columns.

### Z0: Möbius-system check

The Boolean subset-zeta matrices through width eight must have full modular
rank `2^width`.  This checks the linear system used in the adjacent-swap proof.

### G0: component-gap check

For every integer partition of every `n` from 3 through 20, the registered
cross-component pair bound must strictly exceed `c-1` whenever `c>=2`.
Connected proper domains use the separate bound `k>=1>0`.

### N0: constructive non-RUM extensions

Using two frozen nonuniform Luce weight vectors on five alternatives, test:

- every single-missing-menu domain;
- the empty domain;
- one disconnected two-pair domain; and
- at least 128 seeded proper-domain masks.

Every constructed completion must:

- preserve every observed probability exactly;
- remain normalized and strictly positive; and
- exhibit a strict random-utility regularity violation.

### S0: lower-bound sharpness

For `n=2`, enumerate positive rational binary kernels through denominator 50
and verify that each is Luce.  Record equality of the one-dimensional empty-
domain RUM and Luce fibers.  This checks that `n>=3` cannot be weakened.

### F0: ambient formula

For `3<=n<=20`, verify:

```text
sum_{A: |A|>=2} (|A|-1) = n*2^(n-1) - 2^n + 1.
```

### RESOURCE

Use one worker, at most 120 seconds, and strictly less than 512 MiB resident
memory.

## Stop rule

Every gate must pass.  Equality at a resource cap, source mismatch, failed
test, rank mismatch, non-strict dimension bound, failed witness, or loss of
positivity/preservation is failure.  There is no discretionary override.

The result is write-once.  Repairs require a versioned protocol and fresh
registration.

## Prior-art and claim boundary

Limited-domain RUM feasibility and extension variables, complete-domain RUM,
and arbitrary-menu Luce characterization are classical.  Passing does not
establish representation-theorem novelty.

The candidate result is a finite exact full-kernel tier-identification theorem
under unrestricted completion.  It is not a sampling theorem, evidence about
human or model values, a welfare representation, a strategic/dynamic result,
a physical access theorem, or a full resolution of ASMP-9.
