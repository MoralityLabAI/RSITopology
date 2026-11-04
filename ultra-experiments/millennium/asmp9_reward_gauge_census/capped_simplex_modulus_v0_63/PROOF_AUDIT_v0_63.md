# ASMP-9 capped-simplex modulus proof audit v0.63

## Audit target

The prospective verification covers four assertions:

1. the fixed binary fiber is RUM exactly on one capped simplex;
2. total cap-violation mass is exact TV distance to that simplex;
3. the additive cross-tier modulus is `gamma`; and
4. the multiplicative cross-tier modulus is `1+(5/2)gamma`.

## A. Ranking reconstruction

There are six strict rankings and five independent observed probabilities:
three binary probabilities plus two full-menu coordinates.  Solving the
linear system gives the six weights printed in
`THEOREM_DRAFT_v0_63.md`.  Their sum is one.  Nonnegativity reduces exactly
to

```text
x_a<=2/5,
x_b<=3/5,
x_c<=2/5.
```

The verification grid reconstructs the full-menu and all three binary
probabilities from those weights for every RUM grid point.  For every
non-RUM point at least one weight is negative.

## B. Projection lower and upper certificates

For any cap-violating coordinate `i`, every RUM point has `p_i<=u_i`; hence
the positive part of `q_i-p_i` pays at least `q_i-u_i`.  Summing gives the
TV lower certificate `V(q)`.

Clipping every violated coordinate to its cap removes `V(q)`.  Because the
cap vector sums to `7/5`, the complement has `2/5+V(q)` spare capacity.
Adding back `V(q)` produces a RUM point with exactly `2V(q)` L1 movement.
The construction only raises unviolated coordinates, so it preserves the
probability floor.

The prospective verifier compares the constructive projection with the
minimum over every RUM point on two disjoint exact grids.

## C. Additive primal and dual

The projection theorem gives the class-wide lower bound `gamma`.  The
registered primal pair has one `a`-cap violation of exactly `gamma` and TV
distance exactly `gamma`.

At the Huber threshold `gamma/(1+gamma)`, normalized coordinatewise maxima
give one observed distribution in both contamination neighborhoods.

## D. Multiplicative support exhaustion

For a violation support `E`, aggregate probability on `E` expands from at
most `U_E` to `U_E+d`, while its complement contracts from at least
`1-U_E` to `1-U_E-d`.  A coordinate ratio must be at least each corresponding
aggregate ratio.

No support with cap sum at least one can be violated: it would require
`q(E)>1`.  The only feasible supports have cap sums:

```text
2/5,3/5,4/5.
```

The verifier evaluates all four labelled supports.  The unique cap-sum
minimum is `2/5`, attained by either singleton `{a}` or `{c}`.  The registered
primal uses `{a}`.

At recording ratio `1+(5/2)gamma`, coordinatewise maximum lower-recorded
masses give one common subprobability law with both recording vectors inside
the registered interval.

## E. Precision and implementation

All scientific arithmetic uses `fractions.Fraction`.  There are no floating
point comparisons in a theorem gate.  The independent replay duplicates the
ranking, projection, support, Huber, and recording calculations without
importing `capped_simplex_modulus.py` or the primary verifier.

## F. Remaining non-transfer clauses

The proof does not establish:

- a formula for arbitrary RUM polytopes;
- hidden-menu or latent-selection identification;
- strategic or nonstationary response;
- physical availability of the frozen menu queries;
- welfare or moral meaning of any tier; or
- a full ASMP-9 resolution.

