# ASMP-9 v0.68.2.1 local registration repair

Status: **prereveal registration-only repair; no confirmation outcome read**.

The v0.68.2 attempt stopped before model loading because the additive
registration extended the legacy `environment` object with host/GPU fields.
The frozen runner intentionally requires exact equality between that object
and Python/package versions. Version v0.68.2.1 therefore:

1. restores `environment` to the exact prereveal Python/package object;
2. records Windows and GPU provenance in a separate `host_environment` field;
3. restores the legacy `swap_bytes: 0` contract key; and
4. preserves the Windows page-file increase check as the operational
   invalidation rule.

No model byte, tokenizer, confirmation job, construction authorization,
endpoint, threshold, gate, or decision changes. The aborted v0.68.2
registration is immutable and remains part of the audit trail.
