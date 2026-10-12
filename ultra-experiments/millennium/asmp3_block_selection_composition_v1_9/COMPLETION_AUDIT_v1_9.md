# ASMP-3 block-selection composition completion audit v1.9

## Newly closed

```text
M fixed semantic atoms with disjoint iid replication blocks = typed
fixed majority decoder per atom = inherited/certified
exact independent joint risk 1-(1-e_d)^M = proved
OR/all-zero tight predicate = proved/certified
truth-aware failed-block selector risk = proved/certified
marginal-only extremal risk min(1,M e_d) = proved
per-atom and global persistent comparisons = exact
selection inflation over one-atom error = quantified
replication depth for exact target joint risk = minimized
union-safe replication depth = minimized
total semantic query cost M*d = charged
744 composition rows = certified
12 raw multi-block response spaces = exhausted
24 depth/target cases = exact
clean-room block/selection/depth checker = passed
```

## Still open

```text
unbounded adaptive candidate/refutation generation = open
stopping-time query allocation and sequential tests = open
conditional independence after arbitrary transcript selection = open
adaptive global verifier optimization beyond fixed majority blocks = open
query-replication encoding invariance = open
honest-prover computation characterization = open
matching communication and honest-prover lower bounds = open
WV-ADM interface optimization = open
v0.1 scope adjudication = open/normative
external mathematical review = absent
```

## Harness-based stopping boundary

Single-atom error cannot be substituted unchanged after selection.  With `M`
selectable independent blocks, the exact selected-failure risk is
`1-(1-e)^M`; with marginals alone it can be `min(1,Me)`.  Any further adaptive
theorem must freeze or bound candidate breadth, charge `M*d` queries, and state
a conditional joint-noise law after the selection history.  Without those
inputs there is no single numerical composition profile to compute.

## Non-overclaim rule

The tight OR/selector harness is one fixed interface and does not establish a
global impossibility for all adaptive protocols.  It proves that a theorem
using only the unselected one-atom marginal profile is insufficient.
