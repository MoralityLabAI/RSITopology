# Support-zero-error sensor-kernel theorem v0.17

## Registered kernel

Use the v0.13 positive-volume collar with two control-relevant mode classes, `q=(0,0,8,8)`. Let `Y` be a finite registered sensor-output alphabet. For each mode `z`, fix a nonempty support `S_z subseteq Y` and arbitrary rational probabilities that are strictly positive on `S_z`, zero elsewhere, and sum to one.

At each step the sensor observes the current normal coordinate and produces a registered output `y in S_z`. The charged read transcript retains `y` injectively plus the required normal-cell information. Safety must hold for every disturbance word and every output word in support. For a finite positive-support kernel this also implies per-disturbance almost-sure safety: any unsafe supported finite prefix has positive probability.

Let `a=|union_z S_z|` be the number of active output symbols.

## Theorem

The kernel is feasible if and only if cross-`q` supports are disjoint:

In plain terms: cross-q supports are disjoint exactly in the feasible case.

`union(S_z:q(z)=0) intersection union(S_z:q(z)=8) = empty`.

For every feasible kernel, the exact full-collar region is

`[1+log2(a),infinity) x [2,infinity)`.

For initial normal radius `0<rho<=1`, exact horizon-`T` counts are

- read words: `a^T ceil(rho*2^T)`;
- write words: `2^T ceil(rho*2^T)`.

An infeasible kernel has empty safety-capacity region.

## Sufficiency

When cross-`q` supports are disjoint, every active output has a unique `q` class. The controller therefore decodes `q` from every possible registered output, regardless of its probability. It combines that value with the v0.13 normal controller.

For the full collar, `2^T` normal branch words and `a^T` possible raw output words give `(2a)^T` read words. The controller writes only the two `q` classes crossed with the two normal branches, giving `4^T` write words. All trajectories stay in the collar.

For an inner radius, partition `[-rho,rho]` into `ceil(rho*2^T)` intervals of length at most `2/2^T`, center the selected interval with the first residual control, and use zero residual later. This gives the stated finite counts.

## Necessity

If a registered output `y` lies in both a `q=0` support and a `q=8` support, choose the two corresponding initial states with normal coordinate zero. Both can emit the same observed `y` with positive probability, so the causal controller must issue one common first control. Safety for the low mode requires `u in [-1,1]`; safety for the high mode requires `u in [7,9]`. The intervals are disjoint. Thus support overlap is impossible under support-zero-error or per-disturbance almost-sure safety.

For a feasible kernel, arbitrary disturbance selection and positive support make every active output word possible. The raw-output charging rule therefore requires at least `a^T` output transcripts. Normal expansion requires `ceil(rho*2^T)` cells. Their product is the read converse. The same normal converse combined with all `2^T` `q` words gives the write converse.

## Complete support census

For a declared alphabet of size `s`, each of four modes has one of `2^s-1` nonempty supports, giving `(2^s-1)^4` relations. Exhaustion for `s=1,2,3,4` covers 53,108 relations:

- 724 feasible;
- 52,384 infeasible;
- feasible active-support histogram `20,210,494` for `a=2,3,4`;
- 620 genuinely randomized feasible relations.

An independent combinatorial proof reproduces the census. If a low class uses exactly `l` output symbols, its two ordered nonempty mode supports cover those symbols in `3^l-2` ways. Choosing disjoint low, high, and unused output sets and summing this product gives the same feasible counts.

## Deterministic embedding

Among the feasible relations are 104 labeled deterministic kernels. Quotienting output labels leaves exactly the four partitions from v0.16, with block histogram `1,2,1`. Thus the partition theorem is recovered exactly. Sensor randomization changes which support refinements exist, but it does not change the support-zero-error rate formula.

## Scope

This result is exact for finite memoryless kernels, raw-output charging, and universal support safety. It does not address block error, expected-length compression, channel memory, hidden sensor state, continuous outputs, or asymptotically vanishing failure probability.
