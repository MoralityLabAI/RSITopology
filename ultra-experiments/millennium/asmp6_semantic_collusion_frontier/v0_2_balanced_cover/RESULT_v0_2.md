# ASMP-6 balanced-cover parity result v0.2

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
`-1/m` to the same number, and—only for odd `m`—zero to the remaining
coordinate.  Even alphabets split into disjoint message supports.  Odd
alphabets retain one shared neutral symbol and hence error `1/(2m)`.

The registered exact grid covered every alphabet size from 2 through 31.  All
probability, averaged-cover, optimality, parity, odd-error, and messagewise
control gates passed.

## Metric robustness

All five frozen probe families passed:

- symbol relabeling leaves the error unchanged;
- the `m=3` to `m=4` change crosses the divisibility boundary;
- relaxing per-message cover to averaged cover never worsens the optimum;
- every construction meets the independent sign-count bound; and
- identical message laws reproduce chance error.

## Measurement reliability

The primary path used exact `Fraction` arithmetic.  An import-independent
verifier enumerated every ternary extremal sign vector for `m=2..9` and found
zero discrepancies.  It separately checked the general sign-count formula
through `m=63`, again with zero failures.

## Claim support and operation

The result supports only a one-shot, two-message, uniform-alphabet statement
under exact averaged cover.  It is an opaque-symbol regression fixture for
future ASMP-6 instruments.  The next useful step must register multiletter or
history semantics and an active auditor.

This package contains no language, learned encoder, shared key, or adaptive
policy.  It is not an asymptotic capacity theorem, an operational covert
channel, or a resolution of ASMP-6.  The elementary extremal argument is not
claimed as novel.

## Artifact integrity

| Artifact | SHA-256 |
|---|---|
| `artifacts_v0_2/result_v0_2.json` | `afa4c9aebe274f512bc8d7bd09a7f921b6ac395e84101e7a43799583995a387d` |
| `artifacts_v0_2/verification_v0_2.json` | `26cdfbfbc84c32eacc7864393b796571ed47b83ee4afd3dfc79d0bc2468ee808` |

Dedicated tests: `5 passed`.
