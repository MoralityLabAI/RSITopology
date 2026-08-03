# ASMP-6 balanced-cover parity protocol v0.2

## Frozen optimization problem

Let `Q` be uniform on `m >= 2` opaque symbols.  Two equiprobable messages use
laws `P0` and `P1`.  The averaged-cover arm requires

```text
(P0 + P1) / 2 = Q.
```

The messagewise arm requires `P0=P1=Q`.  The score is optimal equal-prior
Bayes decoding error.  No active auditor, block code, or history is present.

Writing `d_i=P0_i-1/m` gives `P1_i=1/m-d_i`, `sum_i d_i=0`, and
`|d_i|<=1/m`.  The Bayes error is

```text
(1 - sum_i |d_i|) / 2.
```

The registered theorem grid is `m=2..31`.  An import-independent verifier
enumerates every ternary extremal sign vector through `m=9` and checks the
general sign-count dual bound through `m=63`.

## Gates

- exact probability and averaged-cover feasibility;
- matching achievability and sign-count upper bound;
- perfect decoding if and only if the alphabet is even;
- messagewise-cover chance control; and
- invariance, sensitivity, monotonicity, anti-gaming, and clean-control probes.

## Conclusion layers

- **Task result:** the exact one-shot parity theorem.
- **Measurement reliability:** rational witnesses, a closed-form dual bound,
  and import-independent extremal enumeration.
- **Claim support:** uniform finite alphabets, two equiprobable messages, and
  exact cover only.
- **Operational decision:** use parity as a regression fixture; next work must
  register block/history semantics and an active auditor.

## Claim boundary

This does not provide a linguistic or learned covert channel, an asymptotic
capacity theorem, a multiletter result, a keyed construction, or a resolution
of ASMP-6.  The elementary extremal argument is not claimed as novel.
