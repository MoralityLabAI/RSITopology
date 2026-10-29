# ASMP-9 v0.16.2: balanced allocation is the exact maximin design

## Result in one sentence

For the independent Bernoulli cycle experiment introduced in ASMP-9 v0.13,
with every edge probability constrained to
`epsilon <= p_e <= 1-epsilon`, positive integer trial counts differing by at
most one are the unique fixed-total maximin allocation up to edge
permutation.

## The mathematical result

Let a consistently oriented cycle have `k >= 3` edges. Edge `i` receives
`n_i >= 1` independent Bernoulli trials, with

```text
sum_i n_i = N
```

and a declared probability interior

```text
0 < epsilon <= 1/2,
epsilon <= p_i <= 1-epsilon.
```

The conditional cycle experiment is informative exactly when the realized
edge counts do not contain both a zero edge and a full edge. Let `F(n)` be
the minimum probability of that event over the permitted edge
probabilities.

Then every Robin-Hood transfer

```text
(a,b) -> (a+1,b-1),  where a <= b-2,
```

strictly increases `F`. Repeating these transfers proves that the unique
maximizer, up to edge permutation, is the balanced allocation.

If

```text
N = q k + t,  0 <= t < k,
```

the optimum has `k-t` edges with `q` trials and `t` edges with `q+1` trials.

Write

```text
r = 1-epsilon, s = epsilon,
x_u = 1-r^u,
y_u = 1-s^u,
z_u = 1-r^u-s^u.
```

The exact optimal value is therefore

```text
F_star(k,N,epsilon)
  = min over 0<=j<=k-t and 0<=l<=t of

      x_q^j y_q^(k-t-j) x_(q+1)^l y_(q+1)^(t-l)
    + y_q^j x_q^(k-t-j) y_(q+1)^l x_(q+1)^(t-l)
    - z_q^(k-t) z_(q+1)^t.
```

This reduces nature's endpoint search from `2^k` labelings to
`(k-t+1)(t+1)` exact cells.

For target availability `1-delta`, the necessary and sufficient total trial
budget inside this model is

```text
N_star(k,epsilon,delta)
  = min {N >= k : F_star(k,N,epsilon) >= 1-delta}.
```

## Why balancing works

Fix two imbalanced counts `a <= b-2` and freeze the labels on all other
edges. Their contributions reduce to three constants

```text
0 <= W <= m <= M.
```

Minimizing over the selected pair's four endpoint labels leaves two
branches:

```text
S_ab = M x_a x_b + m y_a y_b - W z_a z_b
O_ab = M x_a y_b + m y_a x_b - W z_a z_b.
```

The same-label branch improves because

```text
E_ab = x_a x_b + y_a y_b - z_a z_b
     = 1-r^a s^b-s^a r^b
```

is nondecreasing under balancing and the remaining products are
log-concave. The opposite-label branch improves because

```text
D_ab = x_a y_b + y_a x_b - z_a z_b
     = 1-r^(a+b)-s^(a+b)
```

depends only on the fixed pair total, while its remaining product terms
increase. Both branches improve, so their minimum improves. Minimizing over
the other edge labels preserves the strict inequality.

The boundary cases are real:

- at `epsilon=0`, worst-case availability is zero for every finite
  allocation; and
- at `k=2`, the opposite-label branch can depend only on total count, so
  uniqueness fails.

## Prospective verification

The theorem, implementation, prior-art boundary, protocol, exact logarithmic
threshold search, and tests were frozen at commit
`af94d8db0fd4164e94a116487894459a79972f35`.

The prospective registration was committed at
`c139fa3363763de6ab52b8727f0ff3e4a3545654`. It sealed 26 files, including
the immutable records of two earlier registered resource aborts.

The fresh registered run covered:

- 504 pairwise proof games;
- 16 full global-allocation cells;
- 12 compact-value/full-endpoint comparisons;
- 36 exact total-budget thresholds; and
- 6 negative-boundary controls.

All ten registered gates passed. The 36 thresholds required 495 exact value
evaluations under exponential bracketing and binary search; the largest
selected total was `3114`.

The complete run, including result serialization and ledgers, took
`41.8990082` seconds, peaked at `34,738,176` resident bytes, and used no GPU,
against frozen caps of 120 seconds and 1 GiB.

## Independent replay

The independent verifier:

- recomputed all 26 sealed hashes;
- verified all result, report, start, and progress hashes;
- replayed every pairwise identity;
- re-enumerated every registered allocation and endpoint assignment;
- replayed every compact value and boundary;
- recomputed every logged threshold-search evaluation exactly; and
- checked the complete-run resource envelope.

All 46 checks passed. A detached clean-worktree replay also passed all 19
focused tests and the same 46 checks.

## Why versions v0.16 and v0.16.1 remain in the record

Version v0.16 exceeded the frozen 120-second cap before producing an atomic
result. Version v0.16.1 completed four stages but its linear threshold scan
also exceeded the same cap. Neither run evaluated the scientific gates.

Version v0.16.2 did not relax the theorem, gate universe, or cap. It replaced
the linear scan with an exact logarithmic search and used a third disjoint
registry. The two aborts are evidence about implementation cost, not evidence
for the theorem, and remain sealed dependencies.

## Prior art and claim boundary

Majorization, Robin-Hood transfers, reliability allocation, and optimal
paired-comparison design are established subjects. This result is presented
as a narrow ASMP-9 specialization: it closes the fixed-total integer
allocation question for one exact conditional quotient, not as a new general
theory of majorization.

It does not cover adaptive allocation, multiple-cycle graphs, dependent
responses, asymmetric interiors, unknown response links, downstream power
rather than availability, behavioral validation, general inverse
reinforcement learning, or ASMP-9 resolution.

## Canonical artifacts

- [`THEOREM_v0_16.md`](../balanced_design_v0_16/THEOREM_v0_16.md)
- [`PRIOR_ART_GATE_v0_16.md`](../balanced_design_v0_16/PRIOR_ART_GATE_v0_16.md)
- [`PROTOCOL_v0_16_2.md`](PROTOCOL_v0_16_2.md)
- [`registration_v0_16_2.json`](registration_v0_16_2.json)
- [`RESULT_v0_16_2.md`](artifacts_v0_16_2/RESULT_v0_16_2.md)
- [`result_v0_16_2.json`](artifacts_v0_16_2/result_v0_16_2.json)
- [`receipt_v0_16_2.json`](artifacts_v0_16_2/receipt_v0_16_2.json)
- [`verification_v0_16_2.json`](artifacts_v0_16_2/verification_v0_16_2.json)
- [`release_manifest_v0_16_2.json`](release_manifest_v0_16_2.json)
- [`RESOLUTION_AUDIT_v0_16.md`](../RESOLUTION_AUDIT_v0_16.md)
