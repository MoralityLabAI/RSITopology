# ASMP-3 canonical admissibility audit v2.21

## Construction-to-source map

| Frozen source field | Reduction construction | Status |
|---|---|---|
| Decision relation `R_d` | `b=parity(z)` | Preserved |
| Message order | Simultaneous labelled vectors, then query/decision | Preserved |
| Stopping | One response in the positive witness; arbitrary stopping allowed in the inactive converse | Preserved |
| Atom language | Coordinate atoms `a_i` | Preserved |
| Atom size/locality | `ceil(log2 d)`-bit index, one-coordinate radius | Preserved |
| Ideal oracle | `z_i` before bounded halting; zero afterward | Preserved |
| Complete noise law | Exactly one `BSC(1/5)` response in `G_vec` | Preserved |
| Prover budget | `T(d)=2^(d+4)` | Preserved |
| Zero-sum payoff | Select correct versus false claim label | Preserved |
| Verifier resources | `O(d)` time, one query, `2d+ceil(log2 d)+1` transcript bits | `polylog(T)` |
| Transcript encoding | Canonical labels, vectors, coordinate, response | Frozen |
| Honest efficiency | Send `z` in `O(d)` time | Preserved |
| Decidable `Refute` | Active coordinate mismatch; no inactive refuting set | Preserved; v0.1 expressly permits infinity |
| Full-answer firewall | Each coordinate value occurs in both parity classes for `d>=2` | Passed |
| Positive liveness | Nonhalting machine gives every depth gap `3/5` | Passed |
| Negative liveness | Halting machine gives opposite-answer worlds with identical semantic access | Passed |

## Information boundary

Both claim-labelled advocates observe the semantic world. The verifier observes
the public input, protocol transcript, declared coins, and noisy semantic
responses, but not the world directly. This is the information structure used
by the existing v0.7 parity construction and typed successor.

The inactive-interface converse is uniform over every protocol that retains
this boundary. A protocol-selected message format, longer transcript, or more
rounds does not create trusted information. A direct world-dependent verifier
input would change `InfoV` and the semantic environment.

## Full-domain versus subclass audit

For an adequate encoding `D`, the decision target is all valid encoded
families. The reduction compiler produces valid members of that domain. The
proof assumes a hypothetical decider for the full domain and invokes it only on
compiler outputs. Therefore the result is an undecidability proof for the full
set, even though a structured reduction image supplies the witnesses.

Calling this “only a theorem about the reduction subclass” would incorrectly
reject the standard form of a many-one undecidability proof.

For the ADM reading, the effective compiler wraps the same environment in a
declared singleton interface class `{G_vec}` or a broader class containing it.
The wrapper is part of the valid full ADM description domain. The universal
inactive coupling supplies the converse uniformly over every selected
semantic-respecting interface.
