# Result v0.31

## Closed finite-quotient seam

The complete additive read/write budget region of a finite alternating public
quotient is

`intersection_tau union_C upward(conv(simple-cycle means in C of G_tau))`.

The `limsup` cost objective maps exactly to conjunctive mean-payoff-`inf` after
the sign change `w=R-c`. Classical memoryless-spoiler determinacy makes the
intersection over adversary policies exact; reachable SCC multicycles give the
inner one-player formula.

The arbitrary-memory region is closed and equals the closure of the
finite-memory region. Exact finite-memory attainment can fail: the connector
fixture reaches boundary `(1,1)` only with increasing memory, while a period
with `k` loops per side has exact slack `1/(k+1)`.

## Harness evidence

- Central: 256 games, 2,304 exact budget decisions, 1,202 wins and 1,102 losses.
- Independent: 81 games, 1,296 decisions, 776 wins and 520 losses, plus 162
  adversary-policy checks.
- Every losing census instance has a directly validated memoryless spoiler.
- Adversarial and controller irreversible forks separately validate policy
  intersection and component union.
- Central 512-stage and independent finite-period checks validate the
  infinite-memory closure boundary.
- Eight false quantifier, geometry, memory, and polarity mutations are rejected
  in both implementations.

The central wrapper, independent verifier, all 10 focused tests, and lint pass.
The explicit 32-package chain passes all 354 tests in 336.76 seconds with
Python bytecode and pytest caching disabled. Exact wrapper timings are in
`COMPLETION_AUDIT_v0_31.md`.

## Not claimed

No novelty is claimed for classical multi-mean-payoff game theory. The package
does not construct finite exact quotients for arbitrary nonlinear plants,
claim finite-memory attainment at every boundary point, or provide general
finite-horizon safety-margin corrections.

V0.32 audits those exclusions against the full frozen completion standard and
issues the current operational stop on further autonomous bounded expansion.

V0.33 then reopens the nonfinite theorem route: safe closing promotes reset
blocks to complete component regions without assuming the finite quotient that
this package computes after it is supplied.

V0.35 constructs that safe-closing property from a finite robust fixed-reset
atlas, bypassing the finite game when registered nonlinear connector tubes are
available.
