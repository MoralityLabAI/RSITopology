# ASMP-9 ordinal reward-ray access frontier v0.2

**Verdict:** `finite_ordinal_reward_ray_access_frontier_established`

## Gates

- **G0_registration_binding:** PASS
- **G1_complete_enumeration:** PASS
- **G2_exact_anchor:** PASS
- **G3_robust_frontier_liveness:** PASS
- **G4_solver_validity:** PASS
- **G5_monotonicity:** PASS
- **G6_robust_access_penalty:** PASS
- **G7_witness_integrity:** PASS

## Query-width and query-count frontier

| dimension | reward bound | delta | first complete width | minimum queries | solver |
|---:|---:|---:|---:|---:|---|
| 1 | 1 | `0` | 1 | 1 | optimal |
| 1 | 1 | `1/2` | 1 | 1 | optimal |
| 2 | 1 | `0` | 1 | 2 | optimal |
| 2 | 1 | `1/2` | 2 | 4 | optimal |
| 3 | 1 | `0` | 1 | 3 | optimal |
| 3 | 1 | `1/2` | 2 | 9 | optimal |
| 2 | 2 | `0` | 1 | 4 | optimal |
| 2 | 2 | `1/2` | 3 | 8 | optimal |

## Interpretation

The `delta=0` arm is the exact-sign anchor: ternary coordinate comparisons
retain equality information. The `delta=1/2` arm treats a comparison whose
score lies inside a half-unit threshold band as adversarially ambiguous. The
registered width sweep therefore distinguishes a shortage of query count from
a query grammar that cannot robustly place two reward rays on opposite sides
of any admitted comparison hyperplane.

Every reward coordinate is a primitive cycle-return vector modulo positive
scale. Opposite vectors remain distinct. Every query is a primitive difference
between two nonnegative trajectory bundles.

## Claim boundary

This is a finite, nonadaptive, population-oracle comparison census after the
potential-shaping quotient has already been constructed. It is not a theorem
about arbitrary rewards, human preferences, policy observations, adaptive
query complexity, finite-sample learning, or discounted MDPs. The
misspecification arm is one frozen adversarial threshold model. Solver
optimality is backed by HiGHS status, zero reported MIP gap, matching dual
bound, and independent cover replay; it is not a formal proof certificate.
