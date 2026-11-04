# ASMP-9 context-quotient response theorem draft v0.68

Status: **unregistered theorem development; not claim eligible**.

## 1. Measurement grammar

Let `B` be a finite set of nuisance blocks. In the physical successor, one
block is a fixed `(scenario, display order, tensor shape)` stratum. Let `A`
contain one reference arm and at least one message arm. A score table is

```text
y in R^(B x A).
```

The measurement-nuisance group `N = R^B` acts by

```text
(u . y)_(b,a) = y_(b,a) + u_b.
```

This permits an arbitrary common-mode score offset in every block. It does not
permit an arm-by-order interaction to be called nuisance.

Choose reference arm `a0` and define

```text
Q(y)_(b,a) = y_(b,a) - y_(b,a0),  a != a0.
```

## 2. Maximal-invariant theorem

### Theorem 1

`Q` is a maximal invariant for the `N` action:

```text
Q(y) = Q(y')  iff  y' = u . y for some u in N.
```

### Proof

Common block offsets cancel in every difference, proving invariance. Conversely,
if all reference contrasts agree, set

```text
u_b = y'_(b,a0) - y_(b,a0).
```

Then equality of each contrast gives `y'_(b,a) = y_(b,a) + u_b` for every arm.

Thus the quotient has dimension `|B|(|A|-1)`. No absolute baseline sign
descends to this quotient because a block offset can reverse it without
changing `Q`.

### Theorem 2

A linear estimand

```text
L_c(y) = sum_(b,a) c_(b,a) y_(b,a)
```

is nuisance-invariant if and only if

```text
sum_a c_(b,a) = 0
```

for every block `b`.

### Proof

Under offset `u`, the estimand changes by

```text
sum_b u_b sum_a c_(b,a).
```

This vanishes for every `u` exactly under the stated blockwise zero-sum
condition.

## 3. Endpoint-specific consequence

The v0.67 absolute state map used the sign of a block-level baseline. That sign
is not an estimand on this quotient. The following matched contrasts are:

```text
content effect within one order
  = score(content) - score(balanced)

label effect within one order
  = score(label) - score(balanced)

content specificity within one order
  = score(content) - score(label)

post-washout effect within one order
  = score(content_washout) - score(balanced_washout).
```

The two display orders must be contrasted separately before any pooling.
Agreement across orders is an empirical transportability condition, not a
consequence of the quotient. An arm-by-order interaction survives `Q` and must
remain visible.

## 4. Local object versus global object

Suppose each context supplies a closed interval `I_b` for one matched effect.
A common context-independent scalar effect exists exactly when

```text
max_b lower(I_b) <= min_b upper(I_b).
```

If the inequality fails, the instrument may still report the context-indexed
family `{I_b}`. It may not average the intervals into a global response state.
This separates failure of globality from failure of local measurement.

## 5. What the theorem fixes

The theorem turns the v0.67.1 failure into an admission rule:

1. numerical repeatability is calibrated using byte-identical singleton
   forwards and is not mixed with semantic order sensitivity;
2. only estimands in the blockwise zero-sum contrast space may pass through
   the context/order nuisance quotient;
3. order agreement is tested on those matched contrasts rather than on
   absolute baselines; and
4. a global response operator is optional and requires a separate
   intersection/generalization gate.

## 6. What it does not fix

This is the classical within-block transformation and contrast-space
criterion. It does not show that the additive nuisance action is physically
complete, that the response score is a reward, that context effects are
values, that a latent value object exists, or that any reward-shaping quotient
has been identified. It contributes an exact admission layer for a successor
physical experiment; it does not resolve ASMP-9.
