# ASMP-2 v0.2.1 amendment claim packet

This amendment makes no scientific change to [the v0.2 claim packet](CLAIM_PACKET.md). It replaces repeated singular-value decompositions with the identity

```text
P_ker(A ∪ {v}) = P_ker(A) - rr^T/(r^T r),
r = P_ker(A)v,
```

when `r^T r` exceeds the frozen numerical rank tolerance; otherwise the projector is unchanged. The identity is checked against exact-rational deterministic witnesses inherited from v0.2.

The runner and verifier choose different subset parents, so agreement of their complete census digests tests path-dependent numerical drift. The evidence labels and every scientific threshold remain those of v0.2.

