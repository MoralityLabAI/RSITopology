# ASMP-9 v0.34 engineering-smoke abort

## Status

**Instrument abort. No choice receipt was accepted. No pilot row was
consumed.**

The registered v0.34 smoke started the owned Qwen3.5-0.8B Q4_K_M server and
submitted the first forced-choice prompt. The server returned positive
probability for the model control token `<think>`. The registered answer
alphabet was exactly `{A,B}`, so the fail-closed extractor raised:

```text
ValueError: grammar admitted an unexpected token: '<think>'
```

The run stopped with zero completed records. The extractor was not weakened
and the control token was not discarded or renormalized.

## Resource and cleanup receipt

```text
status                 failed / exit_code_1
elapsed                20.314 seconds
peak job RAM           1,279.941 MB
peak observed I/O      504.636 MB/s
peak GPU temperature   78 C
cleanup                passed
GPU memory after       0 MB
owned processes after  none
```

The peak I/O value was a short immutable-model-load burst; it did not persist
for the registered three samples and therefore did not trigger the sustained
I/O abort.

Local receipt hashes:

```text
a73577738d061b6bda0f97a8d07f551fbe6ad63526bfb28ff9f597b692eae516  wrapper/summary.json
55fdf718a54d1a038df11de9ec422a136d010bcd2abf7fe32ff7580bba609a7c  wrapper/cleanup_summary.json
833edd1626b894e39ee369da0743eddd500f6b0ba56c2f6415c052663fde09bb  wrapper/stderr.log
820c68b26f7999648409a8d8f1e67ddd1020296cab04878243d29160f79ab5bb  server_session_000_stderr.log
```

The local run directory is:

```text
D:\Research_Engine\runs\asmp9_physical_acquisition_smoke_v0_34_20260729
```

## Amendment

Version v0.34.1 uses the checkpoint's no-thinking chat-template prefix before
the unchanged user query. Its extractor remains exact and fail-closed: any
positive-mass token outside `{A,B}` still aborts. The v0.34 registration and
manifest remain immutable in Git history and on disk.

## Claim boundary

This abort demonstrates a prompt/runtime contract failure, not a scientific
result about preference identifiability or Qwen behavior. It cannot be used as
ASMP-9 evidence.

