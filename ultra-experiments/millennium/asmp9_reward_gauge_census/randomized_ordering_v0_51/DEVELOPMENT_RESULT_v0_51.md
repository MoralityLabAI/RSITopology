# ASMP-9 v0.51 randomized-ordering development result

## Status

**Exact finite instrument derived and tested; complete census not yet
registered or run.**

The direct prior-art audit found that the central construction is already
known: randomized minmax regret for combinatorial optimization is a finite
zero-sum game. Version v0.51 therefore claims no new minimax machinery. It
specializes that machinery to decision-relative Buehler evidence ordering and
tests the exact boundary between certification and compromise.

## Exact object

For ordering `pi` and objective/reference scenario `s`, define nonnegative
regret

```text
A(pi,s)
  = C_s(pi) - min_sigma C_s(sigma).
```

The optimizer chooses a distribution `p` over orderings; the adversary
chooses a scenario. Exact rational LP vertex enumeration returns:

- the minimum randomized worst-case regret;
- a primal distribution over orderings;
- a dual least-favorable distribution over scenarios;
- exact primal/dual equality; and
- complementary-slackness support receipts.

## Zero-regret boundary

Randomization has zero regret if and only if every ordering in its support is
optimal in every scenario. Since all regret entries are nonnegative, mixing
cannot cancel incompatible positive entries.

Thus:

```text
randomized value = 0
  iff
deterministic common-optimum intersection is nonempty.
```

Randomization may improve approximate minimax performance. It cannot
manufacture exact decision-relative identity when the common-chain
certificate fails.

## Minimal strict-gain control

The v0.50 reference-switch witness induces regret matrix

```text
          left   right
(x,y)       0     1/2
(y,x)      1/2     0.
```

Exact values:

```text
deterministic minimax regret: 1/2
randomized minimax regret:    1/4
randomization gain:           1/4
primal mixture:              (1/2,1/2)
dual mixture:                (1/2,1/2).
```

This is the smallest strict-gain control: one ordering leaves nothing to
mix, and one scenario has a deterministic zero-regret optimum.

## Verification

Seven development tests pass. They cover:

- exact primal/dual strategies on the minimal game;
- strict gain without false zero-regret certification;
- zero value exactly when a common deterministic optimum exists;
- complementary slackness on planted two- and three-outcome fixtures;
- rectangular and degenerate games; and
- all 81 payoff matrices in `{0,1/2,1}^{2x2}` against an independent direct
  breakpoint calculation.

```text
7 tests passed
```

A disclosed, burned performance pilot ran the first 20 lexicographic table
pairs from the v0.50 universe:

```text
elapsed: 3.3718 seconds
projected full 361-pair census: 60.86 seconds
strict-gain rows in burned prefix: 6
```

The burned prefix is for capacity planning only. Its strict-gain count is not
confirmation evidence and must not enter a gate.

## Prospective census target

The complete successor should retain the v0.50 universe:

```text
19 admissible monotone tables
361 ordered objective pairs
2 reference vertices
6 orderings
4 scenarios per pair.
```

Every pair must pass exact primal/dual, complementary-slackness, zero-support,
and deterministic-dominance checks. The complete strict-gain count and gain
distribution are outcomes, not thresholds.

## Claim boundary

Mastin, Jaillet, and Chin directly subsume the randomized-minmax construction
and prove stronger algorithmic results. Version v0.51 is an exact Buehler
specialization and audit instrument. It does not establish novelty,
large-width efficiency, operational desirability of randomized reporting,
continuous or strategic robustness, physical preference access, or an
ASMP-9 resolution.
