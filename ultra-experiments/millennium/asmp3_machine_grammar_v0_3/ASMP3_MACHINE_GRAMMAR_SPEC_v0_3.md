# ASMP-3 machine grammar specification v0.3

## 1. Status and authority

```text
problem_id = ASMP-3
successor_id = ASMP-3-MACHINE-v0.3
document_status = nonnormative successor proposal
typed_parent = ASMP3_TYPED_SUCCESSOR_DRAFT_v0.2
parent_amended = false
```

This document closes the byte-level, program-level, and quantifier-level
objects needed to ask an executable uniform membership question. It becomes
normative only if `ASMP-3-MACHINE-v0.3` is adopted. It does not silently alter
`ASMP-CANDIDATE-SET-v0.1`.

The machine-readable registry is
`asmp3_machine_grammar_v0_3.json`. The Python implementation is a reference
codec, parser, structural/type validator, WV-IR evaluator, `U_TM_v1` bounded
simulator, and compiler for the v2.21 reduction.

## 2. Canonical instance bytes

An instance is exactly one `ASMP3-CANONICAL-JSON-v0.3` object. Its bytes are:

```text
UTF-8(JSON(value,
          ensure_ascii=true,
          keys=lexicographically sorted,
          separators=(",", ":")))
```

The following are invalid:

- a UTF-8 BOM;
- duplicate object keys;
- floating-point numbers, `NaN`, or infinities;
- negative integers;
- unknown fields;
- non-coprime rationals;
- whitespace, trailing newline, or any trailing byte;
- unsorted program or interface tables;
- aliases or padding in transcript serialization.

Rationals have exactly `{"num":p,"den":q}` with `p>=0`, `q>0`, and
`gcd(p,q)=1`. Identifiers match `[A-Z][A-Z0-9_]{0,63}`. Family identifiers use
lowercase letters, digits, and hyphens.

The top-level object has exactly:

```text
schema_version
problem_id
problem_version
codec
universal_machine
membership_semantics
family_id
interface_mode
scale
programs
environment
interfaces
fixed_interface
admissible_interfaces
provenance
```

Constants are:

```text
schema_version       = asmp3_machine_instance_v0_3
problem_id           = ASMP-3
problem_version      = ASMP-3-MACHINE-v0.3
codec                = ASMP3-CANONICAL-JSON-v0.3
universal_machine    = WV-IR-v0.3
membership_semantics = WV-MEMBERSHIP-v0.3
scale.parameter      = n
scale.minimum        >= 2
```

## 3. Typed component graph

`programs` is a nonempty list sorted by unique program ID. Every environment
and interface field references a program with the exact registered signature.
The 23 signatures in the JSON registry cover:

- public-instance, semantic-world, and output validators;
- the decision relation;
- atom validity, description, locality, and evaluation bounds;
- replication validity and equivalence;
- ideal oracle and complete noise-process objects;
- prover and verifier information projections;
- prover budget;
- message validity, order, stopping, malformed behavior, payoff, and `Refute`;
- verifier-time, semantic-query, and transcript bounds.

Unknown references, duplicate IDs, signature coercions, and missing components
are invalid. Static validity does not assert that an arbitrary submitted
program is total or meets its claimed resource bound; failure, divergence, and
out-of-gas have the total semantics below.

## 4. WV-IR-v0.3 programs

A program is either:

```text
IR program:
  {id, kind="ir", inputs, output, registers, instructions}

registered component builtin:
  {id, kind="builtin", inputs, output, builtin, params}
```

Protocol algorithms quantified by membership are finite IR programs. Builtins
are frozen environment/interface component definitions; they are not hidden
instructions callable by a protocol.

Value types are `bit`, `nat`, `bytes`, `rational`, and `json`. Input arguments
occupy the initial registers. Remaining registers start at typed zero:

```text
bit=0
nat=0
bytes=empty
rational=0/1
json=null
```

The 25 opcodes are:

```text
const_bit const_nat const_bytes const_rational const_json
copy eq lt add sub_sat mul pow2
length parity bytes_to_nat get_bit concat slice
json_encode json_decode bounded_halts
jump branch return fault
```

Control-flow targets are zero-based instruction indices and must be in range.
Every program contains at least one correctly typed `return`; reachability and
termination remain semantic properties.

### 4.1 Exact value operations

- `nat` operations are on unbounded nonnegative integers; `sub_sat(a,b)` is
  `max(0,a-b)`.
- `bytes_to_nat` is unsigned big-endian; empty bytes encode zero.
- `get_bit` index zero is the least-significant bit of the final byte and
  returns zero outside the byte string.
- `length` counts bytes; `slice` uses byte offsets and truncates at the end.
- `parity` is the XOR of every bit in the byte string.
- JSON encode/decode accepts only canonical JSON-value bytes under section 2.
- A failed JSON decode, invalid runtime type, overflow/resource exception, or
  invalid machine operation returns `FAULT`.

The register/arithmetic/branch core is Minsky-complete, so arbitrary computable
component and protocol functions have finite encodings without granting an
opaque host-language escape.

### 4.2 Gas

Define bit size:

```text
size(bit)      = 1
size(nat x)    = max(1, bit_length(x))
size(bytes x)  = max(1, 8*len(x))
size(p/q)      = max(1,bit_length(p)) + max(1,bit_length(q))
size(json x)   = max(1, 8*len(canonical_json(x)))
```

An instruction costs:

```text
1 + sum(size(read register values))
  + sum(size(values written or allocated))
  + bounded_halts_extra
```

`jump` costs one. `branch` and `return` read their operand. `fault` costs one.
Constants charge their written value. Gas is checked before register mutation
or terminal return; insufficient fuel returns `FAULT/OUT_OF_GAS` with the
previously consumed gas. Every loop dispatch therefore costs at least one.

`bounded_halts_extra` is the exact decode/input/transition gas returned by the
reference `U_TM_v1` simulator, so bounded universal simulation is not a
constant-cost primitive.

## 5. U_TM_v1 numbering

A machine index is converted to its minimal unsigned big-endian bytes; zero is
empty. Valid bytes are:

```text
0xA3
ULEB128(state_count >= 1)
ULEB128(start_state < state_count)
for q=0..state_count-1, symbol=0,1,#,_:
    ULEB128(next_state_plus_one)  # zero means HALT
    action_byte
```

In `action_byte`, bits 0--1 are the written symbol and bits 2--3 are movement
`0=left, 1=stay, 2=right`; higher bits must be zero. ULEB128 must be minimal.
Targets must be in range and no trailing byte is allowed. Invalid encodings
halt at step zero, which makes the numbering total.

Input bytes are expanded most-significant bit first as tape symbols 0/1,
followed by `#`; other cells are blank. The head starts at the first input bit.
A transition writes, moves, and then either enters its target state or halts.
`bounded_halts(e,x,s)` is true exactly when the code is invalid or the machine
halts within at most `s` transitions.

This is an effective enumeration of deterministic single-tape Turing machines.
A compiler from any other acceptable numbering translates its finite transition
table to `U_TM_v1`; it need not preserve the source numeric index.

## 6. Environment and interface modes

`environment` contains exactly the typed fields listed in section 3. Noise is
a history-conditional rational transition kernel accepted by a decidable
`noise_legal` component. Membership quantifies over every accepted kernel after
every history, so independence is never inferred from marginal error alone.

Every interface fixes canonical serialization and references all game-machine
components. In `FIX`:

```text
fixed_interface = one listed interface ID
admissible_interfaces = null
```

In `ADM` v0.3:

```text
fixed_interface = null
admissible_interfaces = {
  "kind":"finite",
  "interface_ids":[nonempty sorted unique listed IDs]
}
```

The ADM choice is made uniformly before the hidden world and execution coins.
V0.3 intentionally admits finite catalogs only. A generated infinite catalog
requires a later version with a recursive interface-output type and its own
resource accounting.

## 7. WV-MEMBERSHIP-v0.3

The decision input is the canonical byte string of one valid uniform family.
Invalid bytes are outside the class.

Membership means there exist finite uniform IR programs for the honest role(s)
and verifier, rational `c>0`, and integer `N`, such that for every `n>=N`:

1. honest execution uses at most `T(n)` gas;
2. verifier time, semantic queries, and transcript bits are bounded by
   `C*ceil(log2(T(n)+2))^k` for some fixed integers `C,k`;
3. completeness minus soundness is at least `c` against every adversarial role
   strategy using at most `T(n)` gas;
4. the bound holds under every legal history-conditional noise kernel; and
5. all malformed, fault, and abort outcomes use the frozen interface behavior.

Completeness and soundness are evaluated from the frozen payoff after swapping
claim labels as required: a strategy must support every valid truthful claim,
and the converse quantifies over every false claim and legal obfuscating
strategy. `FIX` freezes its interface before the existential protocol programs.
`ADM` additionally existentially chooses one listed interface uniformly before
the hidden world.

## 8. Version and resolution consequence

The reference compiler maps every `U_TM_v1` index into valid FIX and singleton
ADM instances containing the v2.21 parity/vector construction. Consequently:

```text
compiled instance is in WV-MEMBERSHIP-v0.3
iff the indexed machine never halts.
```

Thus adopting this grammar does not reopen the unrestricted classification:
it makes the v2.21 undecidability result a literal theorem about the successor's
machine-defined full membership set.

## 9. Claim boundary

The parser can prove byte validity, type closure, reference integrity, and
canonical representation. It cannot decide semantic totality or uniform class
membership; the latter is exactly the undecidable property. Adoption of the
successor and external expert reproduction remain non-machine obligations.
