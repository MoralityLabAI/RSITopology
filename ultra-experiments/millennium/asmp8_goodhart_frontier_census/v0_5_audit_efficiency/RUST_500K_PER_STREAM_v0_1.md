# ASMP-8 500,000-audits-per-stream execution

The deterministic Rust reduction completed **500,000 audits per stream** over
1,024 independent counter-based streams: **512,000,000 total audit draws**.

- Engine elapsed time: 0.3033644 seconds.
- Throughput: 1,687,739,233.74 audit draws/second.
- Peak working set: 4,124,672 bytes.
- Mean empirical-Bernstein U1: 0.02982115449560215.
- Mean empirical-Bernstein U2: 0.03562911293371235.
- Deterministic checksum: `a80e639ab9bc88e5`.
- External summary SHA-256:
  `455240fa2fdda6ba180ba732e0a6800e957df6d28bb0dd1cd2643240176baea7`.

Canonical external run:
`D:\Research_Engine\runs\asmp8_rust_500k_per_stream_v0_1`.

This is counter-based synthetic sampling and moment reduction. It contains no
model forward pass and does not replace the sealed NumPy v0.5 scientific
artifacts. The separately staged Qwen 500,000-audit run is a model-forward
stress and measurement study with its own claim boundary.
