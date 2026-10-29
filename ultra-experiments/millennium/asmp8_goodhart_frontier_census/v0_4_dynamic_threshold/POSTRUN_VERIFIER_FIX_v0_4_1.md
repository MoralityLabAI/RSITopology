# ASMP-8 v0.4.1 post-run verifier fix

The registered v0.4 claim runner completed successfully, but the subsequently
invoked registered verifier failed before reading any outcome:

```text
ImportError: cannot import name 'CDF_FIELDS' from 'run'
```

`dynamic_threshold.py` prepends the v0.3 source directory to `sys.path` so it
can reuse the frozen registry. The verifier then executed the generic import
`from run import ...`, which resolved to the v0.3 runner rather than the local
v0.4 runner.

The registered verifier is preserved byte-for-byte under its registration
hash. The additive `verify_result_postrun_v0_4_1.py` duplicates the three
already-frozen CSV field lists locally and performs the intended replay. It is
explicitly labeled post-run and was not prospectively registered.

This packaging defect does not change the protocol, runner, seeds, generated
result, decision gates, or first-passage estimand. The post-run verifier must
therefore be treated as independent reproducibility evidence, not as evidence
that the original verifier implementation passed its own execution gate.
