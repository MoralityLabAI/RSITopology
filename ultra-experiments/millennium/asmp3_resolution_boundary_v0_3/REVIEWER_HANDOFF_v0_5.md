# ASMP-3 external-review handoff

## What clears the block

There is currently a pre-review mathematical hold. First resolve the protocol
quantifier and complete-game-specification issues in
`SIMULATED_ULTRA_REVIEW_SYNTHESIS_v0_6.md`; then reseal the release. Do not
collect acceptance receipts against the current major-revision state.

The canonical acceptance policy requires two genuinely independent expert
teams to reproduce the decisive argument. One team covers
`complexity_and_game_semantics`; the other covers
`probability_noise_and_lower_bound`. At least one team must also implement and
pass a checker independently of the supplied producer and verifiers.

Model-generated reviews, anonymous placeholder identities, duplicated teams,
and mere reruns or wrappers of the supplied checkers do not qualify.

## Frozen review target

Before distributing the packet, run:

```powershell
python build_release_manifest.py
Get-FileHash -Algorithm SHA256 RELEASE_MANIFEST_v0_3.json
```

Send each team the entire directory, the canonical files referenced by the
manifest, the resulting manifest SHA-256, and
`EXPERT_REVIEW_PACKET_v0_3.md`. Each team must submit its initial verdict before
seeing the other team's review.

Any change to a manifest-bound file creates a new review target. Rebuild the
manifest and restart both reviews after any material correction.

## Required receipt

Each team submits one attributable JSON receipt below `reviews/` satisfying
`expert_review.schema.json`. It must:

1. identify the reviewer/team, expertise, and conflicts;
2. select exactly one required review track;
3. bind the exact release-manifest SHA-256;
4. attest that the initial review was independent;
5. answer all twelve end-to-end questions `yes` with substantive evidence;
6. return `accept` or `accept_with_nonmaterial_corrections`;
7. state that no material issue was found; and
8. permit repository storage.

A `no` or `unclear` answer, material issue, wrong hash, duplicate identity, or
nonaccepting verdict is non-qualifying.

## Independent-checker requirement

At least one team places its independently written checker below
`reviews/checkers/<team>/`. The checker should derive the decisive quantity
without importing or wrapping `resolution_harness.py`, `verify_result.py`, or
`verify_fourier_certificate.py`. Its receipt records:

- `implemented_by_review_team: true`;
- the artifact path relative to `reviews/`;
- the artifact's uppercase SHA-256;
- a concise method description; and
- `result: "pass"`.

The other team records an empty artifact and hash,
`implemented_by_review_team: false`, and `result: "not_run"`.

## Final adjudication

After checking the reviewers' real-world identity, expertise, independence, and
attribution, run:

```powershell
python verify_expert_reviews.py --require-complete
python run_harness.py
python verify_result.py
python verify_fourier_certificate.py
python -m pytest . -q
```

The mechanical gate must report a valid release manifest, `2/2` qualifying
end-to-end reviews, both primary tracks covered, at least `1/1` independently
implemented checker, and
`completion_gate_satisfied=true`. Human adjudication remains responsible for
detecting fabricated identities or falsely claimed independence; JSON cannot
establish those facts by itself.
