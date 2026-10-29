# ASMP-9 v0.23 development note

Status: outcome-bearing development record.  None of the graphs, counts, or
symbolic cells named here may later be called fresh.

## Derived exact representation

For a connected bridgeless graph and positive integer edge counts `n_e` at
`epsilon=1/2`,

```text
F_G(n)
  = -2^(-N) Z_G(-1,{2^(n_e)-1}),
N = sum_e n_e.
```

The identity was checked by three independent finite routes on the burned
triangle, diamond, theta, and K4 graphs:

1. direct enumeration of all `3^|E|` residual statuses;
2. spanning-subgraph evaluation of the multivariate random-cluster
   polynomial; and
3. coefficientwise enumeration for fixed bidirected-edge sets.

The uniform specialization reproduces the Backman expression used in v0.22.

## K4 strict-local/suboptimal family

Use edge order `(01,02,03,12,13,23)`.  At total count `6s`, `s>=2`, set

```text
trap     = (s-1,s,s+1,s+1,s,s-1)
balanced = (s,s,s,s,s,s).
```

Let `t=2^s`.  When the three opposite edge pairs have powers `x,y,w`, the
common-denominator numerator is

```text
S(x,y,w)
  = (xyw)^2 - 2(x^2+y^2+w^2) - 8xyw
    + 12(x+y+w) - 24.
```

The balanced-minus-trap numerator gap is

```text
S(t,t,t)-S(t/2,t,2t) = 3t(3t-4)/2 > 0.
```

Every feasible one-unit transfer from the trap is worse.  The 30 ordered
transfers fall into nine factor classes:

```text
low    -> middle : t(4t^2+7t-18)/4
low    -> high   : t(4t^2+31t-42)/4
low    -> low    : t(4t^2-3)/2
middle -> low    : t^2(2t-1)/2
middle -> high   : t(t^2+7t-9)
middle -> middle : t(2t^2-3)
high   -> low    : t(t-2)(2t-3)/2
high   -> middle : t^2(t-2)
high   -> high   : 2t(t^2-3).
```

All are strictly positive for `t>=4`.  At `s=2`, moves donating from a
count-one edge are infeasible and the remaining twenty moves are still
strictly worse.

## Explicit M-concavity violation

Take `x=trap`, `y=balanced`, a high edge `i`, and either low edge `j`.
The exchange-axiom deficit is

```text
f(x)+f(y)-f(x-e_i+e_j)-f(y+e_i-e_j)
  = t^2(4t-5)/2 > 0.
```

Both eligible `j` violate the required inequality, so the objective is not
M-concave.  This is stronger and more mechanically checkable than inferring
non-M-concavity only from the existence of a strict suboptimal local maximum.

## Development checks

Run:

```powershell
python -m pytest -q `
  ultra-experiments/millennium/asmp9_reward_gauge_census/nonuniform_multivariate_v0_23/test_nonuniform_multivariate_v0_23.py
```

Prospective validation must use separately registered cells.  The K4 theorem
is algebraic rather than empirical; fresh numeric `s` values can validate the
implementation but do not make the already-derived family fresh.
