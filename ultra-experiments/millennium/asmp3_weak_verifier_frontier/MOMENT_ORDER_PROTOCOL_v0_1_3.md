# Minimum certifying moment order protocol v0.1.3

## Status

This is a post-result exact characterization prompted by review of v0.1.2. It
is not a preregistered empirical experiment and does not alter v0.1 through
v0.1.2.

## Frozen reference

Let `S` be the error count among nine judgments. Freeze the reference moments
to those of `Binomial(9,1/5)`:

```text
E[(S)_j] = (9)_j (1/5)^j,    j=1,...,9,
```

where `(x)_j` is the falling factorial. For each order `m`, consider every
count law on `{0,...,9}` matching moments `j=1,...,m` and normalization.
Conditional uniformity over bitstrings of the same count converts every such
law into an exchangeable nine-bit joint law.

Define

```text
U_m = max P(S>=5)
```

over that moment class. The certification target is `U_m <= 1/20`.

## Required exact certificates

1. Enumerate all LP vertices with support size at most `m+1` using rational
   arithmetic for `m=1,...,9`.
2. At `m=3`, verify the feasible witness

```text
P(S=0,2,3,5) = (136/625, 84/125, 6/125, 39/625),
```

which has tail `39/625 > 1/20`.
3. At `m=4`, verify the dual inequality

```text
1{S>=5} <= (S)_4/120
```

for every count `S=0,...,9`, giving upper bound `126/3125 < 1/20`.
4. Verify sharpness at `m=4` with

```text
P(S=0,1,2,3,5)
= (404/3125, 207/625, 144/625, 168/625, 126/3125).
```

5. Report the minimum certifying order as four only if the order-three witness
   and order-four primal/dual certificates all pass exactly.

## Claim boundary

The result concerns one independent-reference moment sequence, not arbitrary
panels. It assumes exchangeability and exact knowledge of falling-factorial
moments. It does not say that four moments suffice for other marginal error
rates, panel sizes, thresholds, selected-query distributions, or real judges.

