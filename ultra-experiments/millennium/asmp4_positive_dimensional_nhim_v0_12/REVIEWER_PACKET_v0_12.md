# ASMP-4 v0.12 reviewer packet

## Review question

Does the sensor-registry stopping fork survive if the invariant manifold must
be genuinely positive-dimensional rather than a point?

The proposed answer is yes.

## Minimal fixture

```text
theta_next=theta+1/4 mod 1,
n_next=(3/2)n+u-q(z),
z_next=w,
u in [-1,2].
```

The safe set is `S^1 x {0} x {-3,-1,1,3}`.  Safe feedback leaves the circle
invariant and induces the cylinder diffeomorphism
`f(theta,n)=(theta+1/4 mod 1,(3/2)n)`.

The invariant circle has `E^s={0}`, normal `E^u`, tangent `TN`, unstable
inverse norm `2/3`, tangent norm `1`, and satisfies both checked classical NHIM
inequalities with `lambda=3/4`.

## Fast reproduction

```powershell
python run_verification.py
python verify_positive_dimensional_nhim.py
python -m pytest -q test_positive_dimensional_nhim.py
```

Expected results are nine central gates, eight import-independent checks, and
nine focused tests.

## Evidence ledger

- Two SHA-256 seals bind the canonical source and v0.11 claim.
- Primary-source PDF pages 3 and 4 were rendered and visually inspected.
- Definition 1 and Theorem 2.1 are mapped.
- Exact forward/inverse maps are replayed on independent rational phase grids.
- Normal hyperbolicity and tangent domination are exact rational inequalities.
- The v0.11 uniform local-control box is preserved.
- Tangent rotation contributes no read or write symbol.
- Five adversarial mutations are rejected.
- Twelve predecessor packages contain 155 tests; with v0.12 the integrated
  inventory is 164 passing tests.

## Caveats

1. The invariant circle has positive dimension but zero ambient volume.
2. ASMP-4 does not select this classical diffeomorphism class.
3. The registered sensor observes the exogenous mode, not the neutral tangent
   phase; that partial-observation experiment is explicit but not canonical.
4. The disturbance reset is represented outside the smooth cylinder fiber.
5. External expert review remains absent.

## Falsification conditions

Reject the certificate if the cylinder map is not a global diffeomorphism, the
circle is not invariant, either Definition 1 inequality fails, the tangent
phase changes a transcript language, an interval control other than `q(z)` is
safe on `K`, or one sensor branch uses a different plant, timing, or authority.
