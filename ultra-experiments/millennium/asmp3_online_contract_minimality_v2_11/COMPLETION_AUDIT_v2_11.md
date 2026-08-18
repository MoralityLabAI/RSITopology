# ASMP-3 online-contract minimality completion audit v2.11

```text
parent v2.10 one-shot sufficiency = preserved
observation partition rows = 19
ideal-probe frontier rows = 73
trace-without-H rows = 76
sharp path-error rows = 270
premise counterfamilies = 6/6
positive parent compositions = 12/12
decision-only Las Vegas success = 0
trace-only positive-noise Las Vegas success = 0
probe-confirmed success = k/N exactly
trusted-candidate invalid mass = decoy mass exactly
trace-plus-H invalid mass = 0
soundness-zero uncontrolled-path success = 0
path-loss bound attained = 270/270
producer gates = 10/10
clean-room checks = 10/10
claim scope changed = no
```

## Closed in this release

For the registered black-box Las Vegas observation model, all six clauses of
the v2.10 online contract now have necessity evidence as well as sufficiency.
The information frontiers and path-loss bound are exact, not empirical.

The result justifies stopping extensions of the current harness: more marker
counts or rational probability rows cannot repair an empty safe-witness
intersection or change the identities `k/N` and `max(0,1-s-delta)`.

## Remaining boundary

Minimality is not universal across arbitrary task-specific or non-black-box
proofs.  The normative successor choice, interface-uniform resource lower
bounds, broader correlated-noise models, and external review remain open.  Each
requires a new semantic decision, theorem architecture, or external evidence,
not another instance of this harness.
