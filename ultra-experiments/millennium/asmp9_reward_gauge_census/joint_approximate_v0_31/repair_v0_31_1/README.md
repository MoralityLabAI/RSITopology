# ASMP-9 v0.31.1 resource-only runner repair

Version v0.31 emitted no result because its Windows memory query lacked the
native pointer declaration. This repair:

1. imports the registered v0.31 runner from its sealed path;
2. replaces only `peak_resident_bytes` with the already-working v0.30 native
   declaration; and
3. calls the original `main()` without copying any scientific logic.

The original v0.31 protocol, registration, fixtures, gates, theorem draft,
and implementation hashes remain binding. The repair cannot turn the failed
v0.31 attempt into a pass; it creates a separately registered execution path.
