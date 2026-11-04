# ASMP-9 stochastic experiment v0.37

Version 0.37 converts the v0.36 zero-error correction into an exact
bounded-risk access ledger.

It separates:

1. exact observational fibers;
2. zero-error confusability graphs;
3. connected-component decision quotients;
4. target-only minimax decision risk; and
5. full expanded-parameter directional deficiency.

The comparison-of-experiments mathematics is classical. The bounded
contribution is a preregistered rational census showing where a quotient loses
risk information and where full deficiency prices nuisance distinctions that
the target decision ignores.

## Development and confirmation separation

The burned development grid is `{0,1/2,1}^6`. Its result is explicitly
ineligible for the registered gates.

The confirmation grid is disjoint:

```text
{1/4,1/3,2/3,3/4}^6
```

It contains 4,096 binary-output experiments over three targets and two
nuisance states. Both one-sample and exact-population-law semantics are
reported.

## Prereveal checks

```powershell
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/stochastic_experiment_v0_37/test_experiment.py `
  ultra-experiments/millennium/asmp9_reward_gauge_census/stochastic_experiment_v0_37/test_registered.py `
  -q
```

Do not run `run_registered.py` until the implementation is committed, the
compare-or-fail registration is generated and committed, and that registration
commit is pushed.

## Claim boundary

A pass establishes only the registered finite ledger. It is not a new
Blackwell or Le Cam theorem, not a general nuisance-parameter result, not
reward identification in a real model, and not an ASMP-9 resolution.

