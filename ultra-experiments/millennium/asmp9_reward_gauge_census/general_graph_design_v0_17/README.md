# ASMP-9 general comparison-graph design v0.17

This directory develops the first post-v0.16 target: exact unconditional
availability of the full conditional reward quotient on graphs with more
than one independent cycle, and fixed-total trial allocation for that event.

The burned development census motivated a prospective v0.17 protocol. Its
fresh cells have not been executed. The questions are:

1. can fiber-rank liveness be computed from a three-state residual network;
2. does balanced edge allocation remain maximin on multi-cycle graphs; and
3. if not, what graph object controls the optimal allocation?

The implementation uses exact rational arithmetic, direct conditional-fiber
enumeration, a separate transitive-closure verifier, and a CPU-only resource
cap. `PROTOCOL_v0_17.md` is the human-readable specification;
`protocol_v0_17.json` is the machine-readable gate registry. No result becomes
claim-eligible until the implementation is committed, separately registered,
executed at the registration commit, and independently replayed.
