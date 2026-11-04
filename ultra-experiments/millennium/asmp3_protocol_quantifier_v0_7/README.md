# ASMP-3 protocol-quantifier successor v0.7

This successor addresses the material findings from the v0.6 simulated
complexity review:

- it specifies the complete parity witness game;
- it enumerates all terminal claim types relevant to `r_R`;
- it gives a pointwise uniform-honest-strategy proof;
- it freezes canonical serialization and removes transcript side channels;
- it proves the full adaptive transcript is a Markov kernel of the persistent
  noisy vector; and
- it constructs the richer bit-vector protocol when message encoding is an
  existential protocol choice.

The exact conclusion is a fork:

```text
frozen encoding:       optimal gap = (3/5)^d -> 0
existential encoding:  explicit constant gap = 3/5
```

Run:

```powershell
python run_protocol_quantifier.py
python verify_protocol_quantifier.py
python build_release_manifest.py
python -m pytest . -q
```

This removes “run a larger parity grid” from the unblock path. Remaining
acceptance work is an authoritative scope adjudication followed by two genuine
independent end-to-end expert reproductions. The exact scope-review request is
in `SCOPE_ADJUDICATION_PACKET_v0_7.md`.
