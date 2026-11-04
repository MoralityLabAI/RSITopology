# ASMP-6 balanced-cover parity result v0.2.1 verification repair

## Verdict

`sharp_uniform_alphabet_parity_frontier`

For two equiprobable messages and an `m`-symbol uniform benign cover, exact
message-averaged covertness permits perfect one-shot decoding if and only if
`m` is even.  When `m` is odd, the exact minimum Bayes error is `1/(2m)`.
Exact per-message covertness forces chance error `1/2` for every `m`.

## Task result

Write `d_i=P0_i-1/m`.  Exact averaged cover gives
`P1_i=1/m-d_i`, while probability feasibility gives `|d_i|<=1/m` and
normalization gives `sum_i d_i=0`.  Equal-prior Bayes error is

```text
(1 - TV(P0,P1))/2 = (1 - sum_i |d_i|)/2.
```

If `a` coordinates of `d` are positive and `b` are negative, their common
total mass is at most `min(a,b)/m`.  Therefore

```text
TV(P0,P1) <= 2 floor(m/2) / m.
```

The bound is attained by assigning `+1/m` to `floor(m/2)` coordinates,
`-1/m` to the same number, and, only for odd `m`, zero to the remaining
coordinate.  Even alphabets split into disjoint message supports.  Odd
alphabets retain one shared neutral symbol and hence error `1/(2m)`.

## Verification repair

The primary execution now binds its formula to the frozen uniform-cover,
two-message, equal-prior protocol and rejects semantic mutations.  It emits
only a pre-verification measurement status and an
`await_independent_verification` operation.

The import-independent path reconstructs and compares every field of all 30
registered cells `m=2..31`; recalculates probability, exact cover, total
variation, Bayes error, and the primary gates; replays the full continuous
feasible-polytope vertices for `m=2..9`; and checks the closed-form dual through
`m=63`.  A mutation of the previously unchecked `m=31` cell is now rejected.

## Five conclusion layers

- **Metric robustness:** symbol relabeling, parity-boundary sensitivity,
  cover-relaxation monotonicity, dual-bound anti-gaming, and identical-law
  clean control are independently reconstructed.
- **Task result:** the sharp one-shot parity frontier above.
- **Measurement reliability:** exact rational full-grid reconstruction plus
  independent continuous-extremal and dual replays.
- **Claim support:** one shot, two equiprobable messages, uniform finite cover,
  and exact message-averaged cover only.
- **Operational decision:** register a multiletter successor only after
  independent verification and a passing source/artifact-bound receipt.

## Claim boundary and artifact state

This package contains no language, learned encoder, shared key, adaptive
policy, active auditor, or history.  It is not an asymptotic capacity theorem,
an operational covert channel, or a resolution of ASMP-6.  The elementary
extremal argument is not claimed as novel.

The primary and verification artifacts can be regenerated from the repaired
source.  The final receipt is deliberately not fabricated from an uncommitted
working tree: after the repaired source is committed,
`synthesize_receipt.py --source-commit <40-hex-commit>` binds the exact source
bytes and SHA-256 hashes of the protocol, primary result, and independent
verification.  It also requires the stored verification to match a fresh
independent replay, blocking a stale passing artifact whose input hash was
manually updated.  It refuses output on any mismatch.

The accepted source checkpoint is
`75757216a7c6c73d704308170006ef0ecd700d99`. Its committed source hashes
match the working bytes, the stored independent verification matches a fresh
replay exactly, and all eight final receipt checks passed.

| Generated artifact | SHA-256 |
|---|---|
| `artifacts_v0_2/result_v0_2.json` | `7e28898c132996212482454a97c73eb95466bd2c8f8b60e994bb5d06d804c32c` |
| `artifacts_v0_2/verification_v0_2.json` | `4d500af4d8747f2ee218ec2fe126e1f52a16981c4f42699a17138d9fd642c586` |
| `artifacts_v0_2/final_receipt_v0_2.json` | `ffc0dc6e5406810722b2be28fc96ce60597c03f56b700c9a191cf24b220047d9` |

Focused tests: `24 passed`.
