# ASMP-9 sharp atom-modulus result v0.47

## Verdict

**`sharp_atom_modulus_established_allocation_ranking_changed`**

All thirteen registered gates passed. At the frozen all-zero calibration atom,
the mandatory-set lower bound and the Buehler upper confidence limit agree
exactly for both decision problems and both fixed allocations. The
method-of-types construction used in v0.46 is conservative by a
decision-dependent amount large enough to reverse the registered four-class
allocation comparison.

This closes the v0.46 request for a matching finite decision-deficiency
modulus on one declared finite channel class. It does not establish a
continuous minimax rate, globally optimal statistic or allocation, strategic
robustness, real preference access, or resolution of ASMP-9.

## Frozen confirmation

- Total calibration budget `N=72`.
- Shared symmetric-flip grid

  ```text
  {0,.02,.04,.05,.06,.08,.10,.12,.13,.14,.15}^3
  ```

  containing exactly 1,331 parameters.
- Simultaneous error level `alpha=1/20`.
- Total observed calibration errors as the frozen ordered statistic.
- Four-class directed allocation `(30,21,21)`.
- Root-directed allocation `(70,1,1)`.
- Uniform allocation `(24,24,24)`.
- Complete horizon-two library of 3,748 adaptive policy-risk polynomials.

Two `N=66` development runs were disclosed and burned before registration.
The implementation was committed at `3e69399c7a598dc7805436469aa1d72280c47288`
and the confirmation registration at
`2ab0bc4d56ae93d641dff8be437c881c97641927`. Its SHA-256 is

```text
79b27566df548e734a7f18e4ae3521c6b882716d6337fd8a8cb208072d0da36f
```

## Exact matching modulus

For any deterministic confidence procedure with coverage at least
`1-alpha`, every parameter satisfying

```text
P_p(T=0) = product_q (1-p_q)^n_q > alpha
```

must be included at the all-zero atom. A spike confidence set attains this
mandatory region. More operationally, under the registered total-error
ordering,

```text
U(t) = max {d(p) : P_p(T<=t)>alpha}
```

is the smallest nondecreasing uniformly honest direct upper bound. At `t=0`,
this Buehler bound equals the mandatory-atom lower exactly.

The four registered rows were:

| Decision/design | Sharp lower = upper | v0.46 coupled upper | Exact rectangle |
|---|---:|---:|---:|
| four-class `(30,21,21)` | `13/100 = 0.13` | `0.447391607153` | `0.544566652799` |
| four-class uniform `(24,24,24)` | `42071/373271 ~= 0.112708997` | `0.456342068481` | `0.552012242735` |
| root-group `(70,1,1)` | `1/25 = 0.04` | `0.1125348832` | `0.244321574385` |
| root-group uniform `(24,24,24)` | `1/10 = 0.10` | `0.262668370732` | `0.390331600136` |

Every exact atom modulus is nonzero, every spike construction has coverage at
least `19/20` on all 1,331 grid points, and no fixed design has an
atom-probability equality at `alpha`.

## Allocation-dependent slack

The v0.46 method-of-types upper ranks the four-class directed design ahead of
uniform:

```text
0.447391607153 < 0.456342068481.
```

The exact unavoidable atom modulus ranks them in the opposite order:

```text
0.112708996949 < 0.13.
```

Thus the ranking reversal predicted from burned development data persists at
the disjoint budget. Uniform lowers the sharp four-class modulus by about
`13.30%` relative to `(30,21,21)`, although this pairwise result does not prove
that uniform is globally optimal over all 2,485 positive `N=72` allocations.

The root-directed result is stable across constructions. Concentrating 70 of
72 samples on the only decision-relevant root query lowers the sharp modulus
from `0.10` to `0.04`.

The exact independent-generator rectangle is above the coupled
method-of-types endpoint in every row. The three objects therefore form a
strict hierarchy on this fixture:

```text
sharp mandatory/Buehler modulus
  < method-of-types shared-channel upper
  < independent-generator rectangle.
```

The gaps are not constant across decisions or allocations.

## Controls

### Parameter radius is not decision deficiency

The channels

```text
(.10,0,0) and (.10,.10,.10)
```

have the same `L_infinity` parameter radius `.10`, but their exact
four-class risks are respectively

```text
.10 and .19.
```

This is the registered negative control against replacing the
decision-relative modulus with a convenient parameter radius.

### Root analytic control

For root-group loss, `d(p)=p_root`. Every maximizing witness has root
coordinate equal to the reported modulus. Branch coordinates can vary
without changing the risk, as required by the declared decision quotient.

### Statistic control

For every maximizing witness, the exact total-error CDF starts at the
all-zero product probability and terminates at one. The reported atom is
therefore the unique minimum-statistic endpoint of the nonvacuous confidence
procedure.

## Verification

- Dedicated tests: `15/15`.
- Registered source hashes: all match.
- Independent replay:
  - scientific payload: exact match;
  - exact risk rows: exact match;
  - comparator rows: exact match;
  - registration hash: match;
  - all gates: pass.
- Confirmation wall time: `96.241` seconds.
- Peak aggregate working set: `418,701,312` bytes.
- Frozen ceilings: 180 seconds, 1 GiB, four workers.

Canonical hashes:

```text
exact risk rows:
2128e2ad1fa4cf2bd827bfc928254ae230b08ada79726bd91fce9fdc884513fd

comparator rows:
83f5fbbdcf80c16a6d0955c3cbce960198ad817c4d5222e2d110695d5430e459

result:
daa1863bac0efebc0421dd1b03214a63c6bbe5e13f851dbc76db1e9e1f68c1d5

independent verification:
06623bea888f0c3523c668cfe690215a2db3647bc92f6c995b1727b8c41b0145
```

## Resolution relevance

Version v0.47 replaces the phrase “minimax modulus remains open” with a
narrower ledger:

- the conditional modulus is exact on this finite grid, at the all-zero atom,
  for deterministic confidence procedures;
- the same endpoint is optimal among nondecreasing direct bounds under the
  frozen total-error statistic;
- the earlier concentration and rectangle constructions are now measured
  upper relaxations rather than proxies for unavoidable uncertainty.

The remaining mathematical target is a sharp finite or continuous modulus
that is uniform over relevant observations/statistics and extends beyond iid
known binary channels, together with correlated/adaptive/strategic
misspecification and a justified physical preference channel.

## Claim boundary

The mandatory-atom and Buehler results are classical confidence theory. The
contribution here is their exact decision-relative specialization and
prospectively registered audit in the ASMP-9 access grammar. Nothing in this
result establishes that the finite grid models human or model preferences,
that total errors are an optimal ordering, that randomized confidence
procedures cannot improve another criterion, or that ASMP-9 is resolved.
