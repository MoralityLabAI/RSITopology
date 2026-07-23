# ASMP-8 parallel audit engine

This is a deterministic, constant-memory Rust worker pool for the synthetic
sampling and empirical-Bernstein moment reduction used by the ASMP-8
audit-efficiency program.

It is deliberately separate from the sealed v0.5 implementation:

- it does not rewrite or replace any registered artifact;
- its counter-based random stream is invariant to worker count but is not
  NumPy's registered multinomial stream;
- it estimates the same two bounded moments at a fixed audit count;
- it does not run a language model; and
- it is a throughput and implementation instrument, not a scientific gate.

Build and test:

```powershell
cargo test --manifest-path tools/asmp8-audit-rs/Cargo.toml
cargo build --release --manifest-path tools/asmp8-audit-rs/Cargo.toml
```

Run the registered 8,192-audit scale over 1,024 independent streams:

```powershell
tools/asmp8-audit-rs/target/release/asmp8-audit.exe `
  --audits-per-stream 8192 `
  --streams 1024 `
  --workers 6 `
  --family diffuse_low_error
```

Run the Hoeffding-scale workload:

```powershell
tools/asmp8-audit-rs/target/release/asmp8-audit.exe `
  --audits-per-stream 524288 `
  --streams 1024 `
  --workers 6 `
  --family diffuse_low_error
```

The reported `total_audits` is `audits_per_stream × streams`. Memory is
`O(streams + workers)`, not `O(total_audits)`.

## Model-forward boundary

The Qwen throughput sample spends almost all its time inside the native model
kernel. Reimplementing its outer loop in Rust cannot improve that matrix
multiply. Model-bearing throughput should instead be improved with native
prompt batching, a GPU-enabled llama.cpp build, or a persistent inference
server. This Rust crate makes the statistical reduction negligible once model
scores have been produced.
