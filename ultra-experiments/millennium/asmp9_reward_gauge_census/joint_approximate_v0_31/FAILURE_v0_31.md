# ASMP-9 joint approximate run status v0.31

**Status:** `unavailable_resource_meter_failure_before_output`

The registered v0.31 runner was invoked against registration SHA-256:

```text
4a3d57e5c71335d157fe3e1bd65a4f0b184515dc3be06a143bcca3f019b81379
```

It completed the in-memory scientific calculations and then raised:

```text
OSError: GetProcessMemoryInfo failed
```

before writing `result_v0_31.json` or `run_receipt_v0_31.json`. The created
output directory contained zero files. Therefore v0.31 produced no
claim-eligible scientific result.

The defect is isolated to the Windows resource helper. Unlike the working
v0.30 helper, the v0.31 call did not declare the native handle return type or
the `GetProcessMemoryInfo` argument types. Registered scientific source,
protocol, thresholds, fixtures, and gates remain immutable.

Version v0.31.1 may repair only this resource query by importing the registered
runner and replacing `peak_resident_bytes`. It may not copy, edit, or
reimplement the scientific path.
