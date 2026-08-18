# ASMP-3 honest-search barrier completion audit v2.1

## Newly closed

```text
zero-or-one unique-marker semantic family = typed
false no-marker transcript in one-marker worlds = typed
replication-quotiented refutation dimension = 1
post-witness verification cost = one semantic query
deterministic exact honest search cost = N=2^n
randomized q-query maximin success = q/N exact
two-thirds success threshold = ceil(2N/3)
n^3 honest-query budget success tends to zero
40 exact resource rows through n=40 = certified
63 finite query-subset strategy spaces = exhausted
30 atom-encoding permutations = certified
OR macro global evaluation cost N = charged
independent-noise checking versus ideal-oracle search = separated
clean-room search/resource checker = passed
```

## Still open

```text
positive honest-search characterization for structured task families = open
time complexity beyond semantic query complexity = open
average-case/distributional honest search = open
advice, preprocessing, and witness-bearing transcript models = open
quantum honest-search interfaces = open
matching communication lower bounds beyond the n-bit index = open
adaptive global verifier optimization = open
WV-ADM interface optimization = open
v0.1 FIX-versus-ADM scope adjudication = open/normative
external mathematical review = absent
```

## Characterization consequence

Combinatorial dimension, verification cost, and honest search are three distinct
quantities.  This harness fixes the first two at one while making the third
exponential in the atom-index length.  Any complete ASMP-3 characterization
must retain an operational honest-search condition or an equivalent invariant.

## Non-overclaim rule

The barrier is black-box and classical.  It does not rule out efficient search
from task structure, side information, advice, preprocessing, quantum access,
or transcripts that already carry the witness.
