# ASMP-9 v0.42 registered execution failure

## Status

`implementation_failure_no_scientific_result`

The first execution from registration commit
`99aff69341b3388b53882fde72b29f16a23b0b28` stopped before seed derivation,
sampling, empirical-channel construction, or polytope compilation.

The sealed registration stored the practical margin as the exact rational
string:

```text
1/1000
```

The executor incorrectly called:

```python
float(value)
```

instead of parsing the string as a rational first. Python therefore raised:

```text
ValueError: could not convert string to float: '1/1000'
```

No `artifacts_v0_42/RESULT_v0_42.json` was created. The exact hashes of the
registration and stdout/stderr logs are frozen in
`FAILED_EXECUTION_v0_42.json`.

## Consequence

No scientific gate was evaluated and no claim can be made from v0.42. The
sealed source and registration are not edited. A versioned v0.42.1 repair must:

1. parse rational margin strings with `Fraction`;
2. add an executor-level regression test using the actual registered value;
3. create and publish a new environment lock and registration; and
4. derive a fresh seed from the new registration bytes.
