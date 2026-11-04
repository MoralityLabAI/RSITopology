# ASMP-3 v0.3 registered builtin semantics

## Common encodings

At scale `n>=2`:

- a world is exactly `ceil(n/8)` bytes; unused high bits in the first byte are
  zero;
- a binary output is one byte, `00` or `01`;
- a coordinate atom is the minimal unsigned big-endian byte encoding of
  `i<n`, with zero encoded as empty bytes;
- a vector message uses the world encoding;
- roles are natural numbers zero and one;
- the v2.21 machine is run on empty input for at most `n` transitions.

The vector-interface history is canonical JSON containing ordered events:

```text
message(role=0, body=uppercase hex)
message(role=1, body=uppercase hex)
query(atom=uppercase hex)
response(bit=0|1)
decision(role=0|1)
```

No optional event field, padding, or alias is legal.

## Environment builtins

| Builtin | Exact semantics |
|---|---|
| `PUBLIC_BYTES_VALID_V1` | Accept every byte string. |
| `WORLD_D_BITS_VALID_V1` | Accept exactly the canonical `n`-bit world encoding above. |
| `OUTPUT_BIT_VALID_V1` | Accept exactly `00` or `01`. |
| `PARITY_RELATION_V1` | True iff the output bit equals XOR of the world's `n` bits. |
| `ATOM_COORDINATE_VALID_V1` | True iff the atom is the minimal encoding of an integer below `n`. |
| `ATOM_COORDINATE_BOUND_V1` | Return `max(1,ceil(log2(n)))`. |
| `ATOM_COORDINATE_LOCALITY_V1` | Return one. |
| `ATOM_COORDINATE_COST_V1(e)` | Return the reference gas actually used by `bounded_halts(e,empty,n)` plus the bit-cost of parsing and reading one coordinate. |
| `IDENTITY_REPLICATION_VALID_V1` | True exactly for metadata `null` and a replica byte-equal to the atom. |
| `IDENTITY_REPLICATION_EQUIVALENT_V1` | Byte equality. |
| `V2_21_IDEAL_ORACLE_V1(e)` | Return world bit `i` if `e` has not halted within `n` steps; otherwise return zero. |
| `NOISE_EXACT_BSC_LEGAL_V1` | Accept exactly the kernel emitted by `BSC_ONE_FIFTH_KERNEL_V1`, with no history- or world-dependent extra field. |
| `BSC_ONE_FIFTH_KERNEL_V1` | Given history containing the ideal bit, emit that bit with probability `4/5` and its complement with probability `1/5`. |
| `PROVER_FULL_WORLD_VIEW_V1` | Return canonical concatenation of public instance, world, and role tag. |
| `VERIFIER_PUBLIC_VIEW_V1` | Return the public instance only. |
| `WV_PROVER_EXP_BUDGET_V1` | Return `2^(n+4)`. |

The noise kernel has exactly:

```json
{"outcomes":[{"bit":0,"p":{"den":5,"num":4}},{"bit":1,"p":{"den":5,"num":1}}]}
```

when the ideal bit is zero, with probabilities swapped when it is one. Outcome
order is by bit. The history supplies no trusted world field.

## Interface builtins

| Builtin | Exact semantics |
|---|---|
| `VECTOR_MESSAGE_VALID_V1` | At round zero, role `b` submits one canonical `n`-bit vector of parity `b`; no later prover message is valid. |
| `VECTOR_ORDER_V1` | Require the two labelled messages, then have the verifier select one coordinate, obtain one noisy response, and emit a decision role. |
| `SINGLE_RESPONSE_STOP_V1` | True exactly after a terminal decision or frozen malformed outcome. |
| `WV_LINEAR_TIME_BOUND_V1` | Return `8n+16`. |
| `WV_LINEAR_QUERY_BOUND_V1` | Return one. |
| `WV_LINEAR_TRANSCRIPT_BOUND_V1` | Return `2n+ceil(log2(n))+1`. |
| `MALFORMED_LOSES_V1` | A malformed acting claimant loses; malformed verifier behavior is a verifier fault and loses completeness. |
| `CLAIM_SELECTION_PAYOFF_V1` | Return `1/1` iff the terminal decision role's label equals parity of the world, otherwise `0/1`. The opposing zero-sum payoff is one minus this value. |
| `COORDINATE_REFUTE_V1(e)` | If `e` is still active at `n`, accept exactly one canonical coordinate and ideal-answer bit that disagrees with the target claimant vector there; if `e` has halted, accept no refuting set. |

The `Refute` definition uses ideal answers, never the noisy response. Its halted
branch is empty so a world-independent zero oracle cannot refute a truthful
vector containing a one.

## Builtin privilege boundary

These names are frozen macros for the supplied environment/interface. They are
not instructions available to quantified protocol programs. A new builtin or a
changed semantic table requires a new grammar version and changes provenance
hashes.
