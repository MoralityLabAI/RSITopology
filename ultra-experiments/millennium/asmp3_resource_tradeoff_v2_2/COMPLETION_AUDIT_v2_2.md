# ASMP-3 resource-tradeoff completion audit v2.2

## Newly closed

```text
one-message message-indexed q-query interface = typed
perfect completeness and zero-input soundness = explicit
message/query covering lower bound Kq>=N = proved
minimum message count ceil(N/q) = exact
minimum communication bits ceil(log2 ceil(N/q)) = exact
partition protocol attaining every frontier point = constructive
communication capacity condition 2^b q>=N = exact
one-query and full-recomputation endpoints = exact
honest Find cost N retained separately from message/Check = exact
433 large frontier points = certified
35 small set-cover frontiers = exhaustively minimized
four robust noisy-query operating points = composed
clean-room cover/frontier/noise checker = passed
```

## Still open

```text
interactive communication/query tradeoffs = open
bounded-error and shared-randomness lower bounds = open
adaptive/variable-length verifier query allocation = open
structured atom geometries and advice = open
universal matching lower bounds across WV-FIX = open
honest-search positive characterization = open
WV-ADM interface infimum and attainment = open
v0.1 FIX-versus-ADM scope adjudication = open/normative
external mathematical review = absent
```

## Resource-obligation status

Matching honest-search, communication, and verifier-query bounds are closed for
the declared unique-marker one-message family.  This is a genuine structured
family theorem, but the canonical ASMP-3 obligation asks for bounds matching a
complete class characterization; that universal step remains open.

## Non-overclaim rule

The covering frontier does not automatically extend to interaction, bounded
error, randomness, adaptive queries, or structured side information.
