# When noisy preference access becomes informative

## Result

After potential shaping has been quotiented into bounded primitive
cycle-return rays, freeze the scale-invariant response channel:

```text
P(Y=1 | sign=+1) = 1-eta,
P(Y=1 | sign= 0) = 1/2,
P(Y=1 | sign=-1) = eta,
```

with known `0<=eta<1/2` and conditionally independent responses.

The exact coefficient-width theorem from v0.4 remains the finite-sample
liveness boundary:

```text
W*(B) = 1      for B in {1,2},
        B-1    for B>=3.
```

Below `W*(B)`, a distinct reward-ray pair has identical response laws under
every adaptive experiment, so no sample size can drive worst-case
identification error below `1/2`. At `W*(B)`, an adaptive coordinate/Farey
search identifies every bounded ray with finite worst-case sample complexity.

## Finite-sample bounds

Let:

```text
K(d,B)=d+(d-1)(2+ceil(log2 |F_max(1,B-1)|)).
```

Repeating each of the at most `K(d,B)` logical comparisons:

```text
n=ceil(8 ln(2K/alpha)/(1-2eta)^2)
```

times gives a constructive response bound:

```text
T <= K(d,B) n.
```

Conversely, Fano's inequality and the channel capacity
`1-h2(eta)` give:

```text
T >=
((1-alpha)log2 |P(d,B)| - h2(alpha))
/(1-h2(eta)).
```

The bounds agree in their dependence on dimension, reward resolution, and
near-random channel degradation up to logarithmic factors. The upper bound is
conservative; it is not advertised as an exact finite-sample constant.

## Adaptivity changes the access cost

At the critical width in two dimensions, candidate nonnegative ratios form
the Farey path `F_B`. Consecutive candidates can be separated only by an
admissible endpoint threshold, and each threshold is incident to at most two
adjacent pairs.

Therefore every fixed nonadaptive design needs:

```text
Omega(|F_B|)=Omega(B^2)
```

responses at fixed channel and confidence, whereas adaptive Farey search has
`O(log B)` logical depth and `O(log B log log B)` responses under the simple
repetition rule. This is an access/adaptivity separation inside the frozen
model, not a claim that interventions dominate in every reward-learning
setting.

## Prospective verification

The v0.5 runner first failed before reading its protocol because its repository
root was one directory too high. That failure is preserved. Version v0.5.1
changed only the path wrapper; no scientific cell, seed, threshold, or gate
changed.

The corrected prospective run produced:

- 2,658 fresh every-ray constructor checks;
- 6,144 seeded rays in dimensions 4, 8, and 16;
- 1,280 seeded noisy trials, with zero observed errors;
- four fresh information-design cells, each zero below and positive at the
  theorem width;
- exact Farey adjacency certificates for every `B=33..64`;
- all eight runtime gates passed;
- the independent artifact verifier passed; and
- all 82 development and theorem tests passed.

The zero empirical errors are calibration of the implementation, not proof of
the probability bound. The written argument carries the theorem.

## ASMP-9 contribution and remaining gap

This supplies a finite-sample theorem for one known stochastic preference
channel and a sharp access-width/adaptivity boundary. It still does not resolve
ASMP-9.

Remaining obligations include:

1. discounted potential shaping and the maximal invariance group under that
   operator;
2. policy- or demonstration-based access rather than direct cycle
   comparisons;
3. unknown response parameters;
4. robustness to dependence and behavioral misspecification; and
5. a no-go theorem when inconsistent demonstrators admit no coherent scalar
   value object.

The theorem combines classical Farey search, noisy comparison, and
information-theoretic arguments. Novelty is not claimed.
