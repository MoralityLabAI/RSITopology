# Local execution contract v0.82

- model: exact registered Qwen3.5-0.8B-Instruct files;
- dtype: float16;
- device: one local CUDA GPU;
- batch size: 1;
- checkpoint interval: every record;
- GPU memory allowance: 3900 MB;
- temperature abort: 88 C;
- process memory job-object limit: 6144 MB;
- minimum runtime free RAM: 2048 MB;
- timeout: 3600 seconds; and
- cleanup: stop only owned PIDs, release CUDA state, and verify no owned
  process survives.

System-wide page-file use is telemetry, not an owned-process hard gate.  This
contract never authorizes terminating unrelated processes.

