# V1 chronology and composite-record addendum

Date: 2026-07-14

## Immutable v1 status

No v1 protocol, result, receipt, seal, or release byte has been modified. This
addendum records two limitations found during independent package review and
the prospective v2 correction.

## Forward anchor

The exact existing release
`RSITopology_recursive_protocol_and_measurement_v1_20260714.zip` has SHA-256:

```text
31e678e94010d611f84d86216e6e3a529d08cbedc14fd2d7da7c80136fd7be7f
```

At `2026-07-14T15:51:04Z`, that exact digest was submitted through
`javascript-opentimestamps` 0.4.5 to four external calendars. The initial OTS
proof is 630 bytes with SHA-256:

```text
cf4ff1325e69e7411fa9ea8ec56887c678f19e311ba4b41fb58ba084e2aa87ac
```

The proof currently contains pending attestations from the Alice, Bob,
Eternity Wall, and Catallaxy calendars. It is **not yet independently
Bitcoin-verifiable**. After the calendars publish their commitments, an
upgraded versioned proof can establish that these release bytes existed no
later than the attesting Bitcoin block. The initial proof is preserved and
will not be overwritten.

This is a forward anchor only. It cannot prove that the v1 protocol hash
predated the v1 run. That chronology gap remains an explicit v1 limitation.
V2 closes it prospectively with an externally verified protocol/environment
pre-anchor and an externally submitted run-receipt post-anchor.

## Composite G1 legibility

V1's composite `G1_atlas` record surfaced
`unavailable_insufficient_prompt_families / not_evaluated`, while its separately
registered measurement component had a valid scientific `fail`. The v1
prompt-corpus consequence remained correct (`do_not_invest_stop_branch`), but a
reader of only the composite record could miss the decisive measured failure.

V2 does not rewrite v1. It registers all 25 ordered pairs of component states
in `{pass, fail, inconclusive, unavailable, invalid}`. Because the composite is
a conjunction of necessary components, any valid component failure makes the
composite fail. Every component keeps its own consequence entry; no dominant
component or severity ranking is selected.

For the v1-observed state pair, v2 would emit:

```text
measurement_component = fail
prompt_component = unavailable
composite_decision = fail
stop_reasons = [measurement_component_fail, prompt_component_unavailable]
```

## Two disclosure clarifications

The measurement protocol froze the structured-null seeds and the audit ceiling
of `256/4096` before execution under its internal hash chain. The observed
`255/4096` result passed by one draw. Because v1 lacks an external pre-run
anchor, the package proves internal consistency but not preregistration time.

The deterministic replay compared six files: five outputs bound inside
`run_receipt.json`, plus `run_receipt.json` itself. The five output hashes and
the receipt hash were all byte-identical between canonical and replay runs.

## Canonical anchor artifacts

- Proof: `RSITopology_recursive_protocol_and_measurement_v1_20260714.zip.ots`
- Receipt: `artifacts/v1_forward_anchor_20260714_v2/anchor_receipt.json`
- Proof inspection: `artifacts/v1_forward_anchor_20260714_v2/ots_info.txt`
- Verification output: `artifacts/v1_forward_anchor_20260714_v2/ots_verify.txt`

The earlier `artifacts/v1_forward_anchor_20260714/` receipt is preserved. The
v2 receipt adds the independently captured verification-command output and
role-specific chronology language without changing either the release or its
OTS proof.
