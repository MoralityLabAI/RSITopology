# ASMP-3 blocked audit v0.6

## Status

ASMP-3 is blocked at two layers:

```text
conditional_probability_lower_bound = proved_and_machine_checked
complete_canonical_game_specification = missing
protocol_quantifier_scope = unresolved
simulated_complexity_review = major_revision
qualifying_external_reviews = 0/2
qualifying_external_clean_room_checkers = 0/1
```

## Mathematical/scope block

The exact harness proves that persistent independent per-atom flips of rate
`1/5` give a parity decision gap `(3/5)^d`, despite the displayed single-atom
condition `a_H(k)<=1/5`.

It does not prove that the parity-only observation model is the entire
canonical game. The v0.1 statement says that a task family “admits” a protocol.
If this is existential over admissible transcript encodings, advocates can
send all `d=log2(T)` semantic bits; a verifier selects a differing coordinate
and queries it once, obtaining gap `3/5`. The current countermodel excludes that
protocol only by stipulating a parity-only grammar.

A material repair must:

1. define the complete family `G_n`, including `R_n`, `T(n)`, inputs, semantic
   worlds, oracle access, information sets, payoff, and non-power-of-two
   padding;
2. freeze the exact canonical message alphabet, serialization, rounds, stopping
   rule, public coins, malformed/abort behavior, and budgets;
3. settle whether transcript grammar is task data or existential protocol
   choice;
4. prove `r_R` over every false admissible transcript;
5. prove one uniform efficient honest strategy against every legal randomized,
   adaptive, malformed, equivocating, or aborting strategy; and
6. prove full-transcript noninterference/data processing, including every
   encoding, alias, ordering, query schedule, coin, and stopping event.

The simulated ultra probability review accepted the conditional channel
calculation after finite-edge and transcript-identity corrections. The
simulated ultra complexity/game review returned `major_revision`. Neither is a
qualifying external receipt.

## External-acceptance block

After the mathematical repair is complete and the release is resealed, the
canonical policy still requires two genuinely independent expert teams to
reproduce the end-to-end decisive argument. Each team must answer all twelve
review questions. One must implement and pass a clean-room checker.

Model-generated reviews, duplicate identities, self-attestation without
real-world provenance, and another repository-local checker do not satisfy this
condition.

## Convincing stopping argument for the present harness

Increasing `d`, adding more parity rows, or rerunning the enumerative/Fourier
checkers cannot decide the protocol quantifier or instantiate missing game
semantics. Every such computation remains inside the same reduced Markov
experiment whose formula is already exact. Work on the current grid should
stop until the formal specification/scope issue is resolved.

## Exact unblock path

1. Complete and independently audit the six mathematical/scope repairs above.
2. Remove the pre-review hold in `EXPERT_REVIEW_PACKET_v0_3.md`.
3. Rebuild `RELEASE_MANIFEST_v0_3.json` and distribute its exact SHA-256.
4. Obtain two attributable independent end-to-end reviews on that same hash.
5. Store one clean-room checker and its hash below `reviews/checkers/`.
6. Human-adjudicate identity, expertise, independence, and checker execution.
7. Run:

   ```powershell
   python verify_expert_reviews.py --require-complete
   python run_harness.py
   python verify_result.py
   python verify_fourier_certificate.py
   python -m pytest . -q
   ```

Until both layers are cleared, marking ASMP-3 resolved would overstate what the
harness proves and contradict the frozen acceptance policy.
