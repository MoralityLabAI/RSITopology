# Prior-art boundary for ASMP-1 representation theorem v0.2

## Status

The mathematical ingredients are classical. The contribution claimed here is
their consolidation into a representation-sensitive answer to the four
ASMP-1 obligations and an executable exact audit. No new theorem in
computable analysis, real algebraic geometry, compressed sensing, or Gaussian
decision theory is claimed.

## Fiber factorization and linear recovery

Identifiability as constancy on observation fibers is the definition-level
criterion used throughout statistics and inverse problems. The factorization
form and the linear row-space/kernel test are elementary. The singular-value
stability modulus, pseudoinverse recovery, Gaussian concentration bound, and
two-point testing lower bound are standard inverse-problem tools.

Algebraic compressed sensing studies much richer polynomial signal varieties,
global uniqueness, local recoverability, and optimal measurement counts:

- Paul Breiding, Fulvio Gesmundo, Mateusz Michałek, and Nick Vannieuwenhoven,
  “Algebraic compressed sensing,” 2021:
  <https://arxiv.org/abs/2108.13208>

The v0.2 linear-gauge theorem should be described as a transparent calibration
class, not as an advance over that literature.

## Semialgebraic decision lane

Tarski-Seidenberg quantifier elimination makes the first-order theory of real
closed fields decidable. Applying it to statistical model constraints and
identifiability is established practice:

- Dan Geiger and Christopher Meek, “Quantifier Elimination for Statistical
  Problems,” 2013: <https://arxiv.org/abs/1301.6698>
- Lou van den Dries, “Alfred Tarski's elimination theory for real closed
  fields,” *Journal of Symbolic Logic* 53 (1988), 7-19.

The present result only writes the ASMP-1 quotient-fiber failure condition in
that language. It makes no polynomial-time claim.

## Analytic and computable-real undecidability

The harness uses a direct Cauchy-name reduction from halting, so its theorem
does not depend on a black-box identity theorem. It is adjacent to the
classical undecidability of identity questions for rich elementary-function
languages:

- Daniel Richardson, “Some undecidable problems involving elementary
  functions of a real variable,” *Journal of Symbolic Logic* 33(4), 1968,
  514-520: <https://doi.org/10.2307/2271358>

The direct reduction is deliberately narrower in syntax: the mechanisms are
degree-one entire functions, but their coefficients are supplied by arbitrary
computable-real Cauchy programs. The undecidability lies in exact coefficient
equality. A certified nonzero separation promise removes this particular
obstruction.

The theorem also gives an equivalent program-generated Taylor representation
with coefficients only in `{0,1}`, at most one nonzero coefficient, and a
uniform evaluation modulus on a compact domain. This is still an application
of standard halting/equality undecidability, not a claimed new computable
analysis theorem.

## Novelty and claim rule

The safe claim is:

> ASMP-1 v0.1 crosses a representation boundary it does not currently freeze.
> Exact quotient identifiability is decidable for rational semialgebraic
> encodings, uniformly undecidable for arbitrary computable-real analytic
> encodings without a certified gap, and sharply constructive for the frozen
> linear translation-gauge subclass.

Do not claim a new Tarski, Richardson, compressed-sensing, pseudoinverse, or
minimax theorem.
