# ASMP-10 exact finite-prefix obstruction protocol v0.1

## Question

When do finite local training observables identify a bounded-degree polynomial
loss, and when can two losses have identical observed prefixes but opposite
future capability outcomes?

## Frozen mathematical class

Let the state be one-dimensional and let gradient descent use unit step size:

`x_(t+1) = x_t - L'(x_t)`.

The allowed loss class is the real polynomials of degree at most `D`. The
observation filtration contains, at each of `n` distinct registered prefix
points `x_i = i`, all derivatives `L^(r)(x_i)` for `r = 0,...,k`. The primary
census uses `k >= 1`, so the update-producing gradient is included.

Write `J = n(k+1)` for the number of scalar jet observations. The confluent
Vandermonde map from `D+1` polynomial coefficients to these observations is
`H(n,k,D)`.

## Exact threshold claim

The registered claim is the classical Hermite-interpolation threshold:

1. `rank H(n,k,D) = min(D+1, J)` for the registered distinct nodes;
2. if `D < J`, the jet observations identify the loss inside the declared
   degree class;
3. if `D >= J`, a nonzero invisible perturbation exists, with the threshold
   witness

   `q(x) = product_(i=0)^(n-1) (x-i)^(k+1)`.

The witness has degree `J` and all derivatives through order `k` vanish at all
observed nodes. Therefore the two losses

`L_plus(x) = -x + epsilon q(x)` and
`L_minus(x) = -x - epsilon q(x)`

have identical allowed jets and identical gradient-descent states through
`x_n = n`, starting at `x_0 = 0`. Freeze
`epsilon = 1 / q'(n)`. At the first update whose jet was not observed,
`L_plus` leaves the state at `n`, while `L_minus` moves it to `n+2`. The frozen
continuous future score is `S(x) = x-(n+1)` and the capability predicate is
`C(x) = 1[S(x) > 0]`; the two outcomes have scores `-1` and `+1`.

## Census

- `n in {1,2,3,4,6}`;
- `k in {1,2,3}`;
- `D in {max(0,J-2), J-1, J, J+1}` with duplicates removed;
- exact rational arithmetic only.

## Frozen gates

- **R0 rank:** every census row has exact rank `min(D+1,J)`.
- **I0 identification:** every `D=J-1` row has zero nullity.
- **O0 obstruction:** every `D=J` row has a degree-`J` witness in the exact
  kernel; both losses match every registered jet; their observed state prefixes
  agree; and their future scores are exactly `-1` and `+1`.
- **C0 controls:** at least one underdetermined row has positive nullity and at
  least one identified row has zero nullity, preventing a constant-status
  implementation from passing.

All gates are conjunctive. Any failure yields `instrument_failed`; otherwise
the result is `finite_prefix_obstruction_established_for_registered_class`.

## Interpretation

A pass proves an exact obstruction only for the declared bounded-degree
polynomial family and finite jet filtration. It demonstrates that uniform
future prediction needs either enough independent observations to identify the
declared dynamics or additional regularity excluding invisible continuations.
It does not prove that any particular neural-network capability is
unpredictable, nor that SLT, spectral, loss-curve, or representation observables
are useless in a narrower training family.

## Prior-art boundary

The rank and kernel statements are direct consequences of classical confluent
Vandermonde/Hermite interpolation. The experiment's contribution is an exact,
replayable ASMP-10 instrument and claim boundary, not a new interpolation
theorem.

