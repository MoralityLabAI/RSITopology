# ASMP-3 authority handoff v2.18

The mathematical block is now isolated to one normative scope decision.  No
additional experiment on the sealed v0.1 source can supply it.

| Authorized choice | Quantifier order | Immediate effect |
|---|---|---|
| `FIX` | `forall frozen G, exists Pi inside G` | The v0.7 parity witness is a negative-resolution candidate for displayed sufficiency. |
| `ADM` | `exists G in Interfaces(E), exists Pi inside G` | The vector interface defeats that parity counterexample; the admissible interface class must be specified. |
| Publish both | pose `WV-FIX` and `WV-ADM` separately | Removes ambiguity without pretending the two targets are one iff. |

Suggested minimal authoritative language for `FIX`:

> The entire game interface, including transcript encoding and atomic query
> language, is fixed before verifier and prover algorithms are quantified.  A
> protocol may not select or enlarge that interface.

Suggested minimal authoritative language for `ADM`:

> For a frozen environment and declared class `Interfaces(E)`, protocol
> admission may select one interface `G` from that class.  Every component of
> the selected game is then frozen, and interface selection/serialization costs
> count toward the protocol resources.

Do not add both clauses: the mutation harness correctly leaves no surviving
completion.  The typed successor draft already supplies the fuller definitions
needed for a future version.
