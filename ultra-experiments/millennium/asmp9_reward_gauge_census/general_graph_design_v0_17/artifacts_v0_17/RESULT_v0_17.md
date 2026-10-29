# ASMP-9 general comparison-graph allocation v0.17 result

## Verdict

`registered_exact_result_passed`

## Gates

- `G0_registration_binding`: **PASS**
- `G1_registry_completeness`: **PASS**
- `G2_residual_rank_identity`: **PASS**
- `G3_representative_invariance`: **PASS**
- `G4_three_state_exactness`: **PASS**
- `G5_endpoint_reduction`: **PASS**
- `G6_bad_support_completeness`: **PASS**
- `G7_primal_dual_exponent_certificates`: **PASS**
- `G8_finite_nonuniform_counterexample`: **PASS**
- `G9_resource_and_scope`: **PASS**

## Residual-cycle theorem checks

- fresh capacity cells: 6
- realized count representatives: 3852
- conditional fibers: 1900
- residual-rank mismatches: 0
- representative-invariance failures: 0

## Exact ternary compression

| graph | raw binomial enumeration | ternary status polynomial | exact |
| --- | ---: | ---: | :---: |
| wheel5 | 2395953994/3486784401 | 2395953994/3486784401 | yes |
| theta133 | 1529775/11529602 | 1529775/11529602 | yes |
| cycle4_tail | 13923/62500 | 13923/62500 | yes |

## Bad-support exponent certificates

| graph | `tau_G*` | primal feasible | dual feasible |
| --- | ---: | :---: | :---: |
| cycle4_tail | 1/2 | yes | yes |
| cycle6 | 1/3 | yes | yes |
| theta133 | 1/3 | yes | yes |

## Prospective finite counterexample

- graph: theta `(1,3,3)`
- total trials: 14
- positive labelled allocations: 1716
- uniform value: `3557696000/13841287201`
- exact optimum: `25309152000/96889010407`
- optimizer count: 6
- balanced optimizer count: 0
- complete allocation/value digest: `a3c94450494846776f047780a5711a0b2d07f3acbe8a98f3e4d92ef5389f3fa3`

## Interpretation

The result tests whether the one-cycle balancing theorem transfers to graphs
with several cycle directions. The large-deviation allocation is certified
by a finite hypergraph game over minimal bad boundary supports; the finite
theta census is a separately registered stress test. A pass or failure is
about this exact independent Bernoulli comparison model only.

## Resources

- elapsed seconds: 81.550422
- peak resident bytes: 23855104
- GPU used: false

## Claim boundary

Fresh exact verification of residual-cycle fiber rank, ternary status compression, coordinatewise endpoint reduction, minimal-bad-support exponent certificates, and one finite nonuniform-allocation counterexample for independent Bernoulli comparison graphs; not an every-budget optimum theorem, adaptive allocation, dependent or unknown-link behavior, downstream test-power theorem, general IRL identification, or ASMP-9 resolution.
