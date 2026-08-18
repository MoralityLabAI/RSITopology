# ASMP-9 target-recovery/interface distinction v0.76

Status: **additive terminological correction using classical factorization**.

## Two questions previously collapsed

Let `X` be a finite parameter registry, let

```text
T : X -> Z
```

be the registered decision target, and let

```text
O : X -> Y
```

be the registered observation.

There are two different scientific requirements:

1. **target recoverability:** can the target be decoded from the observation?
2. **representative insensitivity:** does the observation itself depend only
   on the target?

They are opposite factorization directions.

## Theorem 1: target recoverability

There exists a decoder on the observed image,

```text
d : O(X) -> Z
```

such that

```text
T = d o O
```

iff:

```text
O(x)=O(x') implies T(x)=T(x').
```

Equivalently, every observation fiber lies inside one target fiber. The
decoder sends each observed value to the unique target value on its fiber.

An observation may therefore distinguish multiple representatives of the same
target and still recover the target exactly.

## Theorem 2: representative-insensitive encoding

There exists an encoder

```text
e : T(X) -> Y
```

such that

```text
O = e o T
```

iff:

```text
T(x)=T(x') implies O(x)=O(x').
```

Equivalently, every target fiber lies inside one observation fiber. This is the
condition that no representative-specific information leaks into the
observation.

## Corollary: exact target interface

The target and observation partitions are equal iff both factorizations hold.
The four possible states are:

| Target recoverable | Representative-insensitive | Status |
|---|---|---|
| yes | yes | `exact_target_interface` |
| yes | no | `recoverable_with_representative_leakage` |
| no | yes | `underidentified` |
| no | no | `cross_cut_misspecified_interface` |

This is a total diagnostic. “Leakage” is not automatically
underidentification; it is a separate interface property.

## Linear quotient translation

Let the target be `R/G`, and let the raw nuisance-quotiented linear channel be

```text
C = pi_N o A,   H = ker(C).
```

Then:

```text
target recoverable          iff H <= G;
representative-insensitive  iff G <= H;
exact target interface      iff H = G.
```

Version v0.69 deliberately forced representative insensitivity by additionally
quotienting the output by `A(G)`. Its resulting kernel necessarily contains
`G`, and equality is then the exact-interface condition. Version v0.76 records
that a raw channel with `H` strictly contained in `G` still recovers the reward
quotient, although it also reveals the representative.

Thus the v0.69 mathematics remains correct, but “identifies the quotient”
should be qualified:

```text
v0.69: representative-insensitive exact interface;
v0.76: decoder-based target recoverability, with leakage reported separately.
```

## Exact controls

For target fibers `{0,1}` and `{2,3}`, the verifier realizes all four cells:

1. observation fibers `{0,1}`, `{2,3}`: exact;
2. four singleton observation fibers: recoverable with leakage;
3. one constant observation fiber: underidentified but insensitive; and
4. crossed fibers `{0,2}`, `{1,3}`: both underidentified and leaky.

The receipt includes explicit pair witnesses and decoder/encoder maps whenever
the relevant factorization exists.

## ASMP-9 consequence

The canonical problem should state which of these it requires:

- If the safety goal is to estimate a decision target, decoder-based
  recoverability is sufficient and representative leakage is an additional
  privacy/governance concern.
- If the safety goal is a portable, target-only certificate whose bytes do not
  encode a gauge choice, representative insensitivity is also required.
- If “observational equivalence exactly equals gauge equivalence” is the frozen
  statement, equality of partitions is the correct stronger target.

Failing to distinguish these can reject an informative channel merely because
it contains extra representative information, or certify an invariant channel
that is too coarse to recover the target.

## Claim boundary

This is elementary factorization through finite partitions. It does not
validate a reward target, gauge, physical observation, response model, or
human/model value object. ASMP-9 remains unresolved.
