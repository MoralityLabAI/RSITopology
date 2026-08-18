# ASMP-9 v0.49.1 verification-universe repair

## Trigger

The frozen v0.49 verification protocol expected all `168` monotone Boolean
functions on four variables. The executor correctly enforced

```text
B(empty)=0,
```

which is mandatory for a Buehler subset table because
`P_theta(empty)=0` cannot exceed `alpha>0`. This excludes exactly the
constant-one monotone function.

The executed universe therefore contained:

```text
168 - 1 = 167 tables
167^2 = 27,889 ordered pairs.
```

Every theorem comparison on that universe matched. Gate D0 failed only because
the registration expected `168` and `28,224`.

The original registration, executor, and failed receipt remain immutable.

## Permitted repair

Version v0.49.1 changes only the universe-count adjudication:

```text
expected admissible Buehler tables = 167
expected ordered pairs = 27,889.
```

The repaired verifier may pass only if:

1. the original registration hash matches;
2. the original failed verification receipt hash matches;
3. every original registered source hash matches;
4. every original gate except D0 passed;
5. D0 failed;
6. the original table and pair counts are exactly `167` and `27,889`;
7. tight-DAG mismatches are zero;
8. common-chain mismatches are zero;
9. the minimal witness, gauge, v0.48 recovery, tests, and resource gates all
   passed; and
10. the original expected count was exactly the uncorrected Dedekind count
    `168`.

No theorem value, witness, test result, or enumeration row may change.

## Claim boundary

This is a post-outcome universe-definition repair. It cannot create new
theorem evidence or strengthen the claim. It only distinguishes the
Buehler-admissible monotone universe from the full Dedekind universe.
