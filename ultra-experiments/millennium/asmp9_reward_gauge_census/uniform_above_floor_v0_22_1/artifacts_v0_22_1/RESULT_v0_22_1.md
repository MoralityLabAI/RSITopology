# ASMP-9 v0.22.1 result: fixed-uniform above-floor value complexity

## Verdict

```text
uniform_above_floor_value_complexity_classified_v0_22_1
```

All ten registered gates passed.  An independent verifier that imported
neither the implementation nor the runner passed all 17 checks.

## The classified object

Let `G=(V,E)` be a finite simple biconnected comparison block.  Set
`epsilon=1/2` and assign the same fixed integer number `r>=2` of independent
fair comparisons to every edge.  Write

```text
z = 2^(-r).
```

The three edge states then have exact weights

```text
P(ZERO)     = z,
P(FULL)     = z,
P(INTERIOR) = 1-2z.
```

For the directed-cut liveness event, an ASMP bidirected `INTERIOR` edge has the
same effect as an unoriented edge in Backman's strongly connected partial
orientations.  Backman's polynomial identity therefore gives

```text
F_G(r)
  = (1-z)^(|V|-1) z^(|E|-|V|+1)
    T_G((1-2z)/(1-z), 1/z).
```

Equivalently,

```text
x_r = (2^r-2)/(2^r-1),
y_r = 2^r,
(x_r-1)(y_r-1) = -1.
```

Every fixed `r>=2` lies on the nonexceptional Jaeger-Vertigan-Welsh
`H_-1` curve.  Exact evaluation of `T_G(x_r,y_r)` is therefore #P-hard.
The nonzero rational prefactor transfers that hardness to exact ASMP
availability.

The hardness remains when the oracle input is one finite simple biconnected
block.  Tutte evaluation factors over connected components and
vertex-biconnected blocks, while every bridge contributes the known factor
`x_r`.  A biconnected-block oracle would therefore evaluate a general simple
graph with polynomially many oracle calls.

Finally, under the common denominator `2^(r|E|)`, the availability numerator
counts the fair binary trial matrices whose residual graph is strongly
connected.  A matrix has polynomial description length and liveness is
checkable in polynomial time.  Thus the numerator is in #P and is #P-complete
under the same polynomial-time Turing reduction convention.

The minimal above-floor case is

```text
r=2, (x_2,y_2)=(2/3,4).
```

## Fresh exact cells

| graph | `r` | exact availability | microtrial numerator |
|---|---:|---:|---:|
| chorded cycle 7 | 2 | `300617/524288` | `601234` |
| chorded cycle 7 | 3 | `477281109/536870912` | `954562218` |
| chorded cycle 7 | 5 | `559451561882397/562949953421312` | `1118903123764794` |
| chorded cycle 8 | 2 | `1220317/2097152` | `2440634` |
| chorded cycle 8 | 3 | `3877481121/4294967296` | `7754962242` |
| chorded cycle 8 | 5 | `17932978933739961/18014398509481984` | `35865957867479922` |
| complete graph `K5` | 2 | `125867/131072` | `1006936` |
| complete graph `K5` | 3 | `133884143/134217728` | `1071073144` |
| complete graph `K5` | 5 | `140736143812943/140737488355328` | `1125889150503544` |

In all nine cells:

- direct three-state enumeration equaled the Backman/Tutte expression;
- the point lay exactly on `H_-1`;
- the common-denominator numerator was integral; and
- each graph had zero isomorphic matches in the sealed prior registry.

For `K5` at `r=2`, direct enumeration of all `2^20=1,048,576` binary trial
matrices gave

```text
125867/131072,
```

equal to both the status census and the Tutte route.  All-zero, all-one, and
alternating endpoint labels produced the same value, as required at
`epsilon=1/2`.

## Mechanical predecessor

The first registered version, v0.22, passed its nine scientific and resource
gates but failed G8 because its frozen evaluator searched case-sensitively for
a lowercase substring inside a capitalized forbidden sentence.  Its verdict
remains:

```text
uniform_above_floor_translation_not_established_v0_22
```

v0.22.1 did not edit or rerun that evaluator.  It hash-bound the complete
failed predecessor, replaced the proxy with equality of both complete
structured claim lists, and used three successor-fresh graphs.  The
predecessor binding passed.

## Registered gates

| gate | status |
|---|---|
| registration and predecessor binding | pass |
| freshness and graph structure | pass |
| exact state law and semantics | pass |
| weighted Tutte identity | pass |
| hard curve and fixed points | pass |
| direct minimal above-floor microtrial | pass |
| endpoint-label invariance | pass |
| exact numerator ledger | pass |
| structured complexity attribution | pass |
| resource and scope | pass |

Runtime was `35.8764254` seconds on CPU with `38,191,104` peak resident bytes.

## Hash chain

```text
source/protocol commit:
23507d1b16a43b4462b4a6aa6ebcef54c32bc497

registration commit:
cfe2e1433709a53f190e9b3fa1c9b9052f6fdd58

registration:
ce2038c8a0277acada81cc4206d5ec2f2b703c98a861dd3423f0677094743420

protocol:
844f32158142e256ebbb03c7fcc70db7bd584e0385da93f5e075141044a142dc

result:
a1039daf298ba89e20c7ca8eccfee9f3428a57712de40043184b1824f01afd5b

run receipt:
126439ae2a4e65403a29f0dd5782c0c61654606f12874e0d13eace6767d8b55f

independent verification:
d41a87073d2d2f26e7f8b87cda9ce5e12363cb5447425e9af9545f38374902f9
```

## Claim boundary

This is a prior-art-derived access-model translation and an exact
implementation verification.  It classifies value computation for a
**declared fixed uniform allocation**.

It does not prove uniform allocation optimal, classify maximin design or
nonuniform counts, handle arbitrary `epsilon`, give approximation complexity,
cover adaptive allocation, dependence, response misspecification, behavioral
reward identification, general inverse reinforcement learning, or resolve
ASMP-9.
