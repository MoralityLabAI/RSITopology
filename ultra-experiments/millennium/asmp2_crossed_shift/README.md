# ASMP-2 crossed-shift continuation pilot

This directory implements the smallest exact experiment proposed in the
bounded ASMP round robin. It separates local tangent spanning from global
continuation in one two-dimensional Bernoulli family.

The analytic statement is primary. The registered runner is an independent
finite-arithmetic implementation check and must be reported as
`instrument_valid_forced_construction`, never as empirical support for a
general shift-certification theorem.

The optional higher-dimensional active-design sweep is not registered here.

## Pre-outcome checks

```powershell
python -m pytest test_crossed_shift.py -q
```

## Claim-eligible run

Run only after the protocol, claim packet, runner, verifier, and tests are
committed:

```powershell
python run.py --protocol protocol_v0_1.json --output-dir artifacts
python verify_result.py --result artifacts/result_v0_1.json `
  --receipt artifacts/receipt_v0_1.json `
  --output artifacts/verification_v0_1.json
```

Outputs are write-once. Any invalid or failed gate stops the sequential ASMP
execution queue.
