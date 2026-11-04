# ASMP-3 machine grammar completion audit v0.3

```text
sealed upstream/grammar inputs = 9
canonical codec fields = 12/12
WV-IR opcodes = 25/25
component signatures = 23/23
registered builtins = 25/25
FIX/ADM compiler rows = 14/14
noncanonical byte fixtures rejected = 5/5
reference runtime checks = 5/5
producer gates = 11/11
clean-room checks = 11/11
focused tests = 26 passed
cross-package ASMP-3 tests = 512 passed across 43 test files
standalone ASMP-3 checkers = 39/39 successful
external reproductions = 0/2
```

The parser proves syntax, canonical bytes, type/reference closure, and mode
placement. It deliberately does not claim to decide semantic totality or
membership.

The standalone total includes the expert-review checker. Its successful result
remains `0/2 qualifying; complete=false`, verifying that the external gate is
open rather than counting missing review as completion.
