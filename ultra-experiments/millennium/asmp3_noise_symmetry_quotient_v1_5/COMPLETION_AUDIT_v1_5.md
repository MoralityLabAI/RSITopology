# ASMP-3 noise-symmetry quotient completion audit v1.5

## Newly closed

```text
compact finite-state hard-budget controller = exact
coordinate-permutation action and response-language invariance = explicit
verifier symmetrization without worst-case value loss = proved
full response histories modulo S_d = Hamming-weight quotient
quotient controller state (truth,round,flips_used) = certified
closed-form controller and terminal state counts = certified
2b<d / 2b>=d quotient value phase = exact
all d=1,...,32 and b=0,...,d = certified (560 cases)
all deterministic verifier rules for d<=3 = exhaustively audited
all v1.4 d<=6 parent rows = cross-checked (27 cases)
clean-room quotient/formula checker = passed
```

## Still open

```text
position-dependent or weighted noise quotient = open
expected/probabilistic rather than hard budget = open
truth-ignorant and independently constrained noise = open
advocate/noise independence restrictions = open
adaptive verifier query selection = open
general implicit-game tractability = open
honest-prover computation characterization = open
WV-ADM interface optimization = open
v0.1 scope adjudication = open/normative
external mathematical review = absent
```

## Non-overclaim rule

The quotient is exact only because prior, hard budget, payoff, and observation
costs are invariant under every coordinate permutation.  Position-dependent
structure requires a different orbit partition and a new value-preservation
argument.
