# ASMP-9 target interface v0.76

This additive correction separates target recovery from representative
insensitivity.

```powershell
python -m pytest -q test_target_interface.py
python verify_development.py
```

For target `T` and observation `O`:

```text
T factors through O -> target recoverable;
O factors through T -> representative-insensitive;
both                -> exact partition match.
```

All four combinations are realized by exact finite fixtures. The distinction
clarifies, rather than invalidates, the stricter v0.69 and v0.74 interfaces.

This is classical finite factorization, not behavioral validation or an
ASMP-9 resolution.
