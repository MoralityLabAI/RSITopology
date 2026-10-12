# ASMP-9 v0.20 block factorization

This successor asks whether the exact finite residual-liveness object from
v0.17-v0.19 decomposes beyond cactus cores.

The candidate theorem is:

```text
global quotient liveness
iff
every nontrivial vertex-biconnected block is residual-strongly-connected.
```

Under independent edge responses this makes fixed-label availability, and
the rectangular endpoint-label minimum, products of block-local factors.
Exact allocation *between* blocks then uses Bellman recursion once exact local
tables are supplied.

## Current status

Development evidence has passed on burned cells. The registered cells must
not be executed until the implementation freeze and separate registration
commits exist.

This version deliberately does not solve the local design problem inside a
general overlapping-cycle block. The one-block negative control makes that
non-contribution executable.

## Development checks

```powershell
python -m pytest ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\test_block_factorization.py ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\test_protocol_v0_20.py -q
```

## Freeze and registration

After committing a clean implementation:

```powershell
python ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\register_v0_20.py --output ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\registration_v0_20.json
```

Commit the registration separately. Record its SHA-256. Only then run:

```powershell
python ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\run_verification_v0_20.py `
  --protocol ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\protocol_v0_20.json `
  --registration ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\registration_v0_20.json `
  --registration-sha256 <FROZEN_SHA256> `
  --result ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\artifacts_v0_20\result_v0_20.json `
  --receipt ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\artifacts_v0_20\run_receipt_v0_20.json
```

Then independently verify:

```powershell
python ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\verify_result_v0_20.py `
  --protocol ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\protocol_v0_20.json `
  --registration ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\registration_v0_20.json `
  --result ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\artifacts_v0_20\result_v0_20.json `
  --receipt ultra-experiments\millennium\asmp9_reward_gauge_census\block_factorization_v0_20\artifacts_v0_20\run_receipt_v0_20.json
```

## Claim boundary

Read `PROTOCOL_v0_20.md` and `protocol_v0_20.json`. No outcome from this
directory is a general reliability-design result, adaptive access theorem,
behavioral reward-identification result, general IRL result, or resolution of
ASMP-9.
