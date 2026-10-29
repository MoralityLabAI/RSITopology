# ASMP-9 physical acquisition v0.34.2 local abort

## Status

`valid_resource_abort_no_scientific_result`

The prospectively registered local burned-pilot run stopped at the hard
temperature gate. It produced 162 checkpointed receipts of 1,944 required
receipts before the wrapper observed 88 C and terminated its owned process
tree. The records directory contains 169 atomic files because seven additional
write-once records landed after the last progress checkpoint. Neither count is
a complete registered census, so the frozen analyzer must not run on this
prefix.

This is not a failed scientific gate. It is a successful fail-closed resource
gate.

## Frozen inputs

- registration:
  `burned_pilot_registration_v0_34_2.json`
- registration file SHA-256:
  `2607647066d027027ec574c4b371ec5a73674356a964288c6e9fe7944a088455`
- registration content SHA-256:
  `19b675937b2799901634761cba04252899b47c27f638533bd239ce3c9d9dc02a`
- prompt-manifest SHA-256:
  `4bea162cfea512ae3ff4e513e896f37b2267ee51715da9228260f80e9c3a2c0b`
- runner SHA-256:
  `7f54b265578aa747c06e1283f0e599158e02719c60b4f4200540ac99443635c3`
- analyzer SHA-256:
  `e0835561376baa2a1b4f9b5f5d50786c08fa942a566df0e7cccff1829bb3a6e4`

## Resource result

| field | value |
|---|---:|
| elapsed seconds | 75.086 |
| checkpointed receipts | 162 / 1,944 |
| atomic receipt files | 169 / 1,944 |
| peak job RAM | 1,320.793 MB |
| peak whole-device GPU delta | 633 MB |
| peak GPU temperature | 88 C |
| thermal pauses before abort | 9 |
| thermal-pause time | 41.021 seconds |
| cleanup | passed |

The GPU returned to zero used memory after cleanup. No unrelated process was
terminated.

## External receipt hashes

Run root:

```text
D:\Research_Engine\runs\asmp9_physical_acquisition_burned_pilot_v0_34_2
```

| artifact | SHA-256 |
|---|---|
| `progress.json` | `88ec5f66f250affe42675636fecbb4b99f417eaf00aae602eccad8b1b467ecee` |
| `measurement_plan.json` | `09b814b310eee89d9251ca59cadab23fae34cc21ab4d082cbc27af945be9f62b` |
| `events.jsonl` | `803dd624af2f70948246268922d4c97b0e14a3cade401ac5c6758a1c88f9fe68` |
| `launcher_stdout.log` | `b534c1131db529294a64159a6876992f24effd0445fdf72c5a8c713b5155985a` |
| `launcher_stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `wrapper/summary.json` | `26aad78d01331bec95c06d1d5a6287bc2525b38a9e94d86274f1611b3bee7109` |
| `wrapper/cleanup_summary.json` | `7096dacc5944db0f3ceaf7583f7a669e4e30a85dd6bb9fc524a41e77f2f5c823` |

## Consequence

The partial receipts are engineering evidence only. They cannot calibrate
thresholds, enter confirmation, or be pooled with a successor run. A complete
attempt requires a versioned execution surface with the same prompt universe,
model bytes, sampling contract, and analysis contract.

