# ASMP-9 evidence-ordering result v0.48

## Verdict

**`decision_dependent_ordering_not_established`**

The registered instrument was valid, but the prospective prediction failed.
On the disjoint confirmation experiment, every optimizer for the four-class
decision problem was also optimal for the root-group decision problem. The
two exact cross-regrets were zero.

This is a clean negative result. Burned development data had exhibited
disjoint optimizer sets and positive cross-regrets, so decision-dependent
evidence ordering is possible in the finite grammar. It did not transfer to
the prospectively registered allocation and parameter grid. Version v0.48
therefore establishes neither a universal common ordering nor a universal
incompatibility theorem.

## Mathematical instrument

For a finite experiment with outcomes `x`, parameter laws `P_theta`, risk
functional `d(theta)`, error level `alpha`, and an ordering `pi`, define the
prefix sets

```text
S_j(pi) = {x_pi(1), ..., x_pi(j)}
```

and the direct Buehler bound

```text
U_pi(x_pi(j))
  = max {d(theta) : P_theta(S_j(pi)) > alpha}.
```

For fixed `pi`, this is the smallest nondecreasing direct bound with the
registered uniform coverage property. Under a frozen reference distribution
`w` on outcomes, the expected certificate cost is

```text
C_d(pi) = sum_x w(x) U_pi(x).
```

The implementation optimizes `C_d` exactly by subset dynamic programming:

```text
DP_d(S)
  = min_{x in S} [DP_d(S \ {x}) + w(x) B_d(S)],

B_d(S)
  = max {d(theta) : P_theta(S) > alpha}.
```

It also counts all optimal orderings and audits intersections and cross-regret
without materializing the permutation universe.

This is a finite specialization of classical Buehler confidence theory and
finite decision ordering. It is not claimed as a new general theorem.

## Prospective confirmation

- Allocation: `(2,1,1)`.
- Symmetric-flip levels: `{0, 3/20, 7/20}`.
- Parameter laws: `27`.
- Outcomes: `12`.
- Implicit ordering universe: `12! = 479,001,600`.
- Error level: `alpha=1/10`.
- Reference law: uniform mixture over the registered parameter laws.
- Decision problems:
  - exact four-class policy-identification risk;
  - root-group decision risk.
- Symbolic horizon-two policy library: `3,748`.

The implementation was committed at
`145a74f5bf311167cb34eefc5da11a0502792373`, and the prospective registration
at `a6362f0514c6328d7f7b8ec2873f3a1843098cec`. The registration SHA-256 is

```text
35e94a38aeebdfe6a33352498a309bf17e6aaa5914519432faaacfb9eb1b065a
```

## Exact result

| Quantity | Four-class risk | Root-group risk |
|---|---:|---:|
| Minimum reference cost | `1636789/2880000` | `16331/48000` |
| Number of optimal orderings | `1,451,520` | `4,354,560` |
| Common optimal orderings | `1,451,520` | `1,451,520` |
| Cross-regret | `0` | `0` |
| Number of distinct bound values | `5` | `2` |

Thus the four-class optimizer set is a subset of the root-group optimizer set
on this fixture. The lexicographically selected representatives differ:

```text
four-class prefix:
  (2,0,1), (2,1,1), (0,1,1)

root-group prefix:
  (0,1,1), (2,0,1), (2,1,1)
```

Different representatives do not imply incompatible optima. The complete set
intersection and zero cross-regrets are the registered discriminators.

## Controls

### Full-statistic liveness

The Buehler tables were not constant. Four-class risk took five distinct bound
values and root-group risk took two. The confirmation therefore tested an
ordering problem rather than repeating only the all-zero atom.

### All-zero endpoint

The direct atom calculation and the singleton-prefix bound agreed exactly:

```text
four-class: 231/400
root-group:   7/20.
```

This recovers the v0.47 mandatory-atom result as the minimum-statistic
endpoint of the full table.

### Exact coverage

The minimum exact coverage under both decision bounds was

```text
144579/160000 = 0.90361875 > 0.9.
```

Every experiment row and the reference law summed exactly to one.

### Burned development witness

The disclosed `(1,1,1)` development fixture over levels
`{0,1/5,2/5}` had:

```text
common optimizer count: 0
four-class cross-regret: 4/3125
root-group cross-regret: 2/625.
```

This proves finite existence of decision-dependent optimal orderings inside
the implementation grammar, but it is not confirmation evidence. The disjoint
prospective fixture refuted transfer of that pattern.

## Verification and repair record

The scientific result and the original verifier were committed immutably at
`83bae5e5e850a5c586d028745f09ad48a70fc0a5`.

The original verifier reproduced the scientific payload, experiment rows,
subset bounds, registration, and every source hash, but returned `ok=false`
because it incorrectly required the scientific prediction gate `X0` to pass.
That conflated a valid registered null with an invalid replay.

An explicitly post-outcome verifier-only repair was committed at
`48b145c6501b7c9f6c1e5f04f2e5ca930dd7e71e` and separately registered at
`466d21961ab072aa8cfb7006bc751f62f6d8bdb0`. Its registration hash is

```text
c50140c8a01df31df616a0a011f679012319c920d60dbbee6c247f4c977902b3
```

The repair changes no scientific value or prediction. It accepts an exact
replay when every instrument gate passes and the recorded status matches the
frozen prediction outcome. The repaired verifier passed:

- registered sources: exact match;
- repair sources and intent: exact match;
- scientific payload: exact match;
- experiment rows: exact match;
- subset bounds: exact match;
- registration: exact match;
- original verifier failure: diagnosed;
- instrument status mapping: exact match.

Tests:

```text
scientific instrument: 13/13
verifier repair:        5/5
combined rerun:        18/18
```

Confirmation resources:

```text
wall time: 39.4692576 seconds
peak aggregate working set: 413,794,304 bytes
workers: 4
```

Canonical hashes:

```text
experiment rows:
d0024a9ff29962372c5bfc6ad3e29601a5fb880c6bd9d094cc192dbea134193f

subset bounds:
6067bf95b61c60f6a86ff317f711497b69dd46f9d42fad00502aa8f61151dea3

scientific result:
bfae0cd82bc6a59c862d963b7a76ac8b25b8d74e00217a377ff1051a9caaff3d

original verifier:
9675399fd37904b73dfee0053034d244f11505f80a6aa457fbe6dd1af68de2c6

repaired verifier:
e8554dd5786a5f795763a80982e5d5df91f061caf7e27513f81bbed492c2bc1d
```

## Resolution relevance

Version v0.48 advances the v0.47 full-statistic obligation:

- it constructs the exact Buehler table at every outcome for any frozen
  ordering;
- it optimizes reference cost over all `12!` orderings by exact dynamic
  programming;
- it counts and intersects complete optimizer sets; and
- it supplies both an internal incompatibility witness and a disjoint
  common-optimum confirmation.

The null changes the next theorem target. Another grid search for a favorable
incompatibility witness would not resolve ASMP-9. The load-bearing question is
now:

> Which structural conditions on two finite decision risks and their
> Buehler set functions guarantee a shared optimal outcome ordering, and
> which conditions force positive cross-regret?

This is a finite common-chain problem over the subset lattice. A useful
successor must provide sufficient or necessary-and-sufficient conditions,
not merely another example.

## Claim boundary

The ordering formula is classical confidence theory, and the dynamic program
is a finite exact optimizer. The result concerns one finite shared-BSC
calibration experiment, one reference law, deterministic nondecreasing direct
bounds, and two decision risks. It establishes neither a universal
decision-dependent ordering theorem nor a universal common-order theorem,
does not validate a physical preference channel, and does not resolve
ASMP-9.
