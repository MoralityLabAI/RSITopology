# ASMP-9 bounded context-degree development v0.57

This development lane asks the next question left open by the v0.56
unrestricted-completion theorem:

> Which non-circular cross-menu restriction lets a proper menu domain identify
> the full stochastic-choice kernel and therefore its Luce/RUM/non-RUM tier?

The candidate restriction bounds the Boolean Mobius degree of every observable
pairwise log-odds function as the rest of the menu changes. This is a
Batsell-Polking-style contextual-choice hierarchy, not a new model class.

The candidate exact result is:

```text
degree at most r + all menus through size r+2
    -> constructive recovery of the full positive choice kernel

all menus only through size r+1
    -> insufficient, even to distinguish Luce from non-RUM, for r >= 1
```

The lower witness works for every fixed universe size `n >= r+2`; it is not
limited to the boundary case `n=r+2`.

The draft also derives the exact deterministic interpolation condition number
for extrapolating pairwise log odds to larger menus. It does not convert that
number into an unregistered finite-sample tier claim.

Files:

- `PRIOR_ART_GATE_v0_57.md`: classical-context-model attribution and residual
  claim boundary.
- `THEOREM_DRAFT_v0_57.md`: definitions, reconstruction proof, and fixed-`n`
  sharpness construction.
- `DEVELOPMENT_RESULT_v0_57.md`: current proof, verification, conditioning,
  and freeze decision.
- `bounded_context_degree.py`: exact rational/formal-log-odds implementation.
- `test_bounded_context_degree.py`: development tests over disjoint finite
  universes and interaction orders.
- `verify_development.py`: independent finite audit that does not import the
  implementation module and does not write an artifact.

Development tests:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest -p no:cacheprovider `
  ultra-experiments/millennium/asmp9_reward_gauge_census/bounded_context_degree_v0_57/test_bounded_context_degree.py `
  -q

python ultra-experiments/millennium/asmp9_reward_gauge_census/bounded_context_degree_v0_57/verify_development.py
```

This directory is unregistered development work. It must not be described as a
claim-eligible theorem until the proof, prior-art boundary, verifier, and
registration are independently reviewed and frozen.
