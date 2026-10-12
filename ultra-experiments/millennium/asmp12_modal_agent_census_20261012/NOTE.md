# ASMP-12 modal-agent census: exact resource-indexed program equilibria for provability-conditioned agents

Status: census note, 2026-10-12. Exact for the enumerated family; nothing here
is a theorem about unrestricted programs, bounded proof search, mixed
strategies, or real agents. Companion to the critique
(`docs/CRITIQUE_NOTES_20261012.md`, §4 ASMP-12) and to the existing ASMP-12
packages, which enumerate *source-reading lookup-table* programs
(`v0_2_survival`, `v0_3_constructible_survival`, `v0_4_inertial_selector`).
This note instantiates the other model the v0.2 scope draft names: the modal
agents of Barasz, Christiano, Fallenstein, Herreshoff, LaVictoire, and
Yudkowsky (*Robust cooperation in the prisoner's dilemma: program equilibrium
via provability logic*, 2014), with resource measured by formula complexity.
The draft's suggestion to measure resource by *proof length* is not pursued:
minimal proof lengths in Peano arithmetic are not computable in practice,
whereas the modal fixed points are exactly decidable.

Code: `modal_census.py` (stdlib only). Data: `census_pqDb.json`.
Reproduce with

```powershell
python ultra-experiments/millennium/asmp12_modal_agent_census_20261012/modal_census.py --inputs p,qD,b --out census_pqDb.json
```

(about eight minutes on one core; the self-test in §3 runs first and aborts on
any mismatch).

## 1. Question

ASMP-12 (v0.2 draft) asks for the achievable payoff set `P_B(G)` of
resource-bounded program equilibria, its behaviour as `B` grows, and sharp
resource thresholds for robust cooperation. The existing packages measure
resource by the size of a lookup-table catalog and find cooperative
equilibria that die when the catalog grows (174 of 512 catalogs when the
temptation exceeds the reward). This census asks the same questions for
agents that condition on *provable* facts about the opponent rather than on
source labels, where resource is the number and complexity of provability
tests.

## 2. The family

Agents are Boolean functions of at most two **provability atoms**
`Box(psi)`, where `psi` is a Boolean function of at most two of the inputs

| input | meaning |
|---|---|
| `p` | the opponent cooperates with me |
| `qD` | the opponent cooperates with DefectBot |
| `b` | `Box(False)`: "PA proves a contradiction"; true exactly at world 0 below, and the device that encodes PA+1 provability, since `PA + Con(PA) proves x` iff `PA proves (b or x)` |

Inputs occur only under a `Box`, so every agent is modalized and the mutual
fixed points of a match are unique (de Jongh–Sambin). Rank is at most 1 in
the Barasz et al. sense: agents may consult the opponent's behaviour against
one fixed test agent (DefectBot). The input `qC` (behaviour against
CooperateBot) is implemented but not used in the reported run; with it the
family has about 23,000 formulas and the full outcome matrix was not computed.

Two resource measures are reported:

- **(atoms, inputs)**: the pair (number of atoms, maximum inputs per atom),
  ordered lexicographically: `(0,0) < (1,0) < (1,1) < (1,2) < (2,1) < (2,2)`;
- **size**: atoms plus total inputs over atoms, from 0 to 6. Constants have
  size 0, `Box(False)` size 1, FairBot `Box(p)` size 2, PrudentBot
  `Box(p) & Box(b | ~qD)` size 5.

Each agent's level is the minimum over all formulas with the same semantic
signature (§3). Families are cumulative: level `L` contains every agent of
level at most `L`.

| level (atoms, inputs) | new agents | cumulative |
|---|---:|---:|
| (0,0) | 2 | 2 |
| (1,0) | 2 | 4 |
| (1,1) | 10 | 14 |
| (1,2) | 52 | 66 |
| (2,1) | 82 | 148 |
| (2,2) | 2,072 | 2,220 |

| size | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| new agents | 2 | 2 | 10 | 62 | 108 | 620 | 1,416 |

From 6,736 syntactically distinct formulas, 2,220 semantically distinct
agents remain. (Correction, same day: the size of a deduplicated agent is the
*minimum* formula size over its equivalence class. The first version of
`modal_census.py` took the size of whichever equal formula was enumerated
first, which put 100 size-5 agents at size 6; `census_pqDb.json` still
carries that assignment. The canonical table above comes from the v2 engine's
regression run, `census_v2_regression_pqDb.json`, which reproduces every other
number of this note exactly. No equilibrium count, death count, or
conclusion changes; only the size-5 and size-6 row counts and the per-level
pair counts at size 5 do.)

## 3. Semantics and self-test

Matches are evaluated on the frame ω of the provability logic GL: worlds
`0, 1, 2, …`, where `Box(x)` holds at world `k` iff `x` holds at every world
`j < k`. For letterless sentences, provability in PA is truth at every finite
world and truth in the standard model is truth at the limit world, whose
`Box` is the conjunction over all finite worlds (Solovay, *Provability
interpretations of modal logic*, 1976; Boolos, *The Logic of Provability*,
1993, ch. 7, on the closed fragment). The fixed-point sentences of a match
are letterless, so an agent's actual action is the eventual value of its
fixed point along the worlds, and "the opponent provably cooperates" is
"cooperates at every finite world".

Implementation: each atom keeps a running conjunction over past worlds; the
match state (two conjunction vectors) is monotone and the opponents'
precomputed behaviour against DefectBot stabilises, so the iteration is
provably at a fixed point once nothing changes after the stabilisation index,
and the limit values are read off. Semantic signatures for deduplication
evaluate the formula on every abstract history (the valuation at world 0, and
the set of valuations seen at later worlds), which is exactly the information
a match can ever present to a depth-2 formula.

Self-test (asserted before the census runs), reproducing Barasz et al.:

| match | outcome |
|---|---|
| FairBot vs FairBot | C, C (and provably so: true at every finite world) |
| FairBot vs DefectBot | D, D (FairBot's cooperation is true at world 0 only, hence not refutable in PA) |
| FairBot vs CooperateBot | C, C |
| PrudentBot vs CooperateBot | D, C |
| PrudentBot vs DefectBot | D, D |
| PrudentBot vs FairBot | C, C |
| PrudentBot vs PrudentBot | C, C |

## 4. Results

Program equilibrium: a pair `(A, B)` in family `F` such that no `A'` in `F`
obtains a strictly higher payoff against `B` than `A` does, and symmetrically.
Pure outcomes only. Payoffs: for each of the 24 strict orderings of
`(T, R, P, S)` the top-ranked symbol receives 4, the next 3, 2, 1.

### 4.1 The five named games, size stratification

| game | ordering | first size with a mutual-cooperation equilibrium | equilibrium payoff set at size 6 | deaths at any transition |
|---|---|---:|---|---:|
| Prisoner's Dilemma | T>R>P>S | 2 (FairBot) | {(2,2), (3,3)} | 0 |
| Chicken | T>R>S>P | 2 (FairBot) | {(2,4), (3,3), (4,2)} | 0 |
| Stag Hunt | R>T>P>S | 0 (CooperateBot) | {(2,2), (4,4)} | 0 |
| Deadlock | T>P>R>S | never | {(3,3)} = mutual defection | 0 |
| Harmony | R>T>S>P | 0 | {(2,3), (3,2), (4,4)} | 0 |

Counts at size 6 (2,220 agents): Prisoner's Dilemma 54,478 equilibrium pairs
of which 1,578 are mutual cooperation; Chicken 512,364 / 1,578; Stag Hunt
1,257,803 / 1,204,903; Deadlock 116,758 / 0; Harmony 1,232,043 / 1,204,903.
The full per-level tables are in the JSON under `games.by_size`.

### 4.2 All 24 orderings

- **Top-level equilibrium payoffs equal the pure individually-rational set
  in every ordering (24/24).** Every pure payoff pair in which each player
  receives at least the pure minmax value is realised by some program
  equilibrium of the 2,220-agent family. This is a finite pure analogue of
  Tennenholtz's program-equilibrium folk theorem (which uses source-code
  equality tests) obtained with provability tests alone, at two atoms.
- **Deaths depend on the resource order.** Under the size stratification
  there are no deaths in any ordering at any transition. Under the
  lexicographic (atoms, inputs) order there are 200 deaths in 7 orderings,
  all at the transition `(1,2) -> (2,1)`:

| ordering | deaths | example dying pair |
|---|---:|---|
| P>R>T>S, P>R>S>T | 13 each | (CooperateBot, `~Box(qD xor b)`) |
| P>S>T>R | 12 | (`~Box(False)`, `~Box(qD xor b)`) |
| S>R>P>T, S>R>T>P | 35 each | (CooperateBot, `~Box(~(qD xor b))`) |
| S>T>P>R, S>T>R>P | 46 each | (DefectBot, `~Box(~(qD xor b))`) |

  Mechanism (worked for P>R>T>S, payoffs P=4, R=3, T=2, S=1): the pair
  (CooperateBot, `X = ~Box(qD xor b)`) plays C,C for (3,3) and is an
  equilibrium among agents with one atom, because the only way to beat 3
  against `X` is mutual defection, which requires an agent that `X`
  defects against while itself defecting. `X` defects against `Y` exactly
  when `Y` cooperates with DefectBot at every world except world 0, i.e.
  cooperates with DefectBot *non-provably*. The agent
  `Y = ~Box(False) & Box(~qD)` does this and defects against `X` (its second
  atom fails because `X` cooperates with DefectBot from world 2 on), so `Y`
  obtains (4,4)-type mutual defection worth 4 > 3 and the pair dies. `Y`
  has two atoms with 0 and 1 inputs: level `(2,1)`, but size 3, the same size
  as `X`. Under the size order `Y` enters together with `X`, the pair is
  never an equilibrium, and no death is recorded. The deaths are therefore
  not a property of "more resource" but of which agents a particular
  ordering admits first. This bears directly on ASMP-12's third obligation
  (invariance under reasonable encodings): even for a 2,220-agent family,
  the birth/death record is not invariant to the resource measure, so a
  v0.2 statement must either fix the measure or ask for measure-invariant
  quantities (for instance the lattice of families rather than a chain).
- None of the seven orderings with deaths is a conflict game of the usual
  kind; all rank the sucker payoff `S` or the punishment `P` first. In the
  Prisoner's Dilemma, Chicken, Stag Hunt, Deadlock and Harmony there are no
  deaths under either order.

### 4.3 Robust cooperation and the Löb threshold

FairBot `Box(p)` is the unique new agent at size 2 that makes mutual
cooperation an equilibrium outcome in the Prisoner's Dilemma and Chicken,
and it survives every expansion: it is unexploitable (no agent in the family
obtains D-against-C versus it), because provable cooperation is sound. In
the 2,220-agent family, 344 agents are unexploitable and 40 of those also
cooperate with themselves. All 40 are FairBot with world-0 or
provably-false guards or with a second atom that cannot fire against a
cooperator, for example

- `Box(p)` (FairBot),
- `Box(p | b)`, i.e. "PA + Con(PA) proves you cooperate" (FairBot at PA+1),
- `~Box(False) & Box(p xor b)`,
- `Box(p) & Box(~qD | b)` family members (PrudentBot-like guards on the
  opponent's behaviour against DefectBot).

So in this family the resource threshold for robust cooperation is one
provability atom over one input, it is attained by Löb's theorem exactly as
in Barasz et al., and no amount of additional resource (within the family)
creates a deviation against it.

### 4.4 A non-Nash program equilibrium in Harmony

In Harmony (R>T>S>P; cooperation dominant) the pair
(`Box(~p)`, DefectBot) is a program equilibrium with outcome (C, D) and
payoffs (2, 3). `Box(~p)` cooperates exactly with opponents that provably
defect against it; against it, any cooperator is met with defection and
receives at most 2, so DefectBot's 3 is a best response, and against
DefectBot every agent receives at most 2, which `Box(~p)` attains. The
dominant-strategy outcome (C, C) remains available, but the family also
sustains an equilibrium in which one player defects in a game where
defection is dominated. This is the folk-theorem flavour of program
equilibrium made concrete with a two-symbol formula.

## 5. What this says about ASMP-12

1. For provability-conditioned agents the pure achievable set saturates the
   pure individually-rational set already at two atoms, in every strict
   symmetric 2×2 game. The interesting ASMP-12 content is therefore not the
   limit set but the *order* in which outcomes appear and the invariance of
   that order.
2. Births and deaths are not invariant to the resource measure. ASMP-12 v0.2
   should state the measure (or demand measure-invariant statements), and
   the existing lookup-table result should be read with the same caveat.
3. In the 3-input family, growing it never destroys an equilibrium in the
   five canonical games under either measure; in the families of §7, which
   can consult the opponent's treatment of FairBot and PrudentBot, deaths
   occur in all five canonical games under both measures. So the monotone
   record is a small-family artifact, not a property of provability-
   conditioned agents. What does hold throughout is that no admitted agent
   ever exploits an unexploitable cooperator; deaths hit pairs whose other
   member relies on a gameable condition (a PA+1 test, a non-provability
   test), and many deaths are improvements, replacing defection or
   exploitation equilibria by mutual cooperation.
4. Robust cooperation has a one-atom threshold and FairBot's
   unexploitability is permanent, consistent with Barasz et al. and with
   Critch's bounded version; a modal census cannot say anything about
   proof-length thresholds, which remain the draft's stated but uncomputed
   target.

## 6. Claim boundary

Exact for: rank-≤1 modal agents over `(p, qD, b)` with at most two atoms of
at most two inputs, pure program equilibria, strict symmetric 2×2 orderings
with payoffs 4,3,2,1, the two stated resource measures. Not covered: mixed
equilibria, rank ≥ 2 agents (references to FairBot or others), PA+n for
n ≥ 2, more than two atoms, the `qC` input, bounded proof search, any
selection dynamic, and any claim about language models or deployed agents.
The semantic correspondence in §3 is cited, not reproved. The absence of
deaths under the size order is a census fact for this family, not a theorem
(and §7 shows it fails in a larger family).

## 7. Extension: references to FairBot and PrudentBot

Same day, second engine: `modal_census_v2.py`. Agents may now condition on
the opponent's behaviour against any of four fixed test agents, DefectBot,
CooperateBot, FairBot `Box(p)`, and PrudentBot `Box(p) & Box(b | ~qDB)`.
Since PrudentBot itself references DefectBot, agents referencing it have
rank 2 in the sense of Barasz et al. The engine evaluates the test agents'
own matches first (DefectBot and CooperateBot are constants, FairBot
references nothing, PrudentBot references DefectBot), then each agent against
each test, then the full outcome matrix; the equilibrium pass is vectorised
with numpy. Deduplication is exact (signature over the full behaviour-input
space) when the family has at most three behaviour inputs; otherwise agents
are deduplicated by signature over their own inputs and then merged whenever
two agents have identical rows and columns in the outcome matrix, which is
the only equivalence that matters for equilibria inside the family. Resource
levels are the minimum over each equivalence class. A regression run on the
§2 family reproduces every number in §4 exactly (2,220 agents; 54,478
Prisoner's Dilemma equilibrium pairs with 1,578 cooperative; 200 deaths in 7
orderings under the atoms order, none under size; 344 unexploitable agents,
40 self-cooperating).

### 7.1 Families

| family | inputs | atoms per agent | formulas | by signature | after behavioural merge |
|---|---|---|---:|---:|---:|
| broad | p, qDB, qCB, qFB, qPB, b | ≤ 2, at most one with two inputs | 20,608 | 12,268 | 4,953 |
| rank-2 core | p, qFB, qPB, b | ≤ 2, each ≤ 2 inputs | see 7.6 | | |

The broad family's outcome matrix took 64 minutes (75 million matches in
pure Python); the behavioural merge removed 7,315 agents that were
syntactically distinct but indistinguishable inside the family.

### 7.2 JustBot is FairBot

"JustBot", cooperate iff the opponent provably cooperates with FairBot, is
`Box(qFB)`. In this semantics it is behaviourally identical to FairBot: both
cooperate with `X` exactly when `X` provably cooperates with FairBot, and
every agent's behaviour against the two is the same because every input an
agent can consult (their actions, and their actions against the four tests)
coincides. The merge confirms it: `Box(qFB)` does not survive as a separate
agent in the broad family. FairBot's condition already *is* "you cooperate
with FairBot".

### 7.3 Equilibria in the five named games (broad family, 4,953 agents)

| game | equilibrium pairs at top | of which mutual cooperation | first size with a cooperative equilibrium |
|---|---:|---:|---:|
| Prisoner's Dilemma | 395 | 331 | 2 (FairBot) |
| Chicken | 40,591 | 331 | 2 |
| Stag Hunt | 6,182,866 | 6,182,802 | 0 |
| Deadlock | 7,950 | 0 | never |
| Harmony | 6,183,104 | 6,182,802 | 0 |

Two things changed against the 3-input family. The Prisoner's Dilemma
equilibrium count fell from 54,478 pairs to 395, because agents that can
consult the opponent's treatment of four tests find profitable deviations
against almost every non-cooperative partner; 331 of the 395 surviving pairs
are mutual cooperation, and the 64 others are mutual defection. And the
top-level equilibrium payoff set still equals the pure individually-rational
set in all 24 orderings.

### 7.4 Deaths now occur in canonical games, and under both orders

| order | total deaths | orderings with deaths | canonical games with deaths |
|---|---:|---:|---|
| (atoms, inputs) | 5,632 | 16 of 24 | Deadlock 75, Harmony 12, both at `(1,2) -> (2,1)` |
| size | 5,460 | 6 of 24 (the six orderings ranking `S` first) | none |

So the §4 finding "no deaths under size" was a property of the small family,
not of provability-conditioned agents in general; the measure-dependence
finding stands and is stronger (16 versus 6 orderings, different canonical
games affected). Two worked deaths:

- Harmony, atoms order: the pair `(Box(F), Box((qCB xor b) negated))` had
  payoffs (3, 3), one player exploiting; the newly admitted two-atom agent
  `(~Box(F) & ~Box(qDB)) | (Box(F) & Box(qDB))` reaches mutual cooperation
  (4, 4) with the second agent, so the exploiter's partner now has a better
  option and the exploitation equilibrium dies. A death can be an
  improvement.
- Deadlock, atoms order: `(DefectBot, Box(qCB xor b))` played mutual
  defection for (3, 3); the new agent `~Box(F) & Box(qDB)` makes the second
  agent cooperate while it defects, worth 4 in Deadlock. The victim
  conditions on behaviour against CooperateBot at world 0 versus later worlds,
  a non-provability test that two-atom agents can game.

Under the size order the same agents enter together with their killers, so no
canonical-game death is recorded; the `S`-first orderings lose equilibria
either way.

### 7.5 Robust cooperation

91 agents are unexploitable (nobody obtains D-against-C versus them) and 23
of those cooperate with themselves. Beyond the FairBot-with-guards family of
§4.3 the list now contains `Box(qPB)`, cooperate iff the opponent provably
cooperates with PrudentBot, and `Box(p & qCB)`, cooperate iff the opponent
provably cooperates both with me and with CooperateBot, plus several
`Box(p) & Box(...)` agents that add a test-behaviour guard to FairBot. All
are FairBot-like in the sense that cooperation is granted only on a provable
cooperation condition, which soundness makes unexploitable.

### 7.6 Rank-2 core family: deaths in every canonical game, under both orders

Inputs `p, qFB, qPB, b`, two atoms of up to two inputs each (the shape of
§2): 23,600 formulas, 11,108 by signature, **1,680** after the behavioural
merge (9,428 agents indistinguishable inside the family; `Box(qFB)` again
merges into FairBot). Levels: 2, 2, 11, 52, 88, 1,525 by (atoms, inputs);
sizes 2, 2, 11, 63, 122, 478, 1,002. Outcome matrix: 69 minutes.

| game | PE pairs at top | mutual cooperation | deaths, atoms order | deaths, size order |
|---|---:|---:|---:|---:|
| Prisoner's Dilemma | 391 | 310 | 35 | 27 |
| Chicken | 15,266 | 310 | 96 | 98 |
| Stag Hunt | 682,118 | 682,037 | 11 | 13 |
| Deadlock | 4,314 | 0 | 130 | 138 |
| Harmony | 682,269 | 682,037 | 10 | 8 |
| all 24 orderings | | | 1,952 in 20 | 2,552 in 20 |

Top-level equilibrium payoffs equal the pure individually-rational set in
24 of 24 orderings. 68 agents are unexploitable, 20 of them self-cooperating
(`Box(p)`, `Box(qPB)`, and FairBot-with-guards; the list is in the JSON).

Two kinds of death occur in the Prisoner's Dilemma:

- *improving*: `(DefectBot, X)` with `X = ~Box(qFB | ~qPB)` played mutual
  defection; the new agent `~Box(p) | Box(b)` reaches mutual cooperation
  with `X`, worth 3 against the 2 DefectBot obtained, so the defection
  equilibrium dies because `X`'s partner can now do better by cooperating;
- *exploitative*: `(FairBot, Y)` with `Y = Box(qFB | b)`, i.e. "cooperate
  iff PA+1 proves you cooperate with FairBot", played mutual cooperation;
  the new agent `~Box(F) & Box(p <-> b)` obtains D-against-C versus `Y` (4
  against FairBot's 3), so the pair dies. FairBot itself is still never
  exploited; what dies is a pair whose *other* member used a PA+1 condition
  that a two-atom agent can satisfy without actually cooperating.

So the §4 picture must be corrected in two places. First, deaths are not
confined to exotic orderings: with references to FairBot and PrudentBot they
occur in all five canonical games and under both resource measures, from the
first level where two-atom agents appear. Second, "FairBot's equilibria are
never destroyed" is true only of FairBot's own unexploitability; equilibria
in which FairBot's partner relies on a weaker provability condition can die.
What survives every expansion is the set of pairs of unexploitable mutual
cooperators, which by definition no admitted agent can improve on.

### 7.7 Claim boundary for §7

Exact for the two families as enumerated, pure program equilibria, strict
symmetric orderings with payoffs 4, 3, 2, 1, and the two resource measures.
The behavioural merge is exact for equilibrium questions inside each family
but makes "number of agents" family-relative. Deaths are classified only by
the printed examples, not by a full census of killer outcomes. Not covered:
rank 3 and above, more than two atoms, two two-input atoms in the six-input
family, mixed equilibria, selection dynamics, bounded proof search.
