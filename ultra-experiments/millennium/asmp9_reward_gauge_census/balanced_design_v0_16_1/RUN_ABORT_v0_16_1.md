# ASMP-9 v0.16.1 registered execution abort

The resource-safe amendment still failed its unchanged 120-second wall cap.

The persisted ledger proves that it completed:

1. registration binding;
2. 504 pairwise proof cells;
3. 16 global allocation cells; and
4. 12 compact-value cells.

Those stages took 67.506 seconds and 22,126,592 peak resident bytes. The
runner then entered the threshold stage. The outer command timed out at
154.029 seconds, after which the surviving worker was terminated.

No result or receipt was emitted. Therefore:

```text
G9_resource_and_scope = fail
joint scientific verdict = not_evaluated_resource_abort
```

The threshold implementation scanned every total budget from `k` to the
answer. At the smallest registered interior this created thousands of exact
rational evaluations. The exact monotonicity theorem permits an equivalent
and much cheaper successor:

1. exponential search for a passing upper bracket;
2. binary search for the first passing total; and
3. exact verification of the selected total and its predecessor.

Any v0.16.2 attempt must use a disjoint registry, preserve both earlier aborts,
retain the 120-second cap, and freeze the logarithmic threshold algorithm
before execution.
