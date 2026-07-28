# Exact ties halve the sharp comparison width

## Result

After potential shaping has been quotiented into cycle-return coordinates,
consider primitive integer reward rays with coordinate bound `B`. An exact
comparison query with primitive integer normal `q` returns:

```text
sign(q dot z) in {-1,0,+1}.
```

For every dimension `d>=2`, the smallest coefficient width sufficient in the
worst case to distinguish all such reward rays is:

```text
Q0*(B) = 1      for B in {1,2},
         B-1    for B>=3.
```

The bound is dimension-independent and sharp.

## Proof idea

Coordinate queries recover signs and zero locations. Any remaining distinct
pair differs in an absolute coordinate ratio. Reduced ratios with numerator
and denominator at most `B` are separated by thresholds from the Farey
sequence of order `B-1`; an exact tie can identify a Farey endpoint.

For `B>=3`, the pair

```text
z  = (B,   B-1),
z' = (B-1, B-2)
```

cannot be separated below width `B-1`. The query `(B-2,-(B-1))` attains the
bound with scores `-1` and `0`.

## The ambiguity discontinuity

Together with the corrected v0.3.1 theorem:

```text
delta = 0:       Q0*(B) = B-1     for B>=3;
0 < delta < 1:   Q*(B)  = 2B-1    for B>=2.
```

Thus an arbitrarily small positive adversarial threshold radius nearly doubles
the worst-case query expressivity required. The benefit at `delta=0` comes
entirely from observing exact ties.

## Prospective verification

The theorem, constructor, protocol, tests, and runner were committed before
the fresh verification run.

- 5,205,885 full-grid ray pairs checked;
- every-pair cells at `d=2,B=9..16`, plus fresh `d=3` and `d=6` cells;
- 12,288 additional seeded high-dimensional pairs;
- exhaustive lower-witness search for bounds 129 through 160;
- all six runtime gates passed;
- the independent artifact verifier passed; and
- all 36 theorem tests passed.

The written Farey proof carries the theorem. The finite run verifies its
implementation and extremal branches.

## ASMP-9 contribution and remaining gap

This closes the exact-tie coefficient-width subproblem for one direct
cycle-coordinate comparison grammar. It does not resolve ASMP-9.

Still open are:

1. minimum query counts rather than coefficient width alone;
2. finite-sample recovery under a declared stochastic preference model;
3. discounted potential shaping;
4. identification from policies or demonstrations rather than direct
   trajectory comparisons; and
5. robust positive or no-go results for inconsistent or misspecified
   demonstrators.

The proof is a classical Farey-sequence specialization. Novelty is not claimed.
