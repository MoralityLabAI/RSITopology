# ASMP-1 representation and recovery boundary result v0.2

## Outcome

All exact harness gates passed. The result replaces the failed structural
cut-separation iff with a representation-sensitive classification:

1. the universal exact criterion is observation-fiber refinement, equivalently
   factorization of `Q/G` through the registered experiment;
2. rational semialgebraic instances with a finite rational gauge are decidable
   by real-closed-field quantifier elimination;
3. no uniform exact criterion exists for arbitrary computable-real analytic
   encodings without a certified separation promise; and
4. linear analytic mechanisms with a frozen translation gauge have a sharp
   rank criterion, exact pseudoinverse recovery, finite-sample guarantee, and
   matching collision/query/sample-scaling lower bounds.

The full statements and proofs are in [THEOREM_v0_2.md](THEOREM_v0_2.md).

## Exact census

The harness enumerated every matrix over `{-1,0,1}` through quotient dimension
three and three scalar observation rows:

| Quotient dimension | Rows | Matrices | Full rank / recoverable | Deficient / exact collision |
|---:|---:|---:|---:|---:|
| 1 | 0 | 1 | 0 | 1 |
| 1 | 1 | 3 | 2 | 1 |
| 1 | 2 | 9 | 8 | 1 |
| 1 | 3 | 27 | 26 | 1 |
| 2 | 0 | 1 | 0 | 1 |
| 2 | 1 | 9 | 0 | 9 |
| 2 | 2 | 81 | 48 | 33 |
| 2 | 3 | 729 | 624 | 105 |
| 3 | 0 | 1 | 0 | 1 |
| 3 | 1 | 27 | 0 | 27 |
| 3 | 2 | 729 | 0 | 729 |
| 3 | 3 | 19,683 | 11,808 | 7,875 |
| **Total** |  | **21,300** | **12,516** | **8,784** |

For every full-rank design, exact rational arithmetic constructed and checked a
left inverse. For every deficient design, it constructed and checked a
nonzero exact nullspace collision. No design with fewer than `q` scalar rows
identified a `q`-dimensional quotient.

## Gauge and stability fixture

The registered four-parameter fixture has a two-dimensional redundant
translation gauge and a two-dimensional mechanistic quotient. The good design

```text
A_bar = [[2,0],
         [0,3]]
```

has exact recovery map `diag(1/2,1/3)` and separation modulus `kappa=2`. The
one-row design `[2,0]` has the exact non-gauge collision `(0,1)`.

The finite-sample receipt evaluates the proved Gaussian upper and two-point
lower formulas over 16 `(q,kappa)` cells. Both display the required
`kappa^-2 epsilon^-2` scaling; the upper bound also pays for simultaneous
recovery in quotient dimension `q`.

## Computability boundary fixture

For halting times `1,2,5,17,64` and a nonhalting fixture, the harness checked
the Cauchy-name construction through precision 80:

```text
c_e=0 if e never halts; otherwise c_e=2^-t.
```

Simulating `e` for `n` steps gives a rational approximation with error at most
`2^-n`. The analytic mechanisms

```text
Y_e(X,A)=(1+c_e)X+A
```

and the base `Y_0=X+A` always agree at the registered environment
`(X,A)=(0,0)` and under the registered intervention `do(A=1)` at `X=0`; their
declared targets at `(X,A)=(1,0)` agree exactly for the nonhalting case. Every
local derivative and the registered intervention effect are at least one, so
the fixture retains positive local conditioning and intervention-strength
margins. This finite execution validates the reduction mechanics. The
universal undecidability conclusion follows from the proof, not from the six
fixtures.

This closes the `kappa` escape hatch. If canonical `kappa` denotes local
conditioning, the reduction has `kappa_local=gamma=1`. If it denotes global
separation of every distinct `Q/G` pair, identifiability is already assumed by
definition and the original iff is circular.

An equivalent encoding uses only program-generated one-bit rational Taylor
coefficients:

```text
a_(e,n)=1 iff e first halts at n,
h_e(X)=sum_n a_(e,n)X^n.
```

At most one coefficient is nonzero, and `h_e(1/2)=c_e`. On `X<=1/2`,
simulating `n` steps gives error at most `2^-n`. Thus the impossibility is not
an artifact of hiding an arbitrary real behind a single opaque coefficient; it
persists for a finite program generating rational analytic coefficients with a
known evaluation modulus.

The Taylor form binds directly to
`C(n=3,s=2,d=2,p=1,F,B=2,kappa_local=1,gamma=1)`: `F` has two deterministic
entire mechanisms and covering number at most two, `E` contains `(X,A)=(0,0)`,
`I` contains the live intervention `do(A=1)`, `Q(Y)=Y(1/2,0)`, and `G` is the
identity.

## Resolution consequence

The v0.1 demand for one polynomial recovery theorem across a parametrically
described analytic function class cannot stand without an effective encoding
restriction. There are three distinct lanes:

| Encoding lane | Exact status |
|---|---|
| Rational semialgebraic, finite rational gauge | Decidable; general polynomial time not claimed |
| Program-named computable-real analytic coefficients, no certified gap | Uniform exact identifiability undecidable |
| Linear rational mechanism with full declared translation gauge | Sharp rank boundary, polynomial recovery, finite-sample bound, matching negatives |

This is stronger than another counterexample to cut coverage: it states why a
uniform replacement criterion cannot exist at the current representation
generality and supplies a complete constructive replacement on a nontrivial
tractable lane.

## Claim boundary

The result is a candidate negative resolution of the **uniform** ASMP-1
classification program and a complete positive resolution of the frozen
linear-gauge subclass. Whether it closes canonical ASMP-1 v0.1 depends on an
external scope judgment: does its phrase “exact encoding and coefficient
bit-complexity are part of `F`” admit arbitrary computable-real Cauchy
programs, or was a decidable rational/algebraic language intended?

Until that representation choice is adjudicated, the safe repository status
is:

```text
uniform boundary established; full canonical resolution candidate,
not yet externally validated as resolved.
```

The theorem does not establish transformer-model class membership or that any
declared abstraction is safety-complete.

## Receipt

The machine-readable receipt is `artifacts/result_v0_2.json`. Its source hash,
cell counts, exact recovery/collision checks, finite-sample formula cells,
Cauchy-name fixtures, and all gate records are stored there.

The independent recomputation receipt is `artifacts/verify_v0_2.json`. It
recomputed the full result, matched the source hash and all 21,300 cells, and
passed every registered document/count/partition check.
