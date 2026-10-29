# Exact contamination and recording moduli on a continuous RUM-boundary slice

Status: **candidate theorem; unregistered development only**.

## 1. Frozen slice

Use alternatives `a,b,c`.  Freeze the binary responses

```text
p(a|ab)=2/5,  p(a|ac)=3/5,  p(b|bc)=3/5.
```

Their Luce cycle defect is `6/125`, so every kernel in the slice is at maximum
menuwise `L1` distance at least `1/125` from the Luce closure.

Fix

```text
0 < gamma <= 1/125.
```

Define the compact RUM segment

```text
R_gamma = {
  p_t(abc)=(2/5, 2/5-t, 1/5+t)
  : 0 <= t <= gamma/2
}
```

and the compact non-RUM segment

```text
N_gamma = {
  q_s(abc)=(2/5+s, 2/5-s, 1/5)
  : gamma <= s <= 2 gamma
}.
```

Every binary menu remains fixed.  Since `n=3`, every pair-context function
has Boolean degree at most one, so the entire class lies in `BP_1`.

## 2. Tier and margin certificates

In lexicographic ranking order

```text
abc, acb, bac, bca, cab, cba,
```

`p_t` is induced by the nonnegative ranking weights

```text
(1/5+t, 1/5-t, 1/5, 1/5-t, 0, 1/5+t).
```

Thus every `p_t` is RUM.  It is not Luce because the fixed binary cycle defect
is nonzero.

Every `q_s` violates regularity:

```text
q_s(a|abc)-q_s(a|ab)=s>0.
```

For any RUM kernel `r`, that functional is nonpositive.  If

```text
d(q_s,r)=max_A ||q_s(.|A)-r(.|A)||_1,
```

then changing the two coordinates in the functional costs at most `d`, because
one coordinate of a probability vector changes by at most half its `L1`
distance.  Hence

```text
d(q_s,P) >= s >= gamma.
```

Both segments therefore lie in the v0.58 closed margin-promised class:
`R_gamma` is non-Luce RUM at Luce distance at least `1/125>=gamma`, and
`N_gamma` is at RUM distance at least `gamma`.

## 3. Exact observed-TV modulus

For `0<=t<=gamma/2` and `gamma<=s<=2gamma`, binary menus agree and

```text
TV[p_t(.|abc),q_s(.|abc)] = s.
```

Therefore

```text
Delta(R_gamma union N_gamma, D_3) >= gamma.
```

Equality is attained by every pair with `s=gamma`, so

```text
Delta = gamma.
```

The exact fixed-Huber population threshold from v0.59 is consequently

```text
epsilon_star = gamma/(1+gamma).
```

The lower certificate is the single event `{a}`:

```text
TV(p_t,q_s) >= |q_s(a)-p_t(a)| = s >= gamma.
```

## 4. Exact bounded-recording modulus

For every cross-tier pair, the `a` coordinate gives

```text
q_s(a)/p_t(a)
  = (2/5+s)/(2/5)
  >= 1+(5/2)gamma.
```

Thus

```text
Lambda >= 1+(5/2)gamma.
```

Set

```text
s_star = gamma,
t_star = (5/2) gamma^2.
```

Because `gamma<=1/125<1/5`, `t_star<=gamma/2`.  At this pair:

```text
q_a/p_a = 1+(5/2)gamma,

p_b/q_b
  = (2/5-(5/2)gamma^2)/(2/5-gamma)
  = 1+(5/2)gamma,

p_c/q_c = 1+(25/2)gamma^2
         <= 1+(5/2)gamma.
```

All binary ratios are one.  Hence the lower bound is attained:

```text
Lambda = 1+(5/2)gamma.
```

The exact v0.60 bounded-recording boundary is therefore

```text
u/ell = 1+(5/2)gamma.
```

Equality is confusable and is reported `boundary_inconclusive`, never as an
identifiability pass.

## 5. What this changes

The v0.61 stack verified that `Delta` and `Lambda` are the right class-level
robustness objects and that their minima are attained on the compact
probability-floor class.  Version v0.62 supplies the first continuous
non-singleton class where both are evaluated exactly with primal and dual
certificates.

It also shows that the generic lower brackets need not be sharp and that the
two corruption grammars have different local geometry:

```text
additive Huber threshold:
  gamma/(1+gamma);

multiplicative recording threshold:
  1+(5/2)gamma.
```

## Proof debt before registration

1. Independently reconstruct every `p_t` from its ranking weights.
2. Verify the Luce-cycle distance certificate with the v0.58 convention.
3. Check the exact primal Huber and bounded-recording common observations.
4. Search for a discrete-choice robust-testing result that already states
   this slice specialization.
5. Keep the slice result separate from any claim about the full
   `C_(n,r,a,gamma)` modulus.

## Claim boundary

This is an elementary exact calculation on one deliberately solvable compact
three-alternative slice.  It is not a general modulus algorithm, a minimax
robust-choice theorem, an empirical result, a welfare result, or a resolution
of ASMP-9.

