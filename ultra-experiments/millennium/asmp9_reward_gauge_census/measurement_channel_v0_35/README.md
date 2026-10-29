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

`PILOT_PROTOCOL_DRAFT_v0_35.json` preserves the design-stage record.
`PILOT_PROTOCOL_v0_35.json` freezes the resulting scientific instrument: a
full presentation-order by response-code factorial, explicit `p=0` and `p=1`
dominance endpoints, and a measurement radius derived from independent
controls. The protocol still does not authorize a model query. Its
deterministic generator produces 2,412 unique prompt rows and 4,824 planned
receipts across two cold starts. The content hash and per-type counts are
recorded in `DESIGN_RECEIPT_v0_35.json`; the multi-megabyte manifest is
regenerated and changed from draft to authorized only by the environment
registration tool.

`pilot_analyzer_v035.py` is the total evaluator. It derives its
instrument radius from semantic-equality and cold-start controls, evaluates
`C0 -> D0 -> M0 -> J0` in fixed sequence, and refuses downstream adjudication
after a failed upstream gate. Its CLI requires the environment registration
and completed capture directory, revalidates the sealed implementation,
manifest, capture summary, and every individual receipt, and emits a
write-once hash-bound result.

`run_measurement_pilot_v035.py` is a narrow adapter over the sealed v0.34
capture engine. It rejects a draft or unauthorized manifest and preserves one
hashed receipt per request. `prepare_registration_v035.py` uses
compare-or-fail semantics to materialize the exact prompt manifest and bind the
actual model, server, CUDA library, implementation files, source evidence,
Git state, and resource envelope. The registered wrapper
`scripts/run_prime_asmp9_measurement_v035_guarded.sh` fixes 4 GiB RAM, zero
swap, 50% CPU, 50 MB/s I/O, 1,600 MB incremental VRAM, an 88 C hard abort, and
a 30-minute wall-time cap.

These files make the pilot preregistration-ready; they are not an
environment-bound registration. No v0.35 model query has been executed.

## Environment registration and launch

On the exact execution host, start from a clean checkout of the scientific
protocol commit. After the model and registered `llama.cpp` build exist:

```bash
python3 ultra-experiments/millennium/asmp9_reward_gauge_census/measurement_channel_v0_35/prepare_registration_v035.py \
  --model-path /workspace/asmp9_measurement_v035/model/Qwen3.5-0.8B-Q4_K_M.gguf \
  --server-path /workspace/llama.cpp/build-sm89/bin/llama-server \
  --cuda-library-path /workspace/llama.cpp/build-sm89/bin/libggml-cuda.so.0.17.0 \
  --prepared-utc 2026-07-29T00:00:00Z \
  --pod-id REPLACE_ME \
  --gpu-description "REPLACE_ME" \
  --listed-hourly-usd 0.00
```

The timestamp and environment values above are placeholders and must describe
the actual host. The preparer refuses a dirty worktree and unequal existing
artifacts. Commit and push the generated manifest and registration before
launch; that Git ordering is the public preregistration chronology.

Then export exactly the `exact_launch_environment` recorded in the
registration and invoke its `exact_launch_command`. Do not edit the generated
registration or relax wrapper caps. Analyze the completed directory with:

```bash
python3 ultra-experiments/millennium/asmp9_reward_gauge_census/measurement_channel_v0_35/pilot_analyzer_v035.py \
  --registration ultra-experiments/millennium/asmp9_reward_gauge_census/measurement_channel_v0_35/measurement_pilot_registration_v035.json \
  --output-dir /workspace/asmp9_measurement_v035/output \
  --output /workspace/asmp9_measurement_v035/output/analysis_v035.json
```

## Tests

```powershell
python -m pytest tests/test_asmp9_measurement_channel_v035.py -q
```

## Claim boundary

This directory contains a classical isotonic specialization, a retrospective
burned replay, a frozen scientific protocol, and execution scaffolding. It
contains no v0.35 outcome and is neither confirmation nor an ASMP-9
resolution.
