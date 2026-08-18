# ASMP-9 balanced maximin design v0.16.1

This is the resource-safe successor to the registered v0.16 execution abort.

The mathematical theorem is unchanged. The registry is entirely disjoint,
the 120-second cap is not relaxed, and the runner writes start/progress/abort
telemetry before expensive stages.

The v0.16 abort remains canonical evidence and is not overwritten or
reclassified.
