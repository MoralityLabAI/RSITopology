# ASMP-9 v0.49 common-ordering theorem development

This additive development branch turns the v0.48 prospective null into a
finite structural question.

Version v0.48 showed both possibilities inside one exact Buehler grammar:

- a burned fixture with disjoint decision-optimal ordering sets; and
- a disjoint confirmation fixture where every four-class optimum was also
  root-group optimal.

The next object is therefore not another favorable parameter grid. It is the
intersection of the two tight-predecessor DAGs on the outcome subset lattice.
The development theorem gives:

1. an exact necessary-and-sufficient common-chain certificate;
2. a finite cut certificate when no common optimum exists; and
3. an ordering-gauge sufficient condition under which two set-bound
   objectives have exactly the same optimizer set.

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest -q -p no:cacheprovider `
  ultra-experiments/millennium/asmp9_reward_gauge_census/common_ordering_v0_49/test_common_ordering.py
```

This directory is theorem development, not a prospective registration or a
claim that ASMP-9 is resolved.
