# ASMP-9 v0.23: nonuniform local value and the K4 exchange trap

ASMP-9 v0.23 closes the exact nonuniform-value representation at
`epsilon=1/2` and falsifies a tempting greedy optimization principle.

For a finite simple biconnected comparison block with arbitrary positive
integer edge counts `n_e`,

```text
F_G(n)
  = -2^(-sum_e n_e) Z_G(-1,{2^(n_e)-1}).
```

This is a direct ASMP specialization of Sokal's classical multivariate Tutte
polynomial and Backman's weighted partial-orientation formula.  No new graph
polynomial is claimed.

The new obstruction occurs on K4.  At total count `6s`, for every `s>=2`,

```text
trap     = (s-1,s,s+1,s+1,s,s-1)
balanced = (s,s,s,s,s,s).
```

Every feasible one-unit transfer from the trap makes exact availability
worse, yet the balanced point is strictly better:

```text
balanced numerator - trap numerator
  = 3*2^s*(3*2^s-4)/2 > 0.
```

The same pair gives a direct violation of the M-concavity exchange axiom.
Thus one-unit exchange ascent can terminate at a strict suboptimal local
maximum; it has no general global-optimality guarantee for this objective.

All eleven prospectively registered gates passed on a fresh
seven-node/eleven-edge block and fresh numeric K4 checks.  A separately
implemented verifier passed 21/21 checks.  Runtime was 9.63 seconds on CPU
with 39,989,248 peak resident bytes.

The result does **not** classify the global maximin optimizer, prove optimizer
NP-hardness, cover arbitrary response probabilities, or resolve ASMP-9.
