# Signed-Control Gate Guest Port Contract

## Status

Protocol version: `signed-control-gate-q16.48-v1`

This directory is a deterministic reference layer only. It contains no RISC
Zero proving or receipt-verification code. A future guest must reproduce the
integer operations and byte layouts below exactly.

## Numeric Format

All public fixed-point scalars are signed Q16.48 integers:

```
real_value = encoded_i64 / 2^48
```

Q16.48 is intentional. With Q32.32, flooring a retention in the first
positive bin can move its square root by `sqrt(2^-32) = 2^-16`, so the fixed
decision cannot be guaranteed to match the float decision outside the
required `2^-20` margin. Q16.48 reduces that worst single-edge shift to
`2^-24` while retaining a signed real range of approximately `[-32768,
32768)`, well beyond all scalar gate domains.

Valid gate ranges are:

- retention: `[0, 1]`
- retention uncertainty: `[0, +infinity)`
- canonical angle: `[0, 180]` degrees, or absent when `det_h_flag` is true
- angle uncertainty: `[0, +infinity)` degrees
- error budget: `[0, 2]`

The host must quantize measured values in the conservative direction:

| Field | Quantization |
|---|---|
| retention | floor |
| retention uncertainty | ceil |
| canonical angle | ceil |
| angle uncertainty | ceil |
| error budget | floor |
| attestation margins | floor |

Boolean values are one byte (`0x00` or `0x01`). Every fixed scalar is an
eight-byte two's-complement little-endian `i64`. Lengths and counts are
little-endian `u32`. Strings are `u32 byte_length || UTF-8 bytes`.

## Arithmetic Contract

### Square root

`sqrt_q_floor(x)` computes:

```
floor(sqrt(x * 2^48))
```

using integer Newton iteration. This is the Q16.48 floor of the real square
root. Consequently, `1 - sqrt(retention)` is never smaller than the value
represented by the quantized retention.

### Sine

The half-angle is converted with
`ceil(pi * 2^48) = 884279719003556`. Sine on
`[0, pi/2]` uses:

```
x - x^3/3! + x^5/5! - x^7/7! + x^9/9! - x^11/11!
  + x^13/13! - x^15/15! + x^17/17! - x^19/19!
```

The Q72 coefficient integers, from `x` through `x^19`, are:

```
4722366482869645213696
-787061080478274202283
39353054023913710114
-936977476759850241
13013576066109031
-118305236964628
758366903619
-3611270970
13276732
-38821
```

Horner evaluation uses a Q16.48 rounded square and Q72 accumulators. On the
encoded domain `x < 8/5`, the alternating-series remainder is less than
`(8/5)^21 / 21! < 0.106566` Q16.48 ulp. For `z = x^2 < 13/5`, the
derivative majorant
`sum(k * z^(k-1) / (2k+1)!, k=1..9) < 0.214224`; multiplying by `x < 8/5`
and the half-ulp error in `z` bounds the rounded-square perturbation by
`0.171379` output ulp. Coefficient and Horner operations each round by at most
half a Q72 ulp, so their combined weighted error is bounded by
`(8/5) * sum((13/5)^k, k=0..9) / 2^24 < 0.000842` Q16.48 ulp. Final rounding
is at most `0.5` ulp. Thus the maximum absolute evaluation error is below
`0.106566 + 0.171379 + 0.000842 + 0.5 = 0.778787` ulp. All polynomial
products are below `2^122` in magnitude and fit signed `i128`.

The gate adds one Q16.48 ulp to the sine result, clamps it to one, doubles it,
and clamps chord displacement to two. This correction is part of the protocol,
not an implementation tolerance.

### Risk and authorization

For every edge, compute point and conservative lineage terms:

```
1 - sqrt_floor(retention)
1 - sqrt_floor(max(0, retention - uncertainty))
```

Holonomy is `2 * sin_upper(angle / 2)`. `det_h_flag` pins both holonomy values
to `2`. An unmeasured loop (`audit_gap`) pins the final conservative bound to
`2`. Point and conservative total risks are independently clamped to `2`.

Authorization requires all three:

1. no audit gap;
2. no orientation reversal;
3. conservative signed-control loss `<=` the floor-quantized public budget.

## Canonical Gate Encoding

`canonical_measurement_bytes` writes fields in this exact order:

1. ASCII magic `RSIZKG01` (8 bytes)
2. protocol-version string
3. measurement-ID string
4. edge count (`u32`)
5. for each edge, in supplied order:
   - edge-ID string
   - retention (`i64`)
   - retention uncertainty (`i64`)
6. canonical-angle-present byte
7. canonical angle (`i64`) when present
8. angle uncertainty (`i64`)
9. `det_h_flag` byte
10. `measured` byte

The measurement commitment is SHA-256 over:

```
canonical_measurement_bytes || error_budget_i64_le
```

The budget is published in the signed control request outside the receipt. The
request also publishes the expected commitment, binding that public budget to
the private edge receipts without adding another journal field.

For a valid gate execution, append:

1. error budget (`i64`)
2. status byte `0x01`
3. these Q16.48 outputs as `i64`, in order:
   - lineage contraction point
   - lineage contraction bound
   - holonomy displacement point
   - holonomy displacement bound
   - measurement uncertainty margin
   - point risk score
   - signed-control loss upper bound
   - error budget
   - authorization margin
4. orientation-reversal byte
5. audit-gap byte
6. authorized byte

Rejected conformance inputs append the budget, status `0x00`, error-type
string, and error-message string. A production guest should reject malformed
inputs before committing a decision journal.

## Public Journal

The public journal is exactly:

```
measurement_commitment_hash[32]
|| protocol_version_string
|| decision_u8
|| authorization_margin_i64_le
```

Semantically this is the tuple:

```
(measurement commitment hash, protocol version, decision, authorization margin)
```

The verifier must match the commitment and protocol version against the signed
control request, which separately exposes the error budget.

## Public and Private Values

Public:

- protocol version
- error budget in the signed control request
- expected measurement commitment hash
- decision
- authorization margin

Private guest input:

- measurement ID
- ordered edge IDs
- per-edge retention and uncertainty receipts
- canonical angle and uncertainty
- orientation and measured/audit flags

The journal reveals no individual edge receipt. It necessarily reveals the
decision and signed margin selected by the frozen public budget.

## Attestation Threshold Port

Registry I/O, anchor strings, SHA syntax checks, and path validation remain
outside the guest. The guest-facing threshold helper receives directionally
rounded margins and structural booleans. It uses integer comparisons only:

- negative-control margin must be `> 281` (the encoded strict epsilon);
- lineage margins must be `>= 0`;
- holonomy angle/loss margins must be `>= 0`;
- orientation, loop availability, structural lineage, and hash-validity flags
  gate level transitions;
- authorization compares integer certification levels `0`, `1`, and `2`.

The strict negative-control comparison is encoded as
`margin_q > floor(1e-12 * 2^48)`, where the frozen integer threshold is `281`.
Because the margin is floor-quantized, a float pass very near the threshold
can become a fixed-point denial, never the reverse.

## Canonical Hashing

JSON commitments use UTF-8 encoded `json.dumps` semantics with sorted keys,
compact separators, ASCII escaping, and non-finite numbers forbidden.

Array commitments use the canonical JSON header:

```
{"dtype":"<f8","shape":[...]}
```

followed by newline byte `0x0a` and contiguous little-endian IEEE-754 binary64
payload bytes. The guest receives these bytes; it does not parse or calculate
floating-point values.
