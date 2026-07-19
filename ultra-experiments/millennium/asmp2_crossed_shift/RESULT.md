# ASMP-2 crossed-shift pilot result

## Decision

**Stage decision: `pass`.** ASMP-4 may open.

The instrument status is `valid` and the evidence label is
`instrument_valid_forced_construction`. This is an exact implementation check
of an analytic proposition, not empirical evidence for a general
shift-spanning theorem.

## Registered outcome

- Registration commit: `a22b1770ce0f645d8aec2f0951a0f118f072b216`
- Runner gates G0–G5: all passed.
- Independent G6 checks: 20/20 passed.
- Exact Fisher matrix: `[[5/64,1/64],[1/64,5/64]]`.
- Exact minimum Fisher eigenvalue: `1/16`; `kappa=1/4`.
- Crossed ambiguity at radii `1/4,1/2,1`: `1/64,1/16,1/4`.
- Matched unspanned ambiguity: `1/16,1/8,1/4`.
- Count-matched diagonal world gap: `1/16`.
- Safety values at `(1,1)`: `3/4` and `1/2`, on opposite sides of `3/5`.
- Signed-permutation checks: 8/8 passed.
- Runtime: 0.1321 seconds; Python allocation peak: 40,244 bytes.

The tracked diff was empty at run start, and every sealed input matched its
committed blob.

## Artifact hashes

- Protocol SHA-256:
  `0dba5b32185e4e4639804f2adb6ca2df1352738205cc7a82dc2458d74b353819`
- Result SHA-256:
  `f3cc10d87fd2a60b8239cbcbb3ed42af8c423bebc159147652648669244dbbdf`
- Verification SHA-256:
  `49ef4149a90e8b56203ba943e4a02281662b7c829a3960dfc9fa0b040317e284`

Canonical artifacts are in [`artifacts/`](artifacts/).

## Interpretation

The run verifies one explicit counterexample to the implication “local tangent
span implies global safety”: the source score experiment has full exact Fisher
rank, while a crossed term is invisible on the axial source design and creates
global ambiguity away from it. This outcome was forced by the construction and
therefore validates only the arithmetic, controls, and certificate format.

It does not establish semiparametric necessity or sufficiency, a useful active
environment policy, minimax sample bounds, or any resolution of ASMP-2. The
higher-dimensional sweep remains unregistered and was not run.
