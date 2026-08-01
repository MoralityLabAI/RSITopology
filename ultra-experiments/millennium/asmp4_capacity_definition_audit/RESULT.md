# ASMP-4 capacity-definition audit result

## Successor

The stop condition in this audit has been acted on. The
[metric-robust v0.3 theorem](../asmp4_metric_robust_collapse_v0_3/RESULT.md)
is the current successor. It strengthens the
[v0.2 serial theorem](../asmp4_serial_collapse_theorem_v0_2/RESULT.md) with
bilateral normal forms and distinguishes whole-language growth from causal
prefix branching. Together they replace the incompatible nominal-grid
interpretation with a complete diagonal-quadrant region, exact finite-horizon
formulas, and assumption-boundary counterexamples. This file is retained as
the diagnostic that motivated that repair.

## Decision

**STOP AND REPAIR THE PROBLEM DEFINITION BEFORE CLAIMING RESOLUTION.**

The existing ASMP-4 v0.1 run is internally reproducible and exact for its
frozen rational, time-indexed memoryless grammar. It is not, however, a finite
instance of the canonical achieved-transcript capacity region `R_K`. The audit
harness exposes definition-level mismatches that prevent a sound extrapolation
from the 108-cell phase map to the stated two-port conjecture.

## Exact audit results

The audit replays the committed `result_v0_1.json` and exhausts open-loop action
sequences over the union of all registered action values.

| Check | Result |
| --- | ---: |
| Source finite witnesses | 77 |
| Source witnesses with `|M_w(T)| > |M_r(T)|` | 0 |
| Source witnesses with strict write collapse `|M_w(T)| < |M_r(T)|` | 34 |
| Raw upward-closure violations | 6 |
| Non-nested write-dictionary pairs | 3 of 3 |
| Raw disagreements between the two zero-port cuts | 3 of 12 plant/horizon contexts |
| `r=0,w=max` mismatches against exhaustive open-loop control | 3 |
| `r=max,w=0` mismatches against exhaustive open-loop control | 0 |
| Feasible rows whose nominal read rate exceeds achieved transcript growth | 60 of 77 |
| Feasible rows whose nominal write rate exceeds achieved transcript growth | 53 of 77 |

The load-bearing cell labelled `(r,w)=(2,2)` at `T=2,c=1/2,a_z=3/2`
realizes only three read transcripts and three write transcripts. Under the
canonical formula its achieved rates are

```text
r_r = r_w = log2(3)/2 = 0.792481250360578 bits/step,
```

not two bits per step.

## Data-processing obstruction

For any deterministic registered code in the canonical architecture, fix a
horizon `T`. The controller receives only the realized read transcript. Its
initial state is plant-independent, and its causal update and output maps are
fixed. Therefore there is a function

```text
Phi_T : M_r^C(T) -> M_w^C(T)
```

whose image is the realized write-transcript set. Consequently,

```text
|M_w^C(T)| <= |M_r^C(T)|
r_w(C) <= r_r(C).
```

Independent shared randomness does not remove this obstruction for universal
worst-case safety: a safe realization can be fixed, producing a deterministic
code without increasing either transcript set. If safety is only probabilistic
over the seed, it is a different specification.

This lemma rules out a write achieved-information threshold above the read
threshold in the architecture as currently stated. A larger *nominal actuator
alphabet* may still be present, but unused write symbols are not achieved
information and do not alter the controller's image.

If `M_r^C(T)` and `M_w^C(T)` are instead meant to include declared but
unrealized container words, the rates become representation-dependent: padding
an otherwise identical code with unused symbols changes its alleged achieved
rate. A capacity theorem therefore needs either realized transcript images or
an explicit minimization over equivalent codebooks.

## Why the current finite phase map is not `R_K`

First, `R_K` is an upper set: a code admitted at `(R_r,R_w)` remains admitted
at all componentwise larger budgets. The raw v0.1 grid violates this six times.
For example, some cells pass with the zero-bit action dictionary `{0}` and
fail after the nominal write budget increases because `{0}` is removed.

Second, every pair of registered write dictionaries is non-nested:

```text
0 bits: {0}
1 bit:  {-1/2,+1/2}
2 bits: {-3/4,-1/4,+1/4,+3/4}.
```

Changing `w` therefore changes both symbol capacity and available control
values. This is an actuator-authority intervention, not a pure information-rate
intervention.

Third, a zero-bit-per-step row in this fixed-alphabet finite harness has a
singleton transcript set. With no state-correlated side information, either
singleton cut reduces to an open-loop action sequence. The two cuts must have
the same feasibility when the actuator class is held fixed. (A zero
*asymptotic* rate can still permit subexponentially many transcripts and is not
being identified with a singleton here.) The raw grid disagrees in three
contexts solely because its dictionaries differ. Exhaustion over the seven
registered action values confirms the common open-loop answer in all 12
contexts.

Fourth, the canonical statement explicitly permits actuator-decoder memory.
A two-step scalar fixture

```text
x_(t+1)=x_t+u_t,  x_0=0,  K={0,1},  U={-1,+1}
```

is safe under the one-symbol scheduled sequence `(+1,-1)`, while every fixed
memoryless one-symbol decoder fails. Both transcript sets are singletons, so
both achieved rates are zero. A static action dictionary cannot represent this
allowed zero-rate code.

## Prior-art boundary

The missing repair is not another static finite grid. Invariance feedback
entropy already supplies a history-dependent operational data-rate theorem for
uncertain coder-controllers and distinguishes it from static memoryless rates:

- Tomar, Rungger, and Zamani,
  [Invariance Feedback Entropy of Uncertain Control Systems](https://arxiv.org/abs/1706.05242).
- Zhong, Huang, and Zou,
  [Invariance entropy for uncertain control systems](https://arxiv.org/abs/2205.05510).
- Colonius and Kawan,
  [Invariance Entropy for Control Systems](https://doi.org/10.1137/080713902).

ASMP-4 must first specify what genuinely new second operational resource remains
after the controller-to-actuator transcript is recognized as a causal image of
the sensor-to-controller transcript.

## Minimum repair required

A versioned ASMP-4 replacement should:

1. choose either achieved transcript growth or nominal link alphabet capacity
   and use that choice consistently;
2. keep the admissible control set and actuator authority fixed across budgets;
3. include the declared decoder memory and all plant-independent open-loop
   sequences;
4. enforce upward-closed budget semantics;
5. incorporate the unavoidable wedge `0 <= r_w <= r_r` for deterministic
   achieved transcripts, or add and charge a genuinely independent controller
   information source; and
6. register a precise plant/evaluator/uncertainty class before requesting a
   coordinate-invariant variational theorem.

Until those choices are fixed, the requested "entire achievable rate region"
does not denote one stable mathematical target. Stopping here is therefore
stronger than merely saying the full problem is difficult: the current
statement and harness use incompatible rate objects.
