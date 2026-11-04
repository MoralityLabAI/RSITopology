# ASMP-9 v0.47 targeted burned development result

## Verdict

**`sharp_atom_modulus_live_confirmation_design_required`**

The targeted nonuniform grid repairs every failure of the first coarse
development run at the four fixed designs:

- every modulus is nonzero;
- mandatory-set lower and Buehler upper match exactly;
- no atom probability equals `alpha`; and
- every v0.46 method-of-types coupled upper is strictly above the sharp atom
  modulus.

The result also finds a decision-relevant ranking change: the v0.46
four-class allocation is worse than uniform under the sharp finite-grid atom
modulus, whereas the root-directed allocation remains substantially better
than uniform.

This run is burned development work.  It is not prospectively registered and
is not claim-eligible.

## Burned targeted design

- Parameter levels:

  ```text
  {0,.02,.04,.05,.06,.08,.10,.12,.13,.14,.15}^3.
  ```

- Full parameter universe: 1,331 shared channels.
- Exact four-class risks computed only on the union of mandatory regions for
  the two fixed classification designs: 154 channel points.
- Four-class decision designs:
  `(28,19,19)` and uniform `(22,22,22)`.
- Root-group designs:
  `(64,1,1)` and uniform `(22,22,22)`.
- `alpha=1/20`.
- Four CPU workers.
- Elapsed time: `74.047` seconds.

All excluded channel points remain in the confidence parameter universe; their
decision risks need not be computed because they cannot enter the mandatory
maximum.  Coverage is checked over the full 1,331-point universe.

## Exact fixed-design moduli

| Decision/design | Sharp atom modulus | v0.46 method-of-types upper | Ratio v0.46/sharp |
|---|---:|---:|---:|
| four-class `(28,19,19)` | `7/50 = 0.14` | `0.4725225142536221` | `3.3752` |
| four-class uniform `(22,22,22)` | `28561/236136 ~= 0.12095149` | `0.4817295510465465` | `3.9828` |
| root-group `(64,1,1)` | `1/25 = 0.04` | `0.121200875641` | `3.0300` |
| root-group uniform `(22,22,22)` | `3/25 = 0.12` | `0.280089971626` | `2.3341` |

The exact four-class witnesses were:

```text
(28,19,19):
  (p_root,p_left,p_right) = (0,0,.14) or (0,.14,0)

(22,22,22):
  (p_root,p_left,p_right) = (.08,0,.05) or (.08,.05,0).
```

For root-group loss, branch coordinates are decision-irrelevant.  The
maximizing root rates were `.04` under `(64,1,1)` and `.12` under uniform.

## Interpretation

The v0.46 method-of-types construction is not merely an approximately
constant inflation of the unavoidable decision uncertainty.  On this finite
grid it reverses the comparison between the registered four-class allocation
and uniform:

```text
v0.46 method-of-types:
  (28,19,19) better than (22,22,22)

sharp all-zero modulus:
  (22,22,22) better than (28,19,19).
```

This does **not** establish that uniform is globally optimal for the sharp
modulus; the targeted run compares only two fixed classification designs.
It establishes that confidence-construction slack is decision- and
allocation-dependent enough to alter a pairwise design ranking.

The root result points the other way: putting 64 of 66 samples on the only
decision-relevant query lowers the sharp modulus from `.12` to `.04`, so the
decision-directed acquisition principle survives there.

## Nonvacuous confidence interpretation

The mandatory-atom lower is attained pointwise by a spike confidence set, but
that construction is useless away from the all-zero outcome.  The theorem
draft now supplies the stronger operational reading.  With total observed
calibration errors as an ordered statistic,

```text
U(t) = max {d(p): P_p(T<=t)>alpha}
```

is the smallest nondecreasing uniformly honest direct upper bound on decision
risk.  At `t=0`, it equals the reported atom modulus.  This is a finite
Buehler-optimal construction, not a new confidence-theory claim.

## Registration implications

A prospective confirmation should:

1. use a disjoint total budget, provisionally `N=72`;
2. freeze extrapolated fixed designs before outcomes:
   four-class `(30,21,21)`, root `(70,1,1)`, and uniform `(24,24,24)`;
3. freeze the finite channel grid and total-error statistic;
4. make the fixed-design comparison primary and any full allocation census
   descriptive;
5. require exact mandatory-set/Buehler equality and zero unhandled boundary
   points;
6. preregister whether the four-class pairwise ranking reversal persists;
7. retain an analytic root-group control;
8. compare against both the v0.46-style coupled method-of-types upper and the
   independent-generator rectangle; and
9. state that optimal choice of evidence statistic remains open.

## Provenance

```text
DEVELOPMENT_TARGETED_RESULT_v0_47.json
SHA-256:
98dba1dff0acfcce4d75cceaa499a41a68aac97dcd30d6ecbbb07be1711f4949
```

## Claim boundary

The result is a burned finite-grid liveness check.  It does not establish a
continuous minimax rate, a globally optimal allocation, optimal choice of
confidence statistic, strategic robustness, real preference access, or
resolution of ASMP-9.
