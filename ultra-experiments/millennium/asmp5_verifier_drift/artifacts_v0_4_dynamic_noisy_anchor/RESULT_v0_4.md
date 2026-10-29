# ASMP-5 dynamic replicated noisy-anchor result v0.4

## Disposition

The registered primary grid completed, but the import-independent verifier
exceeded its frozen wall-clock budget.  The authoritative disposition is
therefore:

```text
task_result: finite_dynamic_noisy_anchor_grid_compiled
measurement_reliability: verifier_resource_stop
claim_support: not_established
operational_decision: no_generalization_or_deployment_authorized
```

This is a completed proof/experiment attempt under the attempt-coverage audit.
It is not a verified ASMP-5 result and does not resolve ASMP-5.

## Frozen evidence chain

- Source commit:
  `b3d38bb32ca8fbfc2c158ec1dae9a864881a08bd`.
- Primary-artifact commit:
  `5385df463d04f3bf8c54b587c3debfe6851f27c0`.
- Primary artifact: `result_v0_4.json`, 75,332 canonical JSON bytes,
  SHA-256
  `a400942465df5364d96d095d6a02e8fed7fa5eb23425874add7e31483ad71fe2`.
- Registry: 54 exact rows in the frozen order
  `m x epsilon x H x temporal_model`.
- All eight primary gates and all seven frozen controls passed.
- No verification artifact exists.  The verifier failed closed before writing
  one.

The source package contains exactly eight committed regular files.  Its
manifest passed the experiment-contract validator with zero errors and zero
warnings.  The cache-disabled source-only suite passed 23 tests, Ruff passed,
and the source was ASCII-only.

## Exact finite theorem attempt

For odd replica count `m`, one hazard-bit majority error has probability

```text
p_m = sum_{k=(m+1)/2}^m C(m,k) epsilon^k (1-epsilon)^(m-k).
```

The primary law freezes all `2m` bit/replica errors as mutually independent.
Because either erroneous hazard bit is independently exploitable after the
installed anchor is revealed, the per-installation visible-adversary risk is

```text
q_m = 1 - (1-p_m)^2.
```

Fresh independent replacements across `H` post-install attack opportunities
give `1-(1-q_m)^H`; a single persistent replacement gives `q_m` for every
positive `H`.  The all-errors event proves `p_m >= epsilon^m > 0`, so fresh
risk tends to one for every finite odd `m` and `epsilon>0`.  Persistent risk is
not claimed to tend to one.

Selected exact-grid values illustrate the temporal distinction:

| `m` | `epsilon` | `H` | fresh risk | persistent risk |
|---:|---:|---:|---:|---:|
| 1 | 1/10 | 64 | about 0.999998610 | 19/100 |
| 3 | 1/10 | 64 | about 0.973619568 | 3451/62500 |
| 5 | 1/10 | 64 | about 0.667260855 | 2663551/156250000 |
| 5 | 1/20 | 64 | about 0.137849911 | 5926166391/2560000000000 |

The JSON artifact retains the exact rational values; decimals above are only
readability aids.

## Controls

- `epsilon=0` reconstructed the exact anchor and zero risk in all 18 matched
  rows.
- The inherited checker-3 behavior cycle `0 -> 2 -> 0` remained a safe
  liveness fixture.
- Single-bit witnesses `0111`/class 0 and `1011`/class 1 established that each
  hazard-bit error is separately exploitable.
- Swapping hazard-bit/proof-class labels preserved every primary risk.
- Perfectly correlated hazard-bit errors and a pre-visibility one-class
  adversary both reduced per-installation risk to `p_m`, making the product
  law and reveal timing live assumptions.
- False-negative-only noise kept unsafe risk zero while retaining a live
  deadlock channel.
- Fresh risk was strictly greater than persistent risk in every positive,
  `H>1` registered comparison.

## Independent-verifier resource stop

The verifier was frozen to reconstruct the grid by complete ordered
`2m`-coin pattern enumeration (at most 1,024 patterns) and an independent
two-state recurrence, with a 15-second wall limit.  A clean replay returned

```text
verification wall limit exceeded
```

after about 91.8 seconds of external wall time.  It wrote no artifact.  The
failure concerns the verifier implementation/budget pairing; it is neither an
independent confirmation nor a mathematical counterexample to the primary
formula proof.  Any repair must be separately versioned and frozen rather
than silently relaxing this protocol.

## Claim boundary

The attempted theorem concerns one four-bit anchor, exact safe bits, a frozen
product law for one-sided hazard-bit false positives, declared fresh or
persistent temporal semantics, and an adversary with exactly two visible
proof-class choices.  It is not evidence about a neural learned checker,
arbitrary correlation, two-sided or state-dependent error, infinite distinct
states, open-ended root replacement, or ASMP-5 generally.
