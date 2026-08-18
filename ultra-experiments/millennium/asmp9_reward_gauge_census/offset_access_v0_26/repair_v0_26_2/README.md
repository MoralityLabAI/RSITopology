# ASMP-9 v0.26.2 runner repair

V0.26.2 imports the sealed v0.26.1 adjudication logic and changes only its
Windows peak-memory call. The successful v0.26 implementation already
declared the native handle argument types; v0.26.1 accidentally omitted them.

No scientific cell is rerun. V0.26 remains failed and v0.26.1 remains
unavailable.

The wrapper renames the imported runner's output files from the v0.26.1
internal names to v0.26.2 names after successful completion.
