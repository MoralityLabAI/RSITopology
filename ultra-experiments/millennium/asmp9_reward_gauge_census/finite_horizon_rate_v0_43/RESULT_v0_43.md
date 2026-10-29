# ASMP-9 v0.43 finite-horizon rate result

## Verdict

**Finite-horizon rate characterization established on the registered binary
sentinel family.**

The quadratic horizon factor in the v0.42.1 sufficient sample bound is not
intrinsic on this family. The exact lower and upper certificates have matching
horizon and gap exponents:

```text
n = Theta(h / g^2)
```

at fixed confidence.

This is a sharp-exponent theorem for one finite experiment family, not a
minimax theorem over every adaptive experiment and not an ASMP-9 resolution.

## The correction

The v0.42 obligation matrix proposed looking for a two-point family with:

```text
risk gap       = Theta(h delta)
one-step KL    = Theta(delta^2).
```

That witness cannot exist uniformly in the horizon for bounded terminal loss.
For the same adaptive policy under two channel libraries, the KL chain rule
and Pinsker imply:

```text
transcript KL <= h kappa
risk gap <= loss_span sqrt(h kappa / 2).
```

If `kappa <= C delta^2`, then:

```text
risk_gap / (h delta) <= sqrt(C/(2h)) -> 0.
```

The registered values for `C=4` were:

| Horizon | Upper bound on `risk_gap/(h delta)` |
|---:|---:|
| 2 | 1.000 |
| 8 | 0.500 |
| 32 | 0.250 |
| 128 | 0.125 |

The original lower-bound target combined two mutually incompatible scaling
requirements. Boundary-support TV perturbations can still accumulate linearly
in `h`, but they do not have the same regular quadratic-KL geometry.

## Exact sentinel deficiency

The registered experiment has two targets, zero-one terminal loss, and one
binary query repeated at most `h` times:

```text
P(Y=1 | theta=0) = 0
P(Y=1 | theta=1) = p.
```

The exact directed deficiency to perfect revelation is:

```text
D_h(p) = (1-p)^h / (1 + (1-p)^h).
```

All 30 registered comparisons—six horizons by five rational probabilities—
matched the existing v0.41 Bellman/LP compiler exactly.

## Lower certificate

For:

```text
p0 = 1/(2h)
p1 = (1/2 + epsilon)/h,
```

all 32 registered horizon/epsilon cells verified in exact rational arithmetic:

```text
epsilon/16 <= D_h(p0)-D_h(p1) <= epsilon
KL(Ber(p0)||Ber(p1))
  <= chi2(Ber(p0)||Ber(p1))
  <= 4 epsilon^2/h.
```

Pinsker/Le Cam then forces:

```text
n = Omega(h/g^2)
```

for an access decision that separates the two deficiencies with both
pointwise errors at most `1/4`.

At the representative fixed value `epsilon=1/8`:

| Horizon | Exact deficiency gap, decimal view | First sample count not ruled out | `n g^2/h` |
|---:|---:|---:|---:|
| 2 | 0.039045093 | 28 | 0.02134327 |
| 8 | 0.030898771 | 148 | 0.01766258 |
| 32 | 0.029371380 | 628 | 0.01693006 |
| 128 | 0.029013032 | 2,548 | 0.01675621 |

The artifact retains the exact rational values; decimals above are only a
readable view.

## Upper certificate

Partition the raw target-one channel samples into blocks of length `h` and
record whether every observation in a block is zero. The block indicator has
mean `(1-p)^h`. Hoeffding concentration plus the one-Lipschitz map
`a -> a/(1+a)` gives:

```text
n = O(h log(1/alpha)/g^2).
```

At `alpha=0.05` and `g=1/16`, every horizon used exactly 473 blocks:

| Horizon | Raw samples | Radius | `n g^2/h` |
|---:|---:|---:|---:|
| 8 | 3,784 | 0.062445574 | 1.84765625 |
| 16 | 7,568 | 0.062445574 | 1.84765625 |
| 32 | 15,136 | 0.062445574 | 1.84765625 |
| 64 | 30,272 | 0.062445574 | 1.84765625 |
| 128 | 60,544 | 0.062445574 | 1.84765625 |

The same frozen linear-horizon rule passed for gaps `1/32` and `1/8`.

## Gates

| Gate | Check | Result |
|---|---|---|
| `P0` | 75 preregistration tests | pass |
| `S0` | registration, environment, source, inherited compiler, runner, and verifier hashes | pass |
| `E0` | 30 exact compiler/formula comparisons | pass |
| `L0` | 32 exact two-point lower certificates | pass |
| `K0` | registered no-linear-witness decay sequence | pass |
| `U0` | 15 block upper-rate rows | pass |
| `R0` | exact row universe | pass |
| `RESOURCE` | 120 seconds and 512 MiB ceilings | pass |

Execution used 8.593 seconds and a peak sampled working set of 276,803,584
bytes. Independent deterministic replay reproduced every scientific row and
gate.

## Provenance

- Implementation commit:
  `6319aad7fdb1fef94d1c25abe1d2d6cc56680b07`
- Registration commit:
  `f20705d22a99072c3d61b0c43ba483d43d176385`
- Registration SHA-256:
  `34d519d48d06fd64d2450c83bce8b1aaf9583b0434885533c720917d5537a81b`
- Result SHA-256:
  `d96bc39cba4435734373d4689343537ecebdf184ac70d51876563c707baea88d`
- Independent verification SHA-256:
  `dfb23d5f6424cfbbf2efff5af5c923ab2a4c3018ca43a16d4f2f079e3b498748`

## Claim boundary

Version v0.43 corrects the finite-horizon exponent on one exact sentinel
family and supplies a general policy-uniform KL perturbation upper bound. It
does not prove the minimax rate for every finite adaptive channel library,
construct optimal simultaneous multinomial KL regions, make policy search
efficient, handle strategic or misspecified demonstrators, validate a real
behavioral channel, or resolve ASMP-9.
