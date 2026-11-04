# ASMP-6 finite semantic-collusion frontier result v0.1

## Verdict

`finite_registry_frontier_established`

All six frozen gates passed. The exact census covered 35 encoder laws, 1,225
ordered encoder pairs, 256 active-audit maps, and 40 frontier cells. This is the
first problem-ID-bound experiment for `ASMP-6`; it does not resolve the full
problem.

## Headline result

The covertness definition changes the answer discontinuously at zero declared
detectability:

| Covertness constraint | Audit charge | Optimal worst-message error |
|---|---:|---:|
| message-averaged TV = 0 | 0 | 0 |
| per-message TV = 0 | 0 | 1/2 |
| message-averaged TV = 0 | 1 | 1/4 |
| message-averaged TV = 0 | 2 | 1/2 |

Thus the mixture-only game admits a perfectly reliable one-bit channel whose
message average is exactly the benign cover law. The stronger per-message game
admits no information at the same zero-TV boundary. In this registry,
message-averaging manufactures the apparent zero-detectability payload.

The active-audit frontier is also exact. For message-averaged TV zero, allowing
one changed-symbol audit raises minimax error from `0` to `1/4`; allowing any
map that changes at most two symbols raises it to `1/2`. More permissive
detectability regions retain some reliability at charge two, but every regime
is at chance by charge four.

## Full exact frontier

Each row lists minimax error across all public deterministic audit maps whose
charge does not exceed the column.

| Covertness | TV cap | b=0 | b=1 | b=2 | b=3 | b=4 |
|---|---:|---:|---:|---:|---:|---:|
| mixture | 0 | 0 | 1/4 | 1/2 | 1/2 | 1/2 |
| mixture | 1/8 | 0 | 1/4 | 3/7 | 1/2 | 1/2 |
| mixture | 1/4 | 0 | 1/4 | 3/7 | 1/2 | 1/2 |
| mixture | 1/2 | 0 | 1/4 | 3/7 | 1/2 | 1/2 |
| per-message | 0 | 1/2 | 1/2 | 1/2 | 1/2 | 1/2 |
| per-message | 1/8 | 1/2 | 1/2 | 1/2 | 1/2 | 1/2 |
| per-message | 1/4 | 1/4 | 3/8 | 1/2 | 1/2 | 1/2 |
| per-message | 1/2 | 0 | 1/4 | 3/7 | 1/2 | 1/2 |

The flat per-message rows at caps `0` and `1/8` are a grid fact: with
quarter-increment encoder probabilities, the only eligible pair in both cells
is the benign cover law for each message.

## Gate record

- `G0_registration_binding`: pass.
- `G1_complete_census`: pass.
- `G2_covertness_definition_separation`: pass.
- `G3_full_audit_kill`: pass.
- `G4_audit_monotonicity`: pass in every covertness stratum.
- `G5_dual_chi_squared_support`: pass. Both rational chi-squared orientations
  were kept distinct, and support failures were not smoothed away.

Nineteen encoder pairs have exactly the benign message-averaged law. The
cover-first chi-squared quantity is finite for 471 of 1,225 pairs; the reverse
quantity is finite for all pairs because the frozen cover has full support.

## Interpretation

The experiment validates an access-class instrument, not a new coding theorem.
It shows concretely why a collusion-capacity claim must say whether covertness
is message-averaged or messagewise and how an active auditor is charged. The
finite active-audit curve is useful to Blue Beam as a synthetic regression
target: a detector that reports only the averaged transcript law misses a
perfectly reliable registered channel, while a charged perturbation test can
destroy it.

## Claim boundary

This is exact/certified evidence for one four-symbol registry. It is not an
asymptotic capacity theorem, a square-root-law test, a cryptographic lower
bound, evidence of LLM collusion, or a released collusion policy. The registry
contains no language, token mapping, learned encoder, preshared key, or adaptive
history. No current result resolves `ASMP-6`.
