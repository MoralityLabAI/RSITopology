# Additive coordinate-fidelity amendment to Gaussian quotient v0.70

Status: **development-only scope correction; v0.70 files remain unchanged**.

## Finding

The v0.70 formula

```text
trace(M^-1)
```

is exact for squared Euclidean loss in the registered orthonormal quotient
coordinates. It is not invariant under an arbitrary change of quotient
coordinates if the identity loss matrix is silently reintroduced after the
change.

Therefore “parameter-optimal” has scientific meaning only after a quotient
loss metric is frozen and transported with the coordinates.

## Coordinate law

Let old quotient coordinates be `x` and new coordinates be

```text
x' = T x
```

for invertible `T`. If raw query rows form matrix `B`, then

```text
B' = B T^-1.
```

Consequently the information matrix transforms by congruence:

```text
M' = T^-T M T^-1.
```

If the registered quadratic scientific loss is

```text
(x_hat-x)^T W (x_hat-x),
```

its new coordinate matrix must be

```text
W' = T^-T W T^-1.
```

The minimax risk is invariant:

```text
trace(W' M'^-1) = trace(W M^-1).
```

For scalar policy functional `c^T x`, the transported covector is

```text
c' = T^-T c,
```

and likewise

```text
c'^T M'^-1 c' = c^T M^-1 c.
```

These identities are exact.

## Consequence for v0.70

The v0.70 fixture registered `W=I` in its displayed quotient coordinates.
Its exact result remains:

```text
Euclidean-coordinate parameter optimum = (5,5,2),
risk = 14/45.
```

It must not be quoted as a coordinate-free optimum. Under the same query
coordinates and sample budget:

```text
W = diag(100,1)  -> optimum (10,1,1);
W = diag(1,100)  -> optimum (1,10,1).
```

Both weighted risks are `211/21`. The change is not a contradiction: these
are different scientific losses.

The policy-functional result is intrinsically coordinate-invariant when the
functional is transported as a covector. This makes the policy-directed
branch better suited to ASMP-9's declared downstream-decision framing, while
still requiring the policy family and margin to be frozen.

## Exact audit

The additive verifier checks:

1. row-based and congruence-based information transformations agree;
2. quadratic risk is unchanged when `W` is transported;
3. policy-functional risk is unchanged when `c` is transported;
4. silently resetting the metric to the identity changes the risk under a
   nonorthogonal reparameterization;
5. orthogonal reframing preserves the identity metric; and
6. the three exact integer-allocation optima above.

## Claim boundary

This amendment corrects coordinate fidelity in a development-only Gaussian
calibration theorem. It does not establish which quotient metric is morally
or behaviorally meaningful, validate a physical channel, identify human or
model value, or resolve ASMP-9.
