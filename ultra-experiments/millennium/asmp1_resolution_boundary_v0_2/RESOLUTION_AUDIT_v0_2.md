# ASMP-1 v0.2 resolution audit

## Verdict

**Candidate negative resolution of the uniform representation-independent
program; complete resolution of the linear-gauge lane; canonical v0.1 remains
pending scope adjudication.**

The result should not be marked as an unconditional full ASMP-1 resolution
without independent review of the encoding quantifier.

## Canonical obligation matrix

| Canonical obligation | General representation-sensitive result | Linear-gauge lane | Audit |
|---|---|---|---|
| 1. Maximal or justified quotient | `X/~O` is the universal maximum-information identifiable quotient; declared `Q/G` must factor through it | Gauge subspace `N` is frozen as the full kernel of parameter-to-mechanism realization | Satisfied as a criterion; functional relevance of any chosen `Q` remains an external premise |
| 2. Necessary and sufficient intervention/environment conditions | Observation-fiber refinement is exact; semialgebraic failure is decidable; arbitrary computable-real lane is uniformly undecidable | `ker(A)=N`, equivalently quotient row rank `q` | Satisfied in the linear lane; no representation-independent graph criterion exists |
| 3. Constructive recovery with finite-sample stability | Semialgebraic recovery is decidable in principle but not polynomially bounded; uniform computable-real recovery is impossible | Exact pseudoinverse, `kappa=sigma_min`, explicit Gaussian/sub-Gaussian bound | Satisfied in the linear lane |
| 4. Matching indistinguishability/query lower bounds | Halting reduction rules out a total uniform exact decider without a certified gap | Exact kernel collision, minimum `q` scalar rows, two-point `kappa^-2 epsilon^-2 log(1/delta)` lower bound | Satisfied in the linear lane and negatively at the uniform encoding boundary |

## Why this may qualify as the canonical negative branch

The canonical document permits a broader-program resolution by proving that no
computable criterion of the declared form can exist. Theorem 4 proves exactly
such a uniform impossibility if the registered encoding family includes
arbitrary computable-real Cauchy programs. It uses degree-one entire functions
with local conditioning and registered intervention strength at least one, so
the obstruction is not nonlinear geometry, high dimension, or a zero-margin
mechanism.

The canonical `kappa` ambiguity does not remove the result. On the local
conditioning reading, the reduction has `kappa_local=gamma=1`. On the global
quotient-separation reading, Theorem 2 shows that `kappa>0` already implies the
desired identifiability, making the Cut-Separation Conjecture circular.

The equivalent Taylor-series form uses only program-generated rational
coefficients `a_(e,n) in {0,1}`, at most one nonzero coefficient, and a known
`2^-n` evaluation modulus on `X<=1/2`. Excluding it therefore requires `F` to
be a finite rational/algebraic grammar with a declared degree or coefficient
cutoff, not merely an exactly encoded analytic program with bit complexity.

The genericity clause also does not silently remove the construction. Each
registered instance is a finite zero-dimensional semantic class, and the
identifiability verdict is uniform on that class. Treating the nonhalting
coincidence as an excluded representational degeneracy requires deciding the
same program equality and is not an effective algebraic or measure-theoretic
genericity rule supplied by v0.1.

The same theorem also identifies the repair: restrict `F` to a decidable
representation language or require a valid, independently checkable
separation certificate. Theorem 3 and Theorems 5-7 then describe two repaired
lanes.

## Why full closure is not yet claimed

The phrase

> “The exact encoding and coefficient bit-complexity are part of `F`”

has two plausible scopes:

1. `F` may be any finitely described analytic evaluator, including a
   computable-real Cauchy program. Then the uniform negative theorem applies
   and is a candidate canonical resolution.
2. `F` was intended to be a fixed decidable rational/algebraic grammar with
   certified margins. Then the undecidability construction lies outside the
   intended class, and the semialgebraic theorem gives decidability but not the
   demanded polynomial recovery theorem for arbitrary nonlinear instances.

The v0.1 text does not choose. The repository should therefore expose this as
the last scope fork rather than silently select the branch that makes the
resolution claim easiest.

## Evidence audit

- Universal theorems: proofs in `THEOREM_v0_2.md`.
- Linear implementation: 21,300 exhaustive exact-rational matrix cells.
- Recovery branch: 12,516 exact left-inverse checks.
- Negative branch: 8,784 exact nonzero collision witnesses.
- Query lower bound: zero full-rank cells whenever rows `< q`.
- Computable-real reduction: uniform Cauchy modulus proved and checked through
  precision 80 on six fixtures.
- Independent verifier: source hash matched and the full 21,300-cell result
  recomputed semantically byte-for-byte.
- Regression tests: `test_identifiability_boundary.py` plus all earlier ASMP-1
  theorem/audit tests.

The census checks the implementation and bounded universe. The proofs, not the
census, establish the universal claims.
