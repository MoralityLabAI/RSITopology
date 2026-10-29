# ASMP-9 selection-channel boundary development result v0.60

Status: **unregistered development result; not claim eligible**.

## Verdict

Selection timing, support, and weight bounds produce three different
identifiability regimes.

1. **Recorded pre-response menu selection:** the joint law exactly recovers
   every selected menu conditional. Unknown target-dependent menu frequencies
   do not bias those conditionals; support is the operative access object.
2. **Positive selection floor:** total finite-sample cost scales as `1/pi`,
   and that exponent is necessary on the explicit v0.58 cross-tier slice.
3. **Unknown outcome-dependent recording:** complete menu assignment alone
   does not identify. With recording weights bounded in `[ell,u]`, however,
   cross-tier confusability has an exact multiplicative radius.

These are classical missing-data and choice-sampling facts composed with the
ASMP-9 tier ledger. Novelty is not established.

## Recorded pre-response selection

Under

```text
A ~ s_p,
Y | A ~ p_A,
```

with both `(A,Y)` recorded,

```text
J(A,x) = s_p(A)p_A(x).
```

Every positive-support menu is recovered by conditioning:

```text
s_p(A) = sum_x J(A,x),
p_A(x) = J(A,x)/s_p(A).
```

Because the map `p -> s_p` is otherwise unrestricted and unknown, the menu
marginal provides no uniform information about missing conditionals. The
joint experiment therefore reduces exactly to the supported menu domain.

Combining this factorization with the verified v0.56 theorem gives:

| supported-domain state | compatible full-kernel tiers |
|---|---|
| complete menu support | the clean kernel's singleton tier |
| proper support, no RUM completion | `{N}` |
| proper support, RUM but no Luce completion | `{R,N}` |
| proper support, Luce completion | `{L,R,N}` |

A proper domain can refute RUM, but cannot uniformly classify every positive
kernel. Complete support is the sharp domain condition for uniform
singleton-tier classification under unrestricted completion.

## Positivity controls total sample complexity

If the identifying menu family has `m_D` menus and

```text
pi = min_A s_p(A)>0,
```

then a per-menu requirement `n_A` is met with total failure probability at
most `delta/2` when

```text
T >= max{
  2 n_A/pi,
  (8/pi) log(2m_D/delta)
}.
```

The proof is the multiplicative Chernoff bound plus a union bound over menu
undercounts. Combining it with the v0.58 conditional-response certificate at
failure probability `delta/2` gives a total `1-delta` certificate.

For the representative `n=3,r=1,a=0.2,gamma=0.2,delta=0.05` cell, the
conditional requirement is `76,463` responses per menu. The resulting total
draw bounds are:

| selection floor `pi` | sufficient total draws |
|---:|---:|
| 0.25 | 611,704 |
| 0.10 | 1,529,260 |
| 0.05 | 3,058,520 |
| 0.01 | 15,292,600 |
| 0.001 | 152,926,000 |

The counts are conservative sufficient bounds, not recommendations or
minimax constants.

### Matching negative exponent

The v0.58 margin-promised RUM/non-RUM pair differs only on the full menu.
If that menu is selected with probability `eta`, single-draw joint KL is

```text
eta D_gamma,

D_gamma = -(2/5)log(1-25gamma^2).
```

Any classifier with maximum error at most `delta<1/2` therefore requires

```text
T
>=
2(1-2delta)^2
/
{eta D_gamma}.
```

This proves `Omega(1/(pi gamma^2))` on the frozen three-alternative slice,
matching the sufficient rate's `1/pi` and `1/gamma^2` exponents there. If
positive support is allowed to approach zero with no declared floor,
population identification survives but no uniform finite total budget does.

## Outcome-dependent recording

Suppose a response `x` is retained with unknown probability `rho(x)`. Its
recorded joint mass is

```text
h(x)=p(x)rho(x).
```

With unrestricted positive `rho`, any two positive clean distributions can
be mapped to the same selected conditional and the same overall retention
rate. Applied menu by menu, this makes every pair of positive full kernels
observationally equivalent despite complete menu assignment.

### Exact bounded-recording radius

Under the nonvacuous restriction

```text
0 < ell <= rho_A(x) <= u <= 1,
```

two clean menu distributions `p,p'` have a common complete record law iff

```text
max_x max{
  p(x)/p'(x),
  p'(x)/p(x)
}
<=
u/ell.
```

The proof is coordinatewise interval intersection. A common recorded mass
must lie in

```text
[ell p(x),u p(x)] intersect [ell p'(x),u p'(x)].
```

When the ratio condition holds, the exact witness is

```text
h(x)=max{ell p(x),ell p'(x)}.
```

For a compact tiered class, define `Lambda` as the minimum of that maximum
coordinate ratio over cross-tier pairs. Then:

```text
u/ell < Lambda       -> tier identifiable;
u/ell = Lambda       -> confusable boundary, reported inconclusive;
u/ell > Lambda       -> cross-tier ambiguity.
```

For the v0.58 separation promise,

```text
Lambda >= (2+gamma)/(2-gamma).
```

This follows from the sharp likelihood-ratio oscillation inequality. The
explicit v0.58 RUM/non-RUM pair supplies the opposite bracket:

```text
Lambda <= 1/(1-5gamma)
```

on the three-alternative slice. The brackets do not coincide; sharp
evaluation of `Lambda` remains open.

Known positive recording weights restore the clean law exactly through

```text
p(x)=h(x)/rho(x).
```

Forced recording or a known response-independent recording intervention has
the same effect.

## Verification

Development tests:

```text
10 passed
```

They cover:

- exact recorded-menu factorization with support zeros;
- the full v0.56 compatible-tier ledger;
- joint-KL factorization;
- exhaustive outcome-selection confounding over a rational simplex;
- exact correction with known recording weights;
- 900 bounded-recording radius and witness cells;
- the likelihood-ratio margin radius;
- the explicit RUM/non-RUM multiplicative witness; and
- matching inverse-selection-probability rate scaling.

Import-independent verifier:

```json
{
  "bounded_radius_checks": 900,
  "confounding_checks": 225,
  "correction_checks": 15,
  "lower_rate_checks": 5,
  "margin_radius_checks": 4,
  "preselection_checks": 4,
  "rate_checks": 5,
  "registered": false,
  "status": "development_checks_passed",
  "tier_handoff_checks": 3,
  "witness_radius_checks": 3
}
```

## Prior-art verdict

Rubin's ignorability framework, Manski-Lerman choice-based sampling,
Horowitz's endogenous choice-set model, and modern latent choice-set
identification all predate this result. The bounded-recording interval
calculation is elementary likelihood-ratio geometry.

The residual is an ASMP-9 access ledger:

```text
selection timing
  + menu support
  + positivity
  + recording-ratio radius
  + the Luce/RUM/non-RUM tier object.
```

No novelty claim is made.

## Freeze decision

Do **not** register yet. Before a claim-eligible version:

1. obtain external review of the missing-data and choice-based-sampling
   subsumption boundary;
2. decide whether pre-response selection and post-response recording belong
   in one theorem or separate registrations;
3. replace the abstract class moduli by certified finite optimizers or dual
   bounds on useful instances;
4. preserve the distinction between recorded menus and hidden consideration
   sets; and
5. specify whether the intended physical channel observes rejected events,
   retention rates, and menu identities.

## Claim boundary

This result assumes finite positive kernels, iid stable conditionals,
recorded menus, and frozen selection timing. It does not identify latent
choice sets, solve latent-state confounding, cover strategic or adaptive
responses, handle nonstationarity or continuous choices, validate the
bounded-context model, or establish moral or welfare relevance. It is not a
human/model experiment and does not resolve ASMP-9.
