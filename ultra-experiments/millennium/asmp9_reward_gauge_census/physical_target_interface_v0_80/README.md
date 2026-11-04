# ASMP-9 controlled physical target interface v0.80

Status: **prospectively registered and executed; R0 failed**.

This package implements the v0.79 next-evidence gate using a controlled
finite-MDP softmax demonstrator.

Prereveal validation:

```powershell
python -m pytest -q test_physical_target.py
python register_v0_80.py
```

Registered execution, only after the registration commit is pushed:

```powershell
python execute_registered.py `
  --registration registration_v0_80.json `
  --output-dir <fresh-output-directory>
```

The executor validates every prereveal source hash, produces a primary run and
byte-identical replay, then applies the frozen gate sequence.

The prereveal commit contains no outcomes. The later
[result](RESULT_v0_80.md) and [independent audit](AUDIT_v0_80.md) import the
hash-matched execution artifacts. W0 and I0 passed; R0 failed; L0 and M0 are
`not_evaluated`.

This controlled negative result does not identify human/model values or
resolve ASMP-9.
