# ASMP-9 strategic elicitation capacity v0.65

Status: **unregistered theorem development; not claim eligible**.

This lane studies a strategic demonstrator rather than a noisy but passive
response channel.

The development grammar has:

- one agent with a finite strict preference type;
- a common message or complete-strategy space;
- a deterministic final outcome;
- utility depending only on that outcome;
- no payments, audits, verification, or type-dependent side consequences; and
- a requirement that the identifying truthful strategy be the unique best
  response.

Every interactive protocol in this grammar reduces to an outcome menu over
complete strategies.  Exact incentive-identification is therefore possible
only for a subset of types admitting distinct assigned outcomes, each of which
is its assigned type's favorite among all assigned outcomes.

For the full domain of strict rankings over `n` alternatives, the maximum
strictly identifiable subset has size `n`, while the domain has size `n!`.
Thus full strict identification is impossible for every `n>=3`.

The deterministic endpoint is not universal.  If a complete report is sealed
before a random outcome pair is drawn, and the reported winner of that pair is
awarded, every full ranking is strictly elicited under expected utility
exactly when all `C(n,2)` pairs have positive probability.  Omitting any pair
admits a zero-regret adjacent-swap witness.  Under unit-range utilities with
adjacent gaps at least `delta`, uniform pair sampling gives the sharp worst
false-report margin `delta/C(n,2)`.  Revealing the pair before the report
instead leaves `n!/2` rankings behaviorally equivalent.

That positive mechanism is explicit prior art in Azrieli, Chambers, and Healy
(2021), *Constrained Preference Elicitation*.  This package records an exact
ASMP-9 access ledger and finite checks; it makes no novelty claim and remains
unregistered.

Files:

- [theorem draft](THEOREM_DRAFT_v0_65.md);
- [prior-art gate](PRIOR_ART_GATE_v0_65.md);
- [development result](DEVELOPMENT_RESULT_v0_65.md);
- [registration decision](REGISTRATION_DECISION_v0_65.md); and
- [machine-readable verification](DEVELOPMENT_VERIFICATION_v0_65.json).

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/strategic_elicitation_capacity_v0_65/test_strategic_elicitation_capacity.py `
  -q -p no:cacheprovider

python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/strategic_elicitation_capacity_v0_65/verify_development.py
```
