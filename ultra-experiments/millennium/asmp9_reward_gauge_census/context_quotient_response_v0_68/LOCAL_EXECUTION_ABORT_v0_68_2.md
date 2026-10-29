# ASMP-9 v0.68.2 local execution preflight abort

Attempt: `20260731T043143Z-24780`

This attempt consumed no confirmation outcome:

- completed score records: `0 / 528`;
- peak GPU allocation delta: `0 MB`;
- model weights loaded: no;
- analysis run: no; and
- cleanup: passed, with no lingering owned process or GPU application.

The frozen runner rejected the additive execution registration before loading
the model because its runtime package-environment equality check received
additional host/GPU fields. The next check would also have rejected the
missing legacy `swap_bytes: 0` key. Both are registration-schema defects, not
scientific outcomes or resource-limit failures.

Canonical external attempt artifacts:

| Artifact | SHA-256 |
|---|---|
| `wrapper_summary.json` | `616d1b68d352b4bb242c63772ffd9794668293de79bdf3159acf95af543dbd63` |
| `events.jsonl` | `5b3b369d8f3323bb69b5f95063b1212b9c011592335cfb70b2681617374293f7` |
| `cleanup_summary.json` | `a253131e4ec5a561c3ea060f96cefe63fb3199144613d9f19174c67ec3c6eda4` |
| `runner.stderr.log` | `703cfb04b3f97deb8b52ad0ac798dca6b2fd8bc2fa316a7282db3685d244e924` |
| `telemetry.csv` | `d713de6d187a44e85d35af2ef712d0702a988232b8aa1c62110979a997f96cd7` |

The exact registration and authorization remain bound by
`CONFIRMATION_EXECUTION_INTENT_v0_68_2.json`. They will not be overwritten.
A retry requires a new output root, additive repair, registration,
authorization, and prereveal intent committed before any forward pass.
