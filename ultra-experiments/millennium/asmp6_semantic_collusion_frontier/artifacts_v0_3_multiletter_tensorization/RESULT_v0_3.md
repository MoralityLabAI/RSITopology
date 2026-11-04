# ASMP-6 finite multiletter tensorization result v0.3

## Verdict

`finite_registered_global_cover_block_advantage_supported`

For the twelve registered cells with alphabet size `m in {2,3,4,5}` and
block length `n in {1,2,3}`, an unrestricted rational block coupling under
exact globally message-averaged uniform transcript cover strictly beats the
registered coordinatewise memoryless product subclass in exactly four cells:
odd `m` with `n in {2,3}`. The other eight cells tie.

This is a finite model result, not an asymptotic capacity theorem or an ASMP-6
resolution.

## Exact theorem and comparison

Let `K=2^n` be the number of equiprobable payload words and `M=m^n` the number
of uniform transcripts. Write `M=qK+r`, with `0 <= r < K`. Decoder-column
occupancy gives the exact unrestricted optimum

```text
e_unrestricted(m,n) = r(K-r)/(KM).
```

A balanced rational joint coupling attains the bound. The independent verifier
established the same upper bound through a separate discrete-concavity,
pairwise-exchange, and marginal-gain certificate rather than reusing the
primary dynamic program.

The product comparator tensors the sharp v0.2 one-shot law:

```text
e_product(m,n) = 0                         if m is even,
e_product(m,n) = 1 - (1 - 1/(2m))^n       if m is odd.
```

| Cell | Unrestricted error | Product error | Product minus unrestricted |
|---|---:|---:|---:|
| `m2_n1` | `0` | `0` | `0` |
| `m2_n2` | `0` | `0` | `0` |
| `m2_n3` | `0` | `0` | `0` |
| `m3_n1` | `1/6` | `1/6` | `0` |
| `m3_n2` | `1/12` | `11/36` | `2/9` |
| `m3_n3` | `5/72` | `91/216` | `19/54` |
| `m4_n1` | `0` | `0` | `0` |
| `m4_n2` | `0` | `0` | `0` |
| `m4_n3` | `0` | `0` | `0` |
| `m5_n1` | `1/10` | `1/10` | `0` |
| `m5_n2` | `3/100` | `19/100` | `4/25` |
| `m5_n3` | `3/200` | `271/1000` | `32/125` |

All even-alphabet cells are error-free. The two odd-alphabet `n=1` cells
exactly reproduce the v0.2 frontier.

## Controls and conclusion layers

All primary gates `G0-G7`, independent gates `V0-V10`, and five frozen metric
probe families passed. The independent mismatch and failure lists are empty.

- **Metric robustness:** message/transcript relabeling, odd-alphabet block
  sensitivity, encoder-class monotonicity, the global-only parity pathology,
  and the per-message-cover blind control all replayed exactly.
- **Task result:** the four registered odd-alphabet block advantages above.
- **Measurement reliability:** exact rational feasibility, MAP scores,
  quotient-remainder optimum, product factorization, controls, source tree,
  and scientific records were independently reconstructed; the result schema
  and bytes were canonicalized and hash-bound.
- **Claim support:** only `m=2..5`, `n=1..3`, uniform finite transcripts,
  equiprobable binary payload words, and exact globally averaged cover.
- **Operational decision:** retain this finite boundary and separately register
  a stronger-cover or active-audit successor.

The global-only parity control has error `1/2` versus blind error `3/4`, while
retaining uniform coordinate marginals. This is a warning that globally
averaged cover is weak. Full per-message transcript cover remains exactly
blind in every registered cell.

## Provenance and resources

- Source freeze: `f27a7baf710c25629212c74713a96b4c781a4463`
- Primary artifact commit: `013af82f671f8008de4ed3ca6841c754a12846ac`
- Independent verification commit: `2221b87d5ae8ff3a31251f0737ad2d8477b3e77f`
- Canonical manifest SHA-256:
  `c29b6fb6642b26ad25326f900c486c792977a7af0416cc279cdcefe5dd920a32`
- Raw manifest SHA-256:
  `49c6cd4a00da73744b0e1d5a9c45941fd1a4aa2cca6c1d5f1b3af8cb9a37447e`
- Primary result SHA-256:
  `fad139727d9fc50c864daf50f8f080acd28e196068c78e8bfbb8d31c9af78d29`
- Verification SHA-256:
  `0ef38697e3e0a910540b07a8dadecfd2eec48787730983c316cc20001d3175d4`

The primary completed `12/12` cells in `0.953 s`, with a peak traced Python
allocation of `504,098` bytes under a `67,108,864`-byte ceiling. Maximum
observed sizes were `1008` dynamic-program state positions, `1000` joint
entries, and `125` transcripts. `tracemalloc` does not measure process RSS or
native-library allocation.

Post-freeze source validation passed `53/53` tests. The primary artifact is
`100,834` canonical JSON bytes; the verification artifact is `9,186` canonical
JSON bytes.

## Claim boundary

The package contains no language, semantic representation, learned encoder,
shared key, shared latent variable, decoder side information, active auditor,
prefix-conditional policy, deployment model, or statistical holdout. It
establishes no square-root law, general tensorization theorem, asymptotic
capacity, operational covert channel, or ASMP-6 resolution. Destination-path
checks harden stable local execution but do not claim resistance to a hostile
concurrent filesystem parent-swap race.
