# ASMP-3 v2.6 external review handoff

## Review target

The review target is the v2.6 disposition and its manifest-bound evidence, not
the superseded v0.3 conditional packet. Reviewers must separately adjudicate:

1. the v0.7 frozen-game total-variation separation and honest/noise scope;
2. the v2.5 nonbinding-`Refute` necessity separation;
3. the witness-transparent extraction theorem and its limits; and
4. the conclusion that these refute the named iff without completing the
   broader classification program.

## Required independent tracks

- `complexity_and_game_semantics`
- `probability_noise_and_lower_bound`

Two attributable independent teams are required. At least one must implement a
checker that derives a decisive quantity without importing or wrapping any
producer or supplied verifier.

## Questions each team must answer

1. Is the task/game family legal under the identified v0.1 reading?
2. Does v0.7 keep efficient honest work and the declared nonzero noise in scope?
3. Is `(3/5)^d` the optimal full frozen-game gap, not just one decoder's value?
4. Does v2.5's protocol truly avoid all `Refute` lookups?
5. Are the padded atoms distinct local classes rather than aliases or macros?
6. Is the padded relation sound and covering with minimum exactly `T`?
7. Does the empty decidable relation force dimension infinity literally?
8. Is `alpha>=1-s-delta` valid and sharp under the declared coupling?
9. Are all finder, message, query, and verifier costs charged?
10. Does any benign encoding invalidate a counterexample?
11. Does the evidence refute the named iff under both principal readings?
12. Does any evidence justify claiming the unrestricted classification complete?

The expected answer to question 12 is “no”; an accepting review of v2.6 accepts
the scoped disposition, not an overclaim of full resolution.

## Mechanical rerun

```powershell
python run_resolution_disposition.py
python verify_resolution_disposition.py
python build_release_manifest.py
python -m pytest . -q
```

Real-world identity and independence still require human adjudication.
