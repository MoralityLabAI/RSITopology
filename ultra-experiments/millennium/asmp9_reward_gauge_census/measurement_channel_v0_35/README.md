# ASMP-9 measurement channel v0.35

The v0.34.4 physical pilot captured perfectly repeatable model probabilities
but rejected its prompt-level common ruler. This directory separates two
failure modes:

1. local departures from a nonincreasing probability-response curve; and
2. absence of endpoint support needed to force a certainty-equivalent
   crossing.

`monotone_ruler.py` proves and implements the exact `L-infinity` distance to
the nonincreasing cone. The retrospective replay is explicitly burned
development work:

```powershell
python ultra-experiments/millennium/asmp9_reward_gauge_census/measurement_channel_v0_35/analyze_v034_repair_radius.py `
  --output ultra-experiments/millennium/asmp9_reward_gauge_census/measurement_channel_v0_35/REPAIR_RADIUS_RESULT_v0_35.json `
  --report ultra-experiments/millennium/asmp9_reward_gauge_census/measurement_channel_v0_35/REPAIR_RADIUS_REPORT_v0_35.md
```

The replay shows modest repair radii but only 4/36 robust standard-gamble
crossings, 2/18 on the preferred basis, and 10/18 robust compound crossings.
Smoothing cannot manufacture the missing endpoint support.

`PILOT_PROTOCOL_DRAFT_v0_35.json` specifies the next falsification instrument:
a full presentation-order by response-code Latin square, explicit `p=0` and
`p=1` dominance endpoints, and a measurement radius derived from independent
controls. It is a draft, not a registration, and does not authorize model
queries. Its deterministic generator produces 2,412 unique prompt rows and
4,824 planned receipts across two cold starts. The content hash and per-type
counts are recorded in `DESIGN_RECEIPT_v0_35.json`; the multi-megabyte draft
manifest is regenerated rather than committed before registration.

`pilot_analyzer_v035.py` is the total evaluator for that draft. It derives its
instrument radius from semantic-equality and cold-start controls, evaluates
`C0 -> D0 -> M0 -> J0` in fixed sequence, and refuses downstream adjudication
after a failed upstream gate. Planted pass, bad-code, and nonmonotone fixtures
exercise all three paths.

## Tests

```powershell
python -m pytest tests/test_asmp9_measurement_channel_v035.py -q
```

## Claim boundary

This directory contains a classical isotonic specialization, a retrospective
burned replay, and a successor draft. None is confirmation or an ASMP-9
resolution.
