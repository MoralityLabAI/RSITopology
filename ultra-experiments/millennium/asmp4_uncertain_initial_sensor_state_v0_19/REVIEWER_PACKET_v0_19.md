# Reviewer packet v0.19

## Claim to attack

For a registered adversarial initial set `I`, the v0.18 theorem holds with
start belief `B_0=I`, exact raw language `L_T(I)`, and observer matrix `A_I`.
The two-state deterministic census has feasibility counts `80,80,32` across
the three nonempty initial sets.

## Highest-value falsification attempts

1. Find an execution in which the earliest mixed start-belief transition does
   not produce the two disjoint safe-control intervals used by necessity.
2. Find a counterexample to downward feasibility monotonicity or raw-language
   inclusion under `I subseteq J`.
3. Produce a transition table contradicting the 768-pair signature histogram.
4. Show that the synchronizing fixture's `2^(T+1)` language has a rate other
   than one raw bit per step, or that the union-dominant fixture is not `4^T`.
5. Identify an uncharged path by which the controller learns the actual initial
   state before the first safety-critical write.

## Load-bearing registrations

- the actual initial sensor state is adversarial within a known nonempty set;
- safety begins immediately, with no free calibration prefix;
- raw words and normal cells are separately injective;
- the normal symbol cannot encode initial state, mode, or event; and
- support-zero-error safety quantifies every initial state and supported path.

A probabilistic prior or a separately charged calibration phase is a successor
contract, not a falsification of this claim.
