# ASMP-9 access Set Cover reduction v0.78

This CPU-only package reduces finite Set Cover to exact target-access design.

```powershell
python -m pytest -q test_access_set_cover.py
python verify_development.py
```

The construction adds one mandatory anchor query and one binary query per
candidate set:

```text
minimum access size = 1 + minimum cover size.
```

The frozen optimum is `2 -> 3`, and 48 seeded small registries verify the
shift, including infeasible cases.

This is a classical worst-case NP-hardness specialization, not evidence that a
natural behavioral interface is hard or an ASMP-9 resolution.
