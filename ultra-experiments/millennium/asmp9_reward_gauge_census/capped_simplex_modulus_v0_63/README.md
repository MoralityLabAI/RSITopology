# ASMP-9 capped-simplex modulus v0.63

Status: **unregistered development lane; not claim eligible**.

This lane strengthens the one-dimensional v0.62 calibration slice to the full
two-dimensional stochastic-choice simplex compatible with one fixed set of
binary choice probabilities.

The fixed binary menus are

```text
p(a|ab)=2/5,
p(a|ac)=3/5,
p(b|bc)=3/5.
```

Writing the full-menu law as `x=(x_a,x_b,x_c)`, stochastic
rationalizability is exactly the capped simplex

```text
P = {x in Delta_3 : x_a<=2/5, x_b<=3/5, x_c<=2/5}.
```

For a full-menu law `q`, define its total regularity-violation mass

```text
V(q)
  = (q_a-2/5)_+ + (q_b-3/5)_+ + (q_c-2/5)_+.
```

The development theorem proves:

```text
dist_TV(q,P) = V(q),

Delta(P,N_gamma) = gamma,

Lambda(P,N_gamma) = 1+(5/2)gamma,
```

where `N_gamma={q: V(q)>=gamma}`, all probabilities are at least `1/10`,
and `0<gamma<=1/50`.

Unlike v0.62, both tier fibers are polygonal regions rather than line
segments.  The multiplicative proof enumerates every possible violated-facet
support and identifies a single `2/5` cap as the active optimum.

Run the development checks with:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest `
  ultra-experiments/millennium/asmp9_reward_gauge_census/capped_simplex_modulus_v0_63/test_capped_simplex_modulus.py `
  -q -p no:cacheprovider

python `
  ultra-experiments/millennium/asmp9_reward_gauge_census/capped_simplex_modulus_v0_63/verify_development.py
```

The calculations are exact-rational implementation checks.  The displayed
inequalities in `THEOREM_DRAFT_v0_63.md` are the proof over the continuous
class.

