# ASMP-3 weighted-noise subset-sum completion audit v1.6

## Newly closed

```text
positive-integer position-dependent flip costs = typed
weighted terminal score sufficiency = proved
exact overlap criterion S(c) intersect [C-B,B] != empty = proved
matching value-one/value-zero saddles = certified
controller state (truth,round,spent_cost) = exact
pseudo-polynomial d(B+1) state bound = certified
unit-cost reduction to v1.5 = cross-checked (27 cases)
all sorted costs 1..4, depths 1..6, all budgets = certified (2729 cases)
all deterministic rules through depth 3 = score-averaging audited (18436 instances)
equal-depth/total/budget opposite-phase pair = certified
PARTITION weak-NP-completeness boundary = reduced
2^32 distinct-score noncompression witness = certified arithmetically
clean-room weighted-language checker = passed
```

## Still open

```text
stochastic or expected flip-cost budgets = open
signed, real-valued, or path-observed costs = open
truth-ignorant and independently constrained noise = open
advocate/noise independence restrictions = open
adaptive verifier query selection = open
general implicit-game tractability = obstructed by PARTITION, not characterized
honest-prover computation characterization = open
matching communication and honest-prover lower bounds = open
WV-ADM interface optimization = open
v0.1 scope adjudication = open/normative
external mathematical review = absent
```

## Convincing local stopping boundary

For binary-encoded positive integer costs, exact weighted overlap already
contains PARTITION and the weighted-score quotient can have `2^d` states.
Polynomial-size explicit score enumeration cannot be demanded without extra
structure (bounded unary budget, repeated cost classes, or approximation), and
a general exact polynomial-time phase decision would imply `P=NP`.  A different
compact symbolic representation may still exist for particular instances.
This is a proved harness boundary, not merely a failed search.

## Non-overclaim rule

Weak NP-completeness obstructs a general exact strongly-polynomial algorithm;
it does not rule out pseudo-polynomial dynamic programming, approximation, or
polynomial algorithms for structured cost families.
