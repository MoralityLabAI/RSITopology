# ASMP-9 v0.18 post-run receipt note

The `started_at_utc` field in `artifacts_v0_18/result_v0_18.json` is
misnamed. The sealed runner calls `utc_now()` while assembling the result,
after the scientific computation has completed. It is therefore an artifact
emission timestamp, not the wall-clock start time.

The reported `elapsed_seconds` value is measured correctly with a monotonic
`perf_counter` from before protocol and registration loading through gate
evaluation. No scientific gate, registration-order claim, hash, or resource
decision depends on the misnamed UTC field.

The field is preserved unchanged. Any successor runner should record separate
`started_at_utc` and `completed_at_utc` values.
