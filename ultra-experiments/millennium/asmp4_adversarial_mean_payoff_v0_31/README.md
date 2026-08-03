# ASMP-4 adversarial mean-payoff region v0.31

This package computes the complete additive two-port region of any supplied
finite exact alternating quotient. For each memoryless adversary policy, take
the union of reachable SCC cycle-mean polytopes; then intersect those
fixed-policy regions over all adversary policies.

The result closes the nondeterministic finite-quotient seam left open in v0.26.
It also preserves two essential boundaries: irreversible SCC choices remain a
nonconvex union, and exact controller play may need infinite memory even though
finite-memory strategies approximate every winning budget.

Evidence includes 2,304 central exact budget decisions across 256 games and
1,296 independent decisions across 81 games. Every losing census instance has
a validated memoryless spoiler. The connector fixture checks the exact
`1/(k+1)` finite-period slack to the unattained finite-memory boundary.

Run:

```powershell
python run_verification.py
python verify_adversarial_mean_payoff.py
python -m pytest -q
python -m ruff check .
```

The classical multi-mean-payoff results are credited in
`PRIOR_ART_BOUNDARY_v0_31.md`; no graph-game novelty is claimed.

The v0.32 successor audit seals this result as the final finite/additive layer
of the current chain and moves the remaining work upstream to the missing
global class and abstraction/replacement theorem.
