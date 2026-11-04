# ASMP-4 v0.11 reviewer packet

## Review question

Does the same-plant sensor-registry fork survive after replacing the v0.6
binary-input derivative shortcut with an operational local-control certificate
and a primary-definition-level NHIM audit?

The proposed answer is yes.

## Minimal claim

On the plant

```text
n_next=(3/2)n+u-q(z),  z_next=w,  u in [-1,2],
```

only `u=q(z)` preserves the exact safe manifold.  Both safe values, `0` and
`1`, are interior to the bounded authority interval.  A uniform local box is
reachable by `u=q(z)+eta-(3/2)n`.

Putting the bi-infinite disturbance word in a full-shift base gives the
closed-loop fiber cocycle `phi(k,omega,n)=(3/2)^k n`.  The point
`M(omega)={0}` satisfies the mapped primary random-NHIM definition for every
mode sequence.  Computed and raw sensor registries retain exact regions
`[1,infinity) x [1,infinity)` and `[2,infinity) x [1,infinity)`.

## Fast reproduction

From this directory, run:

```powershell
python run_verification.py
python verify_nhim_cocycle_audit.py
python -m pytest -q test_nhim_cocycle_audit.py
```

Expected results are twelve central gates, eleven import-independent checks,
and ten focused tests.

## Evidence ledger

- Three SHA-256 seals bind the canonical source and the v0.6/v0.10 claims.
- PDF pages 4 and 5 of the primary source were rendered and visually checked.
- Definitions 2.1-2.4 are mapped clause by clause.
- The local box `|n|<=1/6`, `|eta|<=3/4` fits exactly inside the authority
  margin.
- Cocycle composition is checked for positive and negative integer times.
- Uniform Bernoulli cylinder mass is shift-invariant.
- Every one of 5,460 mode words through horizon six is safe under the causal
  feedback.
- Five category-breaking mutations are rejected.
- Eleven predecessor packages contribute 145 tests; with the ten v0.11 tests,
  the integrated ASMP-4 chain contains 155 tests.

## Caveats to preserve

1. The canonical source does not select a random-cocycle NHIM definition.
2. The full-shift probability measure is definitional scaffolding only; the
   safety quantifier remains every disturbance sequence.
3. The invariant fiber is a zero-dimensional point.  No positive-volume or
   perturbation-stable safety theorem is claimed.
4. The repair changes the plant authority from the v0.6 binary set to a bounded
   interval, but both sensor branches use exactly the same repaired plant and
   only the same two controls can be safe.
5. External expert review remains absent.

## Falsification conditions

Reject the repair if any of the following is shown:

- the local reachability control can leave `[-1,2]` inside the declared box;
- an extra interval control preserves `K` at one of the four modes;
- the full-shift fiber fails a checked Definition 2.1-2.4 clause;
- a current control depends on a future mode;
- the interval authority changes either exact transcript-language converse; or
- the zero-dimensional random manifold is excluded by the registered positive
  class ultimately chosen for ASMP-4.
