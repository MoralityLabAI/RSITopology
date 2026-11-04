# ASMP-4 v0.11 completion audit

| Audit item | Evidence | Status |
|---|---|---|
| Prior vulnerability | Binary v0.6 action domain plus formal input derivative | Identified |
| Repaired authority | Bounded interval `[-1,2]` with safe controls in its interior | Exact |
| Local normal control | Uniform `|n|<=1/6`, `|eta|<=3/4` reachability formula | Proven |
| Cocycle category | Bi-infinite full-shift base and invertible normal fiber | Exact |
| Random NHIM | Point manifold, invariant splitting, isomorphism, and rate bounds | Definition-mapped |
| Adversarial quantifier | Every full-shift sequence | Universal |
| Timing | Current observe/read/write/control before next reset | No lookahead |
| Delayed counterfactual | No current read at `t=0` | Infeasible |
| Definition mutations | One-sided base, discrete authority, stale read, closed rate gap, and future sensing | 5/5 rejected |
| Capacity regions | Computed `(1,1)` and raw `(2,1)` corners | Preserved |
| Prior harness | Eleven packages and 145 tests | Inventoried |
| Integrated harness | Twelve packages including v0.11 | 155 tests passed |

The audit repairs the witness used by the stopping argument.  It does not turn
the conditional fixture into a full canonical ASMP-4 classification.
