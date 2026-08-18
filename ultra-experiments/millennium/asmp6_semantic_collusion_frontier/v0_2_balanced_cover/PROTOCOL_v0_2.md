# ASMP-6 balanced-cover parity protocol v0.2.1 verification repair

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
reconstructs and compares every field of every registered cell.  It enumerates
the vertices of the full continuous feasible polytope through `m=9` and checks
the general sign-count dual bound through `m=63`.  Primary gate booleans are
treated as reported data: the verifier derives their expected values again
from the reported cells and independently reconstructed probe pack.

## Executable protocol binding

The primary and independent paths separately reject the computation unless the
protocol ID/schema and all of these frozen fields hold:

- `cover_law = uniform`;
- `message_count = 2`;
- `message_prior = [1/2, 1/2]`; and
- the registered alphabet interval is exactly `m=2..31`;
- the continuous-vertex enumeration maximum is exactly `m=9`; and
- the six-item claim boundary is byte-for-byte the registered boundary.

Mutation tests replace the cover law, message count, prior, alphabet range,
enumeration maximum, and claim boundary and require both paths to fail closed.
In particular, the equal-prior Bayes formula is never reported under an
unequal-prior protocol, and a reduced grid cannot masquerade as full-grid
verification.

## Gates

- **Primary G0-G6:** executable protocol binding, exact probability and cover
  feasibility, optimality, parity, odd-error, messagewise control, and five
  metric-robustness probes.
- **Independent V0-V9:** frozen semantics, exact registered grid, full-cell
  reconstruction, probability replay, continuous-polytope enumeration,
  general dual replay, independent probes, derived primary-gate comparison,
  pre-verification layer discipline, and protocol/result identity.
- **Synthesis C0-C7:** exact source-commit bytes, artifact hashes, frozen
  protocol, primary pre-verification state, independent gates, verifier input
  bindings, final conclusion layers, and claim boundary.

## Conclusion layers

- **Metric robustness:** five probes independently reconstructed and replayed.
- **Task result:** the exact one-shot parity theorem.
- **Measurement reliability:** exact rational full-grid reconstruction, a
  continuous-polytope vertex replay, and a closed-form dual replay.
- **Claim support:** uniform finite alphabets, two equiprobable messages, and
  exact cover only.
- **Operational decision:** register the multiletter successor only after the
  independent verification artifact exists and the final receipt binds it to
  its protocol, primary result, and committed source.

`run.py` can emit only `awaiting_independent_verification`; it cannot authorize
the successor operation.  The verifier advances that decision after all
independent gates pass.  `synthesize_receipt.py` then refuses to emit a final
receipt unless every listed source file is byte-identical to the declared
40-hex source commit and all three artifacts are hash-bound.  Synthesis also
reruns the independent verifier over the bound protocol/result and requires
the stored verification JSON to equal that fresh replay exactly; a stale
passing verification cannot be rescued by editing only its declared hash.

## Claim boundary

This is exactly a one-shot opaque-symbol result for two equiprobable messages,
a uniform cover, and exact averaged-cover/messagewise-control semantics.  It
does not provide a linguistic or learned covert channel, an asymptotic
capacity theorem, a multiletter result, a keyed construction, or a resolution
of ASMP-6.  The elementary extremal argument is not claimed as novel.
