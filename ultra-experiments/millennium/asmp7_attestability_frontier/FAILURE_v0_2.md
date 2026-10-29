# ASMP-7 boundary-degradation v0.2 execution failure

The registered v0.2 run was attempted once after registration commit
`12ef776b1ccf5c060968c5b3dfc3f4cc3e173340`.

It stopped before writing `result.json`, `frontier.csv`, or `receipt.json`.
While converting an exact `Fraction` cutoff certificate to a decimal string,
CPython raised:

```text
ValueError: Exceeds the limit (4300 digits) for integer string conversion
```

The run therefore produced no scientific outcome. The failure was in receipt
serialization after computation, not in a registered scientific gate. V0.2
remains immutable. Any repair requires a separately registered successor and a
fresh output directory.

