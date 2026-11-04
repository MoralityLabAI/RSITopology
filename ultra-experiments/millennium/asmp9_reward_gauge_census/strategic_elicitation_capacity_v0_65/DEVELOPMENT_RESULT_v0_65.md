# ASMP-9 strategic elicitation capacity v0.65

Status: **unregistered development result; not claim eligible**.

## Verdict

The static strategic branch has an exact finite access boundary, but its
positive randomized mechanism is established prior art.

In the deterministic outcome-only grammar, an arbitrarily interactive
protocol reduces to a menu over complete strategies.  A type subset is
strictly incentive-identifiable exactly when its members can be assigned
distinct outcomes such that each type strictly prefers its own assignment to
every other assignment.  The exact capacity is

```text
max over nonempty outcome menus A
  |{top_A(theta): theta in Theta}|.
```

For the full domain of strict rankings over `n` outcomes, this capacity is
`n`, against `n!` latent rankings.  Full strict identification is therefore
impossible in this deterministic grammar for `n>=3`.

Random problem selection changes the access class.  If a complete ranking
report is committed before a random outcome pair is drawn, and the
report-preferred member of that pair is awarded, then all `n!` rankings are
strictly elicited under expected utility if and only if every one of the
`C(n,2)` pairs has positive probability.  Omitting one pair admits a
zero-regret report that swaps only that adjacent pair.

This positive construction is explicit in Azrieli, Chambers, and Healy
(2021), *Constrained Preference Elicitation*, including the full-ranking and
random-pair example.  Version v0.65 claims no novelty for it.

## Quantitative boundary

Pure ordinal strictness has no positive uniform numerical margin.  Under the
additional normalization

```text
utility range <= 1
minimum adjacent utility gap >= delta
0 < delta <= 1/(n-1),
```

the worst false-report regret is at least

```text
delta * min_pair_weight.
```

The bound is sharp.  Uniform pair sampling is the maximin design and gives

```text
delta / C(n,2).
```

The normalization is assumed, not behaviorally validated.

## Commitment-timing boundary

The full report must be fixed before the pair draw.  If the pair is revealed
first, a correct binary response is consistent with `n!/2` full rankings.  For
`n>=3`, the response does not identify the ranking even though it selects the
best outcome from the revealed pair.

This identifies commitment timing, not randomness alone, as part of the
access primitive.

## Verification

The dedicated suite passes `10/10` tests.  The import-independent development
audit checks:

- `66` complete type domains through `n=3`;
- `4,103` deterministic direct outcome maps;
- `5,912` full-domain rankings through `n=7`;
- `5,912` report-top best-response sets;
- `15,016` true-report/false-report random-pair comparisons through `n=5`;
- `55` omitted-pair adjacent-swap witnesses through `n=7`;
- `6` sharp uniform-margin cells; and
- `6` revealed-pair equivalence-class cells.

Malformed rankings, maps, utility representations, pair keys, pair weights,
and normalized gaps fail closed.

## What this changes

The ASMP-9 access ledger now distinguishes:

```text
deterministic outcome-only protocol
  -> at most n full-ranking types strictly identified;

sealed full report + objective random problem selection
  -> all n! rankings elicited with full pair support;

pair revealed before response
  -> only one comparison identified;

dynamic target, strategic drift, audits, verified consequences, and physical
compliance
  -> still open.
```

The result narrows the static strategic obligation.  It does not establish
that a human or model obeys expected utility, commits to one reusable report,
has a stable latent ranking, treats the randomizer as objective, or responds
to awarded outcomes as the grammar assumes.

## Claim boundary

This is an exact finite specialization and access ledger beneath classical
mechanism-design and random-problem-selection theory.  It is unregistered,
not evidence about human or model behavior, and not a resolution of ASMP-9.
