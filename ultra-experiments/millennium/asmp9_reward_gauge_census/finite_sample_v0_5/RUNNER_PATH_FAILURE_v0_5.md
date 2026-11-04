# ASMP-9 v0.5 execution failure

## Status

```text
superseded_mechanical_failure_before_outcomes
```

The registered v0.5 runner set:

```python
REPO = HERE.parents[4]
```

For this directory layout that resolves to `C:\projects`, one parent above the
repository. The first registered invocation therefore raised
`FileNotFoundError` while attempting to read `protocol_v0_5.json`.

No protocol cell, reward ray, noisy response, information-design LP, or gate
outcome was computed. No output directory was created.

Version v0.5.1 changes only execution plumbing: a wrapper sets
`REPO=HERE.parents[3]` before invoking the byte-identical v0.5 runner. The
scientific protocol cells, seeds, thresholds, theorem, and success verdict are
unchanged.
