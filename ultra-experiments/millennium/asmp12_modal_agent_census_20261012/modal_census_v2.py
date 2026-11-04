"""ASMP-12 modal-agent census, version 2 (2026-10-12): references to test agents
and a vectorised equilibrium pass.

Agents are Boolean functions of at most `max_atoms` provability atoms Box(psi),
where psi is a Boolean function of at most `max_inputs` of the inputs

    p      the opponent cooperates with me
    qX     the opponent cooperates with test agent X   (X in the chosen test list)
    b      Box(False), true exactly at world 0 (encodes PA+1 provability)

Test agents available: DB (DefectBot), CB (CooperateBot), FB (FairBot = Box(p)),
PB (PrudentBot = Box(p) & Box(b | ~qDB)).  PrudentBot references DefectBot, so an
agent referencing PB has rank 2 in the sense of Barasz et al. (2014).

Semantics as in modal_census.py: fixed points evaluated on the GL frame omega;
provability = truth at every finite world; action = the eventual value.

Equilibria for all 24 strict symmetric 2x2 orderings under two resource
stratifications are computed with numpy on the full outcome matrix.

Options:
  --tests DB,CB,FB,PB   which q-inputs exist
  --max-atoms 2  --max-inputs 2
  --max-two-input-atoms N   cap on atoms with two inputs per agent (default: no cap)
  --out census.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from dataclasses import dataclass, field

import numpy as np

TEST_ORDER = ["DB", "CB", "FB", "PB"]


# ----------------------------------------------------------------------------
# Atoms and agents
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Atom:
    inputs: tuple[int, ...]   # indices into the input list (b is the last input)
    local: int                # truth table over the inputs in order (bit = f(x))

    def value(self, x_bits: int, pos_of: dict[int, int]) -> int:
        local = 0
        for pos, inp in enumerate(self.inputs):
            local |= ((x_bits >> inp) & 1) << pos
        return (self.local >> local) & 1

    @property
    def n_inputs(self) -> int:
        return len(self.inputs)


@dataclass
class Agent:
    atoms: tuple[int, ...]
    ftable: int
    level: tuple[int, int]
    name: str = ""
    seqs: dict[str, tuple[int, ...]] = field(default_factory=dict)   # behaviour vs each test agent
    stab: int = 0
    min_size: int = 0        # minimum formula size over the agent's equivalence class

    def eval_f(self, vals: list[int]) -> int:
        n = len(self.atoms)
        if n == 0:
            return self.ftable & 1
        if n == 1:
            return (self.ftable >> vals[0]) & 1
        return (self.ftable >> (vals[0] | (vals[1] << 1))) & 1


class Family:
    def __init__(self, tests: list[str]):
        self.tests = tests
        self.input_names = ["p"] + ["q" + t for t in tests] + ["b"]
        self.B = len(self.input_names) - 1          # index of b
        self.behav_inputs = list(range(self.B))      # p and the q's
        self.atoms: list[Atom] = []
        self.atom_index: dict[tuple[tuple[int, ...], int], int] = {}

    def add_atom(self, inputs: tuple[int, ...], local: int) -> int:
        key = (inputs, local)
        if key in self.atom_index:
            return self.atom_index[key]
        self.atoms.append(Atom(inputs, local))
        self.atom_index[key] = len(self.atoms) - 1
        return self.atom_index[key]

    def atom_name(self, i: int) -> str:
        at = self.atoms[i]
        n = len(at.inputs)
        if n == 0:
            return "Box(F)"
        rows = []
        for local in range(1 << n):
            if (at.local >> local) & 1:
                lits = [self.input_names[inp] if (local >> pos) & 1 else "~" + self.input_names[inp] for pos, inp in enumerate(at.inputs)]
                rows.append("&".join(lits))
        return "Box(" + ("|".join(rows) if rows else "F") + ")"

    def agent_name(self, ag: Agent) -> str:
        n = len(ag.atoms)
        if n == 0:
            return "CooperateBot" if ag.ftable & 1 else "DefectBot"
        names = [self.atom_name(i) for i in ag.atoms]
        if n == 1:
            return {0: "F", 3: "T", 2: names[0], 1: "~" + names[0]}[ag.ftable & 3]
        rows = []
        for local in range(4):
            if (ag.ftable >> local) & 1:
                rows.append("(" + (names[0] if local & 1 else "~" + names[0]) + " & " + (names[1] if local & 2 else "~" + names[1]) + ")")
        return " | ".join(rows) if rows else "F"


def canonical_local(inputs: tuple[int, ...], local: int) -> bool:
    """True iff the table depends on every listed input (so the enumeration is irredundant)."""
    n = len(inputs)
    for pos in range(n):
        dep = False
        for x in range(1 << n):
            if ((local >> x) & 1) != ((local >> (x ^ (1 << pos))) & 1):
                dep = True
                break
        if not dep:
            return False
    return True


def build_family(tests: list[str], max_inputs: int, max_atoms: int, max_two_input_atoms: int | None,
                 allowed_input_names: list[str] | None = None) -> tuple[Family, list[Agent]]:
    fam = Family(tests)
    if allowed_input_names:
        all_inputs = [fam.input_names.index(x) for x in allowed_input_names]
    else:
        all_inputs = list(range(len(fam.input_names)))
    # atoms: Box(F) (no inputs), then functions of 1..max_inputs inputs depending on all of them
    fam.add_atom((), 0)
    for n in range(1, max_inputs + 1):
        for inputs in itertools.combinations(all_inputs, n):
            for local in range(1 << (1 << n)):
                if local == 0 or local == (1 << (1 << n)) - 1:
                    continue
                if canonical_local(inputs, local):
                    fam.add_atom(inputs, local)
    atoms = fam.atoms
    formulas: list[Agent] = [Agent((), 0, (0, 0)), Agent((), 1, (0, 0))]
    for i, at in enumerate(atoms):
        for ft in (1, 2):
            formulas.append(Agent((i,), ft, (1, at.n_inputs)))
    if max_atoms >= 2:
        for i, j in itertools.combinations(range(len(atoms)), 2):
            n2 = (atoms[i].n_inputs >= 2) + (atoms[j].n_inputs >= 2)
            if max_two_input_atoms is not None and n2 > max_two_input_atoms:
                continue
            lvl = (2, max(atoms[i].n_inputs, atoms[j].n_inputs))
            for ft in range(16):
                dep0 = any(((ft >> (a0 | (a1 << 1))) & 1) != ((ft >> ((1 - a0) | (a1 << 1))) & 1) for a0 in range(2) for a1 in range(2))
                dep1 = any(((ft >> (a0 | (a1 << 1))) & 1) != ((ft >> (a0 | ((1 - a1) << 1))) & 1) for a0 in range(2) for a1 in range(2))
                if dep0 and dep1:
                    formulas.append(Agent((i, j), ft, lvl))
    return fam, formulas


# ----------------------------------------------------------------------------
# Semantic signature over the agent's own behaviour inputs
# ----------------------------------------------------------------------------


def used_behaviour_inputs(fam: Family, ag: Agent) -> tuple[int, ...]:
    s = set()
    for i in ag.atoms:
        for inp in fam.atoms[i].inputs:
            if inp != fam.B:
                s.add(inp)
    return tuple(sorted(s))


def signature(fam: Family, ag: Agent, full: bool = False) -> tuple[tuple[int, ...], int]:
    """Semantic signature over the agent's used behaviour inputs, or over all of the
    family's behaviour inputs when `full` (exact dedup; feasible for <= 3 inputs)."""
    U = tuple(fam.behav_inputs) if full else used_behaviour_inputs(fam, ag)
    m = len(U)
    nval = 1 << m

    def xbits(h: int, bval: int) -> int:
        x = 0
        for pos, inp in enumerate(U):
            x |= ((h >> pos) & 1) << inp
        x |= bval << fam.B
        return x

    atom_objs = [fam.atoms[i] for i in ag.atoms]
    # psi(h, b=1) and psi(v, b=0) tables per atom
    t1 = [sum(((a.value(xbits(h, 1), {}) & 1) << h) for h in range(nval)) for a in atom_objs]
    t0 = [sum(((a.value(xbits(v, 0), {}) & 1) << v) for v in range(nval)) for a in atom_objs]
    sig = 0
    bit = 0

    def push(v: int) -> None:
        nonlocal sig, bit
        if v:
            sig |= 1 << bit
        bit += 1

    push(ag.eval_f([1, 1]))
    for h0 in range(nval):
        push(ag.eval_f([((t >> h0) & 1) for t in t1] + [1, 1]))
    full = (1 << nval) - 1
    for h0 in range(nval):
        for V in range(1, nval + 1 if nval == 1 else (1 << nval)):
            if nval == 1 and V > 1:
                break
            vals = []
            for a_idx in range(len(atom_objs)):
                a = (t1[a_idx] >> h0) & 1
                if a and (V & ~t0[a_idx] & full):
                    a = 0
                vals.append(a)
            push(ag.eval_f(vals + [1, 1]))
    return U, sig


# ----------------------------------------------------------------------------
# Matches on the frame omega
# ----------------------------------------------------------------------------


def refs(fam: Family, ag: Agent) -> list[tuple[int, str]]:
    """(input index, test name) for every test behaviour input the agent's atoms use."""
    out = []
    for i in ag.atoms:
        for inp in fam.atoms[i].inputs:
            if 1 <= inp <= len(fam.tests):
                pair = (inp, fam.tests[inp - 1])
                if pair not in out:
                    out.append(pair)
    return out


def run_match(fam: Family, A: Agent, B: Agent, K: int = 64) -> tuple[int, int, list[int], list[int], int]:
    atomsA = [fam.atoms[i] for i in A.atoms]
    atomsB = [fam.atoms[i] for i in B.atoms]
    convA = [1] * len(atomsA)
    convB = [1] * len(atomsB)
    seqA: list[int] = []
    seqB: list[int] = []
    kmin = max(A.stab, B.stab, 1)
    refsA = refs(fam, A)
    refsB = refs(fam, B)
    for inp, t in refsA:
        if not B.seqs.get(t):
            raise RuntimeError(f"{A.name or A.atoms} references q{t} but the opponent's behaviour vs {t} is not computed")
    for inp, t in refsB:
        if not A.seqs.get(t):
            raise RuntimeError(f"{B.name or B.atoms} references q{t} but the opponent's behaviour vs {t} is not computed")
    for k in range(K):
        pA = A.eval_f(convA + [1, 1])
        pB = B.eval_f(convB + [1, 1])
        seqA.append(pA)
        seqB.append(pB)
        bval = 1 if k == 0 else 0
        xA = pB | (bval << fam.B)
        xB = pA | (bval << fam.B)
        for inp, t in refsA:
            sB = B.seqs[t]
            xA |= sB[min(k, len(sB) - 1)] << inp
        for inp, t in refsB:
            sA = A.seqs[t]
            xB |= sA[min(k, len(sA) - 1)] << inp
        changed = False
        for i, at in enumerate(atomsA):
            if convA[i] and not at.value(xA, {}):
                convA[i] = 0
                changed = True
        for i, at in enumerate(atomsB):
            if convB[i] and not at.value(xB, {}):
                convB[i] = 0
                changed = True
        if k >= kmin and not changed:
            return pA, pB, seqA, seqB, k
    raise RuntimeError("match did not stabilise")


def test_agents(fam: Family) -> dict[str, Agent]:
    """The fixed test agents expressed in this family's input numbering."""
    P = 0
    B = fam.B
    bots: dict[str, Agent] = {
        "DB": Agent((), 0, (0, 0), name="DefectBot"),
        "CB": Agent((), 1, (0, 0), name="CooperateBot"),
    }
    box_p = fam.add_atom((P,), 0b10)
    bots["FB"] = Agent((box_p,), 2, (1, 1), name="FairBot")
    if "DB" in fam.tests:
        qD = 1 + fam.tests.index("DB")
        box_b_or_not_qD = fam.add_atom((qD, B), 0b1101)   # over (qD, b): f(0,0)=1 f(1,0)=0 f(0,1)=1 f(1,1)=1
        bots["PB"] = Agent((box_p, box_b_or_not_qD), 0b1000, (2, 2), name="PrudentBot")
    return bots


def precompute_vs_tests(fam: Family, bots: dict[str, Agent], agents: list[Agent]) -> None:
    """Fill ag.seqs[t] for every agent and every test t, in test-rank order."""
    order = [t for t in TEST_ORDER if t in fam.tests]
    # test agents among themselves first, in rank order: DB, CB are constants; FB references
    # nothing; PB references DB.  Each X vs U is computed after X's own behaviour against
    # everything U references is known.
    for t in bots:
        bots[t].seqs = {}
        bots[t].stab = 0
    for u in order:
        for t in bots:
            X, Y = bots[t], bots[u]
            if u == "DB":
                seq, stab = constant_match(fam, X, 0)
            elif u == "CB":
                seq, stab = constant_match(fam, X, 1)
            else:
                pA, pB, sa, sb, k = run_match(fam, X, Y)
                seq, stab = sa, k
            X.seqs[u] = tuple(seq)
            X.stab = max(X.stab, stab)
    for ag in agents:
        ag.seqs = {}
        ag.stab = 0
        for u in order:
            if u == "DB":
                seq, stab = constant_match(fam, ag, 0)
            elif u == "CB":
                seq, stab = constant_match(fam, ag, 1)
            else:
                pA, pB, sa, sb, k = run_match(fam, ag, bots[u])
                seq, stab = sa, k
            ag.seqs[u] = tuple(seq)
            ag.stab = max(ag.stab, stab)


def constant_match(fam: Family, ag: Agent, opp_coop: int) -> tuple[list[int], int]:
    """Agent vs DefectBot (opp_coop=0: DB cooperates with nobody, including every test)
    or vs CooperateBot (opp_coop=1: cooperates with everybody)."""
    atomsA = [fam.atoms[i] for i in ag.atoms]
    conv = [1] * len(atomsA)
    seq: list[int] = []
    for k in range(64):
        pA = ag.eval_f(conv + [1, 1])
        seq.append(pA)
        bval = 1 if k == 0 else 0
        x = opp_coop | (bval << fam.B)
        for ti in range(len(fam.tests)):
            x |= opp_coop << (1 + ti)
        changed = False
        for i, at in enumerate(atomsA):
            if conv[i] and not at.value(x, {}):
                conv[i] = 0
                changed = True
        if k >= 1 and not changed:
            return seq, k
    raise RuntimeError("constant match did not stabilise")


# ----------------------------------------------------------------------------
# Games, vectorised
# ----------------------------------------------------------------------------

GAME_NAMES = {"TRPS": "Prisoner's Dilemma", "TRSP": "Chicken", "RTPS": "Stag Hunt", "TPRS": "Deadlock", "RTSP": "Harmony", "RPTS": "Assurance"}


def payoff_table(order: str) -> np.ndarray:
    vals = {ch: 4 - i for i, ch in enumerate(order)}
    T, R, P, S = vals["T"], vals["R"], vals["P"], vals["S"]
    tab = np.zeros((2, 2), dtype=np.int8)   # [my action][their action], 1 = cooperate
    tab[1, 1], tab[1, 0], tab[0, 1], tab[0, 0] = R, S, T, P
    return tab


def pure_ir(order: str) -> list[list[int]]:
    tab = payoff_table(order)
    minmax = min(max(int(tab[a, o]) for a in (0, 1)) for o in (0, 1))
    out = set()
    for a in (0, 1):
        for b in (0, 1):
            if tab[a, b] >= minmax and tab[b, a] >= minmax:
                out.add((int(tab[a, b]), int(tab[b, a])))
    return [list(x) for x in sorted(out)]


def analyse(order: str, act: np.ndarray, level_of: np.ndarray, levels: list, names: list[str]) -> dict:
    tab = payoff_table(order)
    payA = tab[act, act.T]                 # payA[a,b] = payoff of a against b
    res = {"order": order, "name": GAME_NAMES.get(order, ""), "levels": []}
    prev_fam = None
    prev_pe = None
    for lvl in levels:
        fam = np.flatnonzero(level_of <= lvl)
        sub = payA[np.ix_(fam, fam)]
        best = sub.max(axis=0)
        pe = (sub == best[None, :]) & (sub.T == best[:, None])
        asub = act[np.ix_(fam, fam)]
        cc = int((pe & (asub == 1) & (asub.T == 1)).sum())
        n_pe = int(pe.sum())
        pays = np.unique(np.stack([sub[pe], sub.T[pe]], axis=1), axis=0) if n_pe else np.zeros((0, 2), dtype=np.int8)
        deaths = 0
        death_examples = []
        if prev_fam is not None:
            pos = np.searchsorted(fam, prev_fam)
            pe_prev_now = pe[np.ix_(pos, pos)]
            dead = prev_pe & ~pe_prev_now
            deaths = int(dead.sum())
            for (i, j) in np.argwhere(dead)[:3]:
                a, b = int(prev_fam[i]), int(prev_fam[j])
                killer = None
                pb, pa = int(payA[a, b]), int(payA[b, a])
                bpos = int(np.searchsorted(fam, b))
                apos = int(np.searchsorted(fam, a))
                if pb < int(best[bpos]):
                    k = int(fam[int(np.argmax(sub[:, bpos]))])
                    killer = {"against": names[b], "new_agent": names[k], "outcome": [int(act[k, b]), int(act[b, k])], "payoff": int(payA[k, b]), "was": pb}
                elif pa < int(best[apos]):
                    k = int(fam[int(np.argmax(sub[:, apos]))])
                    killer = {"against": names[a], "new_agent": names[k], "outcome": [int(act[k, a]), int(act[a, k])], "payoff": int(payA[k, a]), "was": pa}
                death_examples.append({"pair": [names[a], names[b]], "killer": killer})
        births = int(pe.sum()) - (int(prev_pe.sum()) - deaths if prev_pe is not None else 0)
        examples = {}
        for x, y in pays.tolist():
            hit = np.argwhere(pe & (sub == x) & (sub.T == y))
            if hit.size:
                i, j = int(hit[0][0]), int(hit[0][1])
                examples[f"({int(x)}, {int(y)})"] = [names[int(fam[i])], names[int(fam[j])], [int(asub[i, j]), int(asub[j, i])]]
        res["levels"].append({
            "level": list(lvl) if isinstance(lvl, tuple) else int(lvl),
            "agents": int(len(fam)),
            "equilibrium_pairs": int(pe.sum()),
            "equilibrium_payoffs": [[int(x), int(y)] for x, y in pays.tolist()],
            "mutual_cooperation_pairs": cc,
            "deaths_from_previous": deaths,
            "births": births,
            "example_pair_per_payoff": examples,
            "death_examples": death_examples,
        })
        prev_fam, prev_pe = fam, pe
    res["pure_individually_rational_payoffs"] = pure_ir(order)
    return res


# ----------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", default="DB,CB,FB,PB", help="test agents whose q-inputs exist; DB required")
    ap.add_argument("--inputs", default="", help="comma list of input names formulas may use (default: all)")
    ap.add_argument("--max-inputs", type=int, default=2)
    ap.add_argument("--max-atoms", type=int, default=2)
    ap.add_argument("--max-two-input-atoms", type=int, default=-1)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    tests = [t.strip() for t in args.tests.split(",") if t.strip()]
    assert "DB" in tests, "DB is required (PrudentBot references DB)"
    cap = None if args.max_two_input_atoms < 0 else args.max_two_input_atoms
    allowed = [x.strip() for x in args.inputs.split(",") if x.strip()] or None
    t0 = time.time()
    fam, formulas = build_family(tests, args.max_inputs, args.max_atoms, cap, allowed)
    bots = test_agents(fam)
    # dedup by signature: over the full behaviour-input space when that is small (exact),
    # otherwise over each agent's own inputs (sound but may leave behavioural duplicates,
    # which are merged after the outcome matrix is known)
    full_sig = len(fam.behav_inputs) <= 3

    def fsize(ag: Agent) -> int:
        return len(ag.atoms) + sum(fam.atoms[i].n_inputs for i in ag.atoms)

    # each equivalence class keeps the lowest-level representative, and records the
    # minimum of BOTH resource measures over the class (so levels do not depend on which
    # formula was enumerated first)
    best: dict[tuple, Agent] = {}
    for ag in formulas:
        ag.min_size = fsize(ag)
        key = signature(fam, ag, full=full_sig)
        cur = best.get(key)
        if cur is None:
            best[key] = ag
        else:
            if ag.level < cur.level:
                ag.min_size = min(ag.min_size, cur.min_size)
                best[key] = ag
            else:
                cur.min_size = min(cur.min_size, ag.min_size)
    agents = sorted(best.values(), key=lambda a: (a.level, a.atoms, a.ftable))
    print(f"signature dedup: {'full input space (exact)' if full_sig else 'own inputs (behavioural merge follows)'}")
    for ag in agents:
        ag.name = fam.agent_name(ag)
    n = len(agents)
    print(f"tests={tests} inputs={fam.input_names} atoms={len(fam.atoms)} formulas={len(formulas)} distinct={n} ({time.time()-t0:.1f}s)")
    levels_atoms = sorted({ag.level for ag in agents})
    for lvl in levels_atoms:
        print(f"  level {lvl}: {sum(1 for a in agents if a.level == lvl)} new, {sum(1 for a in agents if a.level <= lvl)} cumulative")
    # behaviour vs tests, then self-test
    precompute_vs_tests(fam, bots, agents)
    FB, PB, DB, CB = bots["FB"], bots.get("PB"), bots["DB"], bots["CB"]
    expect = {("FB", "FB"): (1, 1), ("FB", "DB"): (0, 0), ("FB", "CB"): (1, 1), ("DB", "CB"): (0, 1)}
    if PB is not None:
        expect.update({("PB", "CB"): (0, 1), ("PB", "DB"): (0, 0), ("PB", "FB"): (1, 1), ("PB", "PB"): (1, 1)})
    for (x, y), want in expect.items():
        got = run_match(fam, bots[x], bots[y])[:2]
        assert got == want, f"self-test {x} vs {y}: {got} != {want}"
    print("self-test: named-bot outcomes match Barasz et al. (2014)")
    # outcome matrix
    t1 = time.time()
    act = np.zeros((n, n), dtype=np.uint8)
    for a in range(n):
        A = agents[a]
        for b in range(a, n):
            pA, pB, *_ = run_match(fam, A, agents[b])
            act[a, b] = pA
            act[b, a] = pB
        if a % 500 == 0 and a:
            print(f"  matches: row {a}/{n} ({time.time()-t1:.0f}s)")
    print(f"outcome matrix {n}x{n} ({time.time()-t1:.1f}s)")
    # behavioural merge: agents with identical rows and columns are interchangeable for
    # every equilibrium question inside this family; keep the lowest-level representative
    if not full_sig:
        groups: dict[bytes, list[int]] = {}
        for i in range(n):
            key = act[i].tobytes() + b"|" + act[:, i].tobytes()
            groups.setdefault(key, []).append(i)
        keep = []
        for g in groups.values():
            rep = min(g, key=lambda i: (agents[i].level, i))
            agents[rep].level = min(agents[i].level for i in g)
            agents[rep].min_size = min(agents[i].min_size for i in g)
            keep.append(rep)
        keep.sort()
        merged = n - len(keep)
        agents = [agents[i] for i in keep]
        act = act[np.ix_(keep, keep)]
        n = len(agents)
        print(f"behavioural merge: {merged} duplicates removed, {n} agents remain")
    names = [ag.name for ag in agents]
    # JustBot check: Box(qFB) vs FairBot Box(p): identical rows and columns?
    jb_report = None
    if "FB" in tests:
        qF = 1 + tests.index("FB")
        jb_key = fam.add_atom((qF,), 0b10)
        jb = next((i for i, ag in enumerate(agents) if ag.atoms == (jb_key,) and ag.ftable == 2), None)
        fb = next((i for i, ag in enumerate(agents) if ag.atoms == (fam.atom_index[((0,), 0b10)],) and ag.ftable == 2), None)
        if jb is not None and fb is not None:
            same_rows = bool(np.array_equal(act[jb], act[fb]))
            same_cols = bool(np.array_equal(act[:, jb], act[:, fb]))
            jb_report = {"justbot_index": jb, "fairbot_index": fb, "same_rows": same_rows, "same_cols": same_cols}
            print(f"JustBot Box(qFB) vs FairBot Box(p): identical rows={same_rows}, identical columns={same_cols}")
    # stratifications
    level_atoms = [ag.level for ag in agents]
    level_size = np.array([ag.min_size for ag in agents])
    la = np.array([l[0] * 100 + l[1] for l in level_atoms])   # lexicographic code
    lev_codes = sorted(set(la.tolist()))
    size_levels = sorted(set(level_size.tolist()))
    orders = ["".join(p) for p in itertools.permutations("TRPS")]
    games_by = {}
    for sname, (lv, lvls, decode) in {
        "by_atoms_inputs": (la, lev_codes, lambda c: (c // 100, c % 100)),
        "by_size": (level_size, size_levels, lambda c: c),
    }.items():
        t2 = time.time()
        games = {}
        for order in orders:
            g = analyse(order, act, lv, lvls, names)
            for L in g["levels"]:
                if sname == "by_atoms_inputs":
                    L["level"] = list(decode(L["level"]))
            games[order] = g
        games_by[sname] = games
        print(f"equilibrium analysis [{sname}] ({time.time()-t2:.1f}s)")
    unexploitable = [names[b] for b in range(n) if not np.any((act[:, b] == 0) & (act[b, :] == 1))]
    coop_unexpl = [names[b] for b in range(n) if (not np.any((act[:, b] == 0) & (act[b, :] == 1))) and act[b, b] == 1]
    for sname, games in games_by.items():
        print(f"=== {sname} ===")
        print("game | level | agents | PE pairs | PE payoffs | CC pairs | deaths | births")
        for order in ["TRPS", "TRSP", "RTPS", "TPRS", "RTSP"]:
            g = games[order]
            for L in g["levels"]:
                print(f"{order} {g['name'][:12]:12s} | {L['level']} | {L['agents']:5d} | {L['equilibrium_pairs']:9d} | {L['equilibrium_payoffs']} | {L['mutual_cooperation_pairs']:8d} | {L['deaths_from_previous']:5d} | {L['births']:8d}")
        total_deaths = sum(L["deaths_from_previous"] for o in orders for L in games[o]["levels"])
        with_deaths = sum(1 for o in orders if any(L["deaths_from_previous"] for L in games[o]["levels"]))
        eq_ir = sum(1 for o in orders if games[o]["levels"][-1]["equilibrium_payoffs"] == games[o]["pure_individually_rational_payoffs"])
        print(f"  deaths: {total_deaths} in {with_deaths}/24 orderings; top-level PE payoffs = pure IR set in {eq_ir}/24")
        for o in orders:
            for L in games[o]["levels"]:
                if L["death_examples"]:
                    print(f"    {o} level {L['level']}: {L['deaths_from_previous']} deaths; e.g. {L['death_examples'][0]}")
                    break
    print(f"unexploitable: {len(unexploitable)}; unexploitable & self-cooperating: {len(coop_unexpl)}")
    print("  e.g.", "; ".join(coop_unexpl[:8]))
    summary = {
        "tests": tests, "inputs": fam.input_names, "max_inputs": args.max_inputs, "max_atoms": args.max_atoms,
        "max_two_input_atoms": cap, "atoms": len(fam.atoms), "formulas": len(formulas), "distinct_agents": n,
        "agents_per_level_by_atoms_inputs": {str(l): sum(1 for a in agents if a.level == l) for l in levels_atoms},
        "agents_per_level_by_size": {str(s): int((level_size == s).sum()) for s in size_levels},
        "justbot_check": jb_report,
        "unexploitable_count": len(unexploitable), "unexploitable_and_self_cooperating": coop_unexpl,
        "games": games_by, "agent_names": names,
        "agent_levels_by_atoms_inputs": [list(l) for l in level_atoms], "agent_levels_by_size": level_size.tolist(),
    }
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, indent=1, sort_keys=True)
        print("wrote", args.out)
    print(f"total {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
