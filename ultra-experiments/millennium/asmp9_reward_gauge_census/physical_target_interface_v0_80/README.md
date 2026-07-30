# ASMP-9 controlled physical target interface v0.80

Status: **prereveal registration; outcomes have not been executed**.

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

No outcome directory is included in the prereveal commit. A future pass would
validate only this controlled softmax-planner channel, not human/model values
or ASMP-9.
