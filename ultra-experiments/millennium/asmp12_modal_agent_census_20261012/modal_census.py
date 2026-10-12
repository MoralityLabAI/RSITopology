"""ASMP-12 modal-agent census (2026-10-12).

Exact, resource-indexed program-equilibrium census for rank-<=1 modal agents in
the sense of Barasz et al. (2014), evaluated in the closed fragment of the
provability logic GL on the frame omega.

Semantics (see NOTE.md for the justification):
  * An agent is a Boolean function of at most two "provability atoms"; each atom
    is Box(psi) where psi is a Boolean function of at most two of the inputs
        p  = "the opponent cooperates with me",
        qD = "the opponent cooperates with DefectBot",
        qC = "the opponent cooperates with CooperateBot",
        b  = Box(False)   (true exactly at world 0; encodes PA+1 provability
                           via Box_1(x) = Box(b or x)).
    Inputs may only occur under a Box, so every agent is modalized and the
    mutual fixed points of a match are unique (de Jongh-Sambin).
  * Worlds 0,1,2,... of the frame omega: Box(x) is true at world k iff x is true
    at every world j < k.  A letterless sentence is provable in PA iff true at
    every finite world, and true in the standard model iff true at the limit
    world omega, whose Box evaluates the conjunction over all finite worlds
    (Solovay 1976; Boolos 1993, ch. 7).  An agent's actual action against an
    opponent is therefore the eventual (stabilised) value of its fixed point.
  * Resource level of an agent: (number of atoms, max inputs per atom), minimised
    over all formulas with the same semantic signature.

Outputs: distinct agents per level, the full outcome matrix, and for each of the
24 strict orderings of (T,R,P,S) the program equilibria within each resource
level, equilibrium outcomes, and deaths/births as the level grows.

Stdlib only; exact (Boolean) arithmetic.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from dataclasses import dataclass

INPUT_NAMES = ("p", "qD", "qC", "b")  # bit positions 0..3 in a 16-entry psi table

# ----------------------------------------------------------------------------
# Atoms: psi as a 16-entry truth table over (p,qD,qC,b); atom = Box(psi).
# ----------------------------------------------------------------------------


def psi_table_from_function(inputs: tuple[int, ...], table: int) -> int:
    """Expand a Boolean function on the given input indices (truth table `table`
    indexed by the inputs' bits in order) to a 16-entry table over all four inputs."""
    full = 0
    for idx in range(16):
        bits = [(idx >> i) & 1 for i in range(4)]
        local = 0
        for pos, inp in enumerate(inputs):
            local |= bits[inp] << pos
        if (table >> local) & 1:
            full |= 1 << idx
    return full


def enumerate_psis(allowed_inputs: tuple[int, ...], max_inputs: int) -> dict[int, tuple[tuple[int, ...], int]]:
    """All Boolean functions depending on <= max_inputs of the allowed inputs,
    excluding the constant True (Box(True) is trivially true).  Returns
    {table16: (inputs, local_table)} keeping the smallest input set for each."""
    found: dict[int, tuple[tuple[int, ...], int]] = {}
    # constant False -> Box(False) = b itself as an atom
    found[0] = ((), 0)
    for n in range(1, max_inputs + 1):
        for inputs in itertools.combinations(allowed_inputs, n):
            for table in range(1 << (1 << n)):
                full = psi_table_from_function(inputs, table)
                if full == 0xFFFF:
                    continue
                if full not in found:
                    found[full] = (inputs, table)
    return found


def psi_name(inputs: tuple[int, ...], table: int) -> str:
    n = len(inputs)
    if n == 0:
        return "F"
    rows = []
    for local in range(1 << n):
        if (table >> local) & 1:
            lits = []
            for pos, inp in enumerate(inputs):
                lits.append(INPUT_NAMES[inp] if (local >> pos) & 1 else "~" + INPUT_NAMES[inp])
            rows.append("&".join(lits))
    if not rows:
        return "F"
    if len(rows) == (1 << n):
        return "T"
    return "|".join(rows)


@dataclass(frozen=True)
class Atom:
    table16: int
    inputs: tuple[int, ...]
    local: int

    @property
    def n_inputs(self) -> int:
        return len(self.inputs)

    def name(self) -> str:
        return "Box(" + psi_name(self.inputs, self.local) + ")"


# ----------------------------------------------------------------------------
# Agents: Boolean function of <= 2 atoms.
# ----------------------------------------------------------------------------


@dataclass
class Agent:
    atoms: tuple[int, ...]      # indices into the atom list
    ftable: int                 # truth table over atom values (1, 2 or 4 entries)
    level: tuple[int, int]      # (n_atoms, max inputs per atom)
    signature: int = 0
    name: str = ""
    seqDB: tuple[int, ...] = ()   # p-sequence of this agent vs DefectBot (worlds 0..)
    seqCB: tuple[int, ...] = ()   # vs CooperateBot
    stab: int = 0                 # index from which both sequences are constant
    actDB: int = 0
    actCB: int = 0

    def eval_f(self, a0: int, a1: int) -> int:
        n = len(self.atoms)
        if n == 0:
            return self.ftable & 1
        if n == 1:
            return (self.ftable >> a0) & 1
        return (self.ftable >> (a0 | (a1 << 1))) & 1


def agent_name(agent: Agent, atoms: list[Atom]) -> str:
    n = len(agent.atoms)
    if n == 0:
        return "CooperateBot" if agent.ftable & 1 else "DefectBot"
    names = [atoms[i].name() for i in agent.atoms]
    if n == 1:
        t = agent.ftable & 3
        return {0: "F", 3: "T", 2: names[0], 1: "~" + names[0]}[t]
    rows = []
    for local in range(4):
        if (agent.ftable >> local) & 1:
            lits = [names[0] if local & 1 else "~" + names[0], names[1] if local & 2 else "~" + names[1]]
            rows.append("(" + " & ".join(lits) + ")")
    return " | ".join(rows) if rows else "F"


# ----------------------------------------------------------------------------
# Semantic signature (exact dedup within the omega-frame semantics).
# ----------------------------------------------------------------------------


def atom_signature_parts(atom: Atom) -> tuple[int, int]:
    """(t1, t0): t1 bit h = psi(h, b=1), t0 bit v = psi(v, b=0) for h,v in {0..7} over (p,qD,qC)."""
    t1 = 0
    t0 = 0
    for h in range(8):
        if (atom.table16 >> (h | 8)) & 1:
            t1 |= 1 << h
        if (atom.table16 >> h) & 1:
            t0 |= 1 << h
    return t1, t0


def agent_signature(agent: Agent, atoms: list[Atom]) -> int:
    parts = [atom_signature_parts(atoms[i]) for i in agent.atoms]
    sig = 0
    bit = 0

    def push(v: int) -> None:
        nonlocal sig, bit
        if v:
            sig |= 1 << bit
        bit += 1

    # world 0: all atoms true
    push(agent.eval_f(1, 1))
    # world 1: atom = psi(h0, b=1)
    for h0 in range(8):
        vals = [((t1 >> h0) & 1) for (t1, t0) in parts] + [1, 1]
        push(agent.eval_f(vals[0], vals[1]))
    # world >= 2: atom = psi(h0,1) & AND_{v in V} psi(v,0), V nonempty subset of {0..7}
    for h0 in range(8):
        for V in range(1, 256):
            vals = []
            for (t1, t0) in parts:
                a = (t1 >> h0) & 1
                if a and (V & ~t0 & 0xFF):
                    a = 0
                vals.append(a)
            vals += [1, 1]
            push(agent.eval_f(vals[0], vals[1]))
    return sig


# ----------------------------------------------------------------------------
# Match evaluation on the frame omega.
# ----------------------------------------------------------------------------


def run_match(A: Agent, B: Agent, atoms: list[Atom], K: int = 64) -> tuple[list[int], list[int], int]:
    """Return (seqA, seqB, stab_index): p-values of A and B at worlds 0..k_stop,
    where the state is proved constant from stab_index on.  Requires A.seqDB etc."""
    atomsA = [atoms[i] for i in A.atoms]
    atomsB = [atoms[i] for i in B.atoms]
    convA = [1] * len(atomsA)
    convB = [1] * len(atomsB)
    seqA: list[int] = []
    seqB: list[int] = []
    kmin = max(A.stab, B.stab, 1)

    def inp(p: int, qD: int, qC: int, b: int) -> int:
        return p | (qD << 1) | (qC << 2) | (b << 3)

    for k in range(K):
        pA = A.eval_f(convA[0] if len(convA) > 0 else 1, convA[1] if len(convA) > 1 else 1)
        pB = B.eval_f(convB[0] if len(convB) > 0 else 1, convB[1] if len(convB) > 1 else 1)
        seqA.append(pA)
        seqB.append(pB)
        b = 1 if k == 0 else 0
        qDB = B.seqDB[min(k, len(B.seqDB) - 1)]
        qCB = B.seqCB[min(k, len(B.seqCB) - 1)]
        qDA = A.seqDB[min(k, len(A.seqDB) - 1)]
        qCA = A.seqCB[min(k, len(A.seqCB) - 1)]
        iA = inp(pB, qDB, qCB, b)
        iB = inp(pA, qDA, qCA, b)
        changed = False
        for i, at in enumerate(atomsA):
            if convA[i] and not ((at.table16 >> iA) & 1):
                convA[i] = 0
                changed = True
        for i, at in enumerate(atomsB):
            if convB[i] and not ((at.table16 >> iB) & 1):
                convB[i] = 0
                changed = True
        if k >= kmin and not changed:
            # state is a fixed point: p-values at every later world equal pA, pB
            return seqA, seqB, k
    raise RuntimeError("match did not stabilise within K worlds")


def constant_agent_sequences(agent: Agent, atoms: list[Atom], opp_p: int, opp_qD: int, opp_qC: int) -> tuple[list[int], int]:
    """Agent vs a constant opponent (DefectBot or CooperateBot)."""
    atomsA = [atoms[i] for i in agent.atoms]
    conv = [1] * len(atomsA)
    seq: list[int] = []
    for k in range(64):
        pA = agent.eval_f(conv[0] if len(conv) > 0 else 1, conv[1] if len(conv) > 1 else 1)
        seq.append(pA)
        b = 1 if k == 0 else 0
        i = opp_p | (opp_qD << 1) | (opp_qC << 2) | (b << 3)
        changed = False
        for j, at in enumerate(atomsA):
            if conv[j] and not ((at.table16 >> i) & 1):
                conv[j] = 0
                changed = True
        if k >= 1 and not changed:
            return seq, k
    raise RuntimeError("constant match did not stabilise")


# ----------------------------------------------------------------------------
# Enumeration.
# ----------------------------------------------------------------------------


def build_family(allowed_inputs: tuple[int, ...], max_inputs: int, max_atoms: int) -> tuple[list[Atom], list[Agent]]:
    psis = enumerate_psis(allowed_inputs, max_inputs)
    atoms = [Atom(t, inputs, local) for t, (inputs, local) in sorted(psis.items())]
    formulas: list[Agent] = []
    formulas.append(Agent(atoms=(), ftable=0, level=(0, 0)))  # DefectBot
    formulas.append(Agent(atoms=(), ftable=1, level=(0, 0)))  # CooperateBot
    for i, at in enumerate(atoms):
        for ft in (1, 2):  # ~a, a   (tables over one atom: bit0 = f(0), bit1 = f(1))
            formulas.append(Agent(atoms=(i,), ftable=ft, level=(1, at.n_inputs)))
    if max_atoms >= 2:
        for i, j in itertools.combinations(range(len(atoms)), 2):
            lvl = (2, max(atoms[i].n_inputs, atoms[j].n_inputs))
            for ft in range(16):
                # keep only functions depending on both atoms
                dep0 = any(((ft >> (a0 | (a1 << 1))) & 1) != ((ft >> ((1 - a0) | (a1 << 1))) & 1) for a0 in range(2) for a1 in range(2))
                dep1 = any(((ft >> (a0 | (a1 << 1))) & 1) != ((ft >> (a0 | ((1 - a1) << 1))) & 1) for a0 in range(2) for a1 in range(2))
                if dep0 and dep1:
                    formulas.append(Agent(atoms=(i, j), ftable=ft, level=lvl))
    # semantic dedup: keep the lowest-level formula per signature
    best: dict[int, Agent] = {}
    for ag in formulas:
        sig = agent_signature(ag, atoms)
        ag.signature = sig
        cur = best.get(sig)
        if cur is None or ag.level < cur.level:
            best[sig] = ag
    agents = sorted(best.values(), key=lambda a: (a.level, a.atoms, a.ftable))
    for ag in agents:
        ag.name = agent_name(ag, atoms)
    return atoms, agents


def precompute_constants(agents: list[Agent], atoms: list[Atom]) -> None:
    # DefectBot: p=0, cooperates with DB: 0, with CB: 0.  CooperateBot: 1,1,1.
    for ag in agents:
        sDB, kDB = constant_agent_sequences(ag, atoms, 0, 0, 0)
        sCB, kCB = constant_agent_sequences(ag, atoms, 1, 1, 1)
        ag.seqDB = tuple(sDB)
        ag.seqCB = tuple(sCB)
        ag.stab = max(kDB, kCB)
        ag.actDB = sDB[-1]
        ag.actCB = sCB[-1]


# ----------------------------------------------------------------------------
# Games and equilibria.
# ----------------------------------------------------------------------------

GAME_NAMES = {
    "TRPS": "Prisoner's Dilemma",
    "TRSP": "Chicken",
    "RTPS": "Stag Hunt",
    "TPRS": "Deadlock",
    "RTSP": "Harmony",
    "RPTS": "Assurance (coordination)",
}


def payoff_matrix(order: str) -> dict[tuple[int, int], int]:
    vals = {ch: 4 - i for i, ch in enumerate(order)}  # first in order gets 4
    T, R, P, S = vals["T"], vals["R"], vals["P"], vals["S"]
    # key: (my action, their action), 1 = cooperate
    return {(1, 1): R, (1, 0): S, (0, 1): T, (0, 0): P}


def analyse_game(order: str, agents: list[Agent], outcome: list[list[tuple[int, int]]],
                 level_of: list, levels: list) -> dict:
    """level_of[i] is the resource level of agent i under the chosen stratification;
    levels is the sorted list of cumulative levels (agents with level <= L are in family L)."""
    pay = payoff_matrix(order)
    n = len(agents)
    payA = [[pay[outcome[a][b]] for b in range(n)] for a in range(n)]
    result = {"order": order, "name": GAME_NAMES.get(order, ""), "levels": []}
    prev_pe: set[tuple[int, int]] = set()
    for lvl in levels:
        fam = [i for i in range(n) if level_of[i] <= lvl]
        best = {b: max(payA[a][b] for a in fam) for b in fam}
        pe = {(a, b) for a in fam for b in fam if payA[a][b] == best[b] and payA[b][a] == best[a]}
        outcomes = sorted({(payA[a][b], payA[b][a]) for (a, b) in pe})
        actions = sorted({outcome[a][b] for (a, b) in pe})
        deaths = {pr for pr in prev_pe if pr not in pe}
        births = {pr for pr in pe if pr not in prev_pe}
        cc_pairs = [(a, b) for (a, b) in pe if outcome[a][b] == (1, 1)]
        examples = {}
        for (a, b) in sorted(pe):
            key = str((payA[a][b], payA[b][a]))
            if key not in examples:
                examples[key] = [agents[a].name, agents[b].name, list(outcome[a][b])]
        death_examples = []
        for (a, b) in sorted(deaths)[:3]:
            # identify a newly admitted agent that strictly improves on the dying pair
            killer = None
            if payA[a][b] < best[b]:
                k = max(fam, key=lambda x: payA[x][b])
                killer = ["vs", agents[b].name, "new agent", agents[k].name, "outcome", list(outcome[k][b]), "payoff", payA[k][b], "was", payA[a][b]]
            elif payA[b][a] < best[a]:
                k = max(fam, key=lambda x: payA[x][a])
                killer = ["vs", agents[a].name, "new agent", agents[k].name, "outcome", list(outcome[k][a]), "payoff", payA[k][a], "was", payA[b][a]]
            death_examples.append([agents[a].name, agents[b].name, killer])
        result["levels"].append({
            "level": list(lvl) if isinstance(lvl, tuple) else lvl,
            "agents": len(fam),
            "equilibrium_pairs": len(pe),
            "equilibrium_payoffs": outcomes,
            "equilibrium_action_profiles": [list(x) for x in actions],
            "mutual_cooperation_pairs": len(cc_pairs),
            "deaths_from_previous": len(deaths),
            "survivors_from_previous": len(prev_pe) - len(deaths),
            "births": len(births),
            "example_pair_per_payoff": examples,
            "death_examples": death_examples,
        })
        prev_pe = pe
    return result


def pure_ir_outcomes(order: str) -> list[tuple[int, int]]:
    """Pure action profiles whose payoffs give each player at least the pure minmax value."""
    pay = payoff_matrix(order)
    minmax = min(max(pay[(a, o)] for a in (0, 1)) for o in (0, 1))  # opponent minimises my best reply
    out = []
    for a in (0, 1):
        for b in (0, 1):
            if pay[(a, b)] >= minmax and pay[(b, a)] >= minmax:
                out.append((pay[(a, b)], pay[(b, a)]))
    return sorted(set(out))


# ----------------------------------------------------------------------------
# Named bots for the correctness tests.
# ----------------------------------------------------------------------------


def find_atom(atoms: list[Atom], table16: int) -> int:
    for i, at in enumerate(atoms):
        if at.table16 == table16:
            return i
    raise KeyError(hex(table16))


def named_bots(atoms: list[Atom]) -> dict[str, Agent]:
    P, QD, QC, B = 0, 1, 2, 3
    box_p = find_atom(atoms, psi_table_from_function((P,), 0b10))            # Box(p)
    box_b_or_not_qD = find_atom(atoms, psi_table_from_function((QD, B), 0b1101))  # Box(b | ~qD): table over (qD,b): f(0,0)=1,f(1,0)=0,f(0,1)=1,f(1,1)=1
    box_qD = find_atom(atoms, psi_table_from_function((QD,), 0b10))
    bots = {
        "DefectBot": Agent(atoms=(), ftable=0, level=(0, 0)),
        "CooperateBot": Agent(atoms=(), ftable=1, level=(0, 0)),
        "FairBot": Agent(atoms=(box_p,), ftable=2, level=(1, 1)),
        "PrudentBot": Agent(atoms=(box_p, box_b_or_not_qD), ftable=0b1000, level=(2, 2)),  # a0 & a1
        "TrollBot": Agent(atoms=(box_qD,), ftable=2, level=(1, 1)),
    }
    for ag in bots.values():
        ag.signature = agent_signature(ag, atoms)
    return bots


def self_test(atoms: list[Atom]) -> None:
    bots = named_bots(atoms)
    precompute_constants(list(bots.values()), atoms)

    def act(a: str, b: str) -> tuple[int, int]:
        sa, sb, _ = run_match(bots[a], bots[b], atoms)
        return sa[-1], sb[-1]

    expect = {
        ("FairBot", "FairBot"): (1, 1),
        ("FairBot", "DefectBot"): (0, 0),
        ("FairBot", "CooperateBot"): (1, 1),
        ("DefectBot", "CooperateBot"): (0, 1),
        ("PrudentBot", "CooperateBot"): (0, 1),
        ("PrudentBot", "DefectBot"): (0, 0),
        ("PrudentBot", "FairBot"): (1, 1),
        ("PrudentBot", "PrudentBot"): (1, 1),
        ("FairBot", "PrudentBot"): (1, 1),
    }
    for (a, b), want in expect.items():
        got = act(a, b)
        assert got == want, f"self-test failed: {a} vs {b}: got {got}, want {want}"
    # Loebian cooperation must be *provable*: FairBot vs FairBot true at every world.
    sa, sb, _ = run_match(bots["FairBot"], bots["FairBot"], atoms)
    assert all(sa) and all(sb)
    # FairBot vs DefectBot: FairBot's cooperation is true at world 0 only (not refutable in PA).
    sa, _, _ = run_match(bots["FairBot"], bots["DefectBot"], atoms)
    assert sa[0] == 1 and all(v == 0 for v in sa[1:])
    print("self-test: named-bot outcomes match Barasz et al. (2014)")


# ----------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="p,qD,b", help="comma list from p,qD,qC,b")
    ap.add_argument("--max-inputs", type=int, default=2)
    ap.add_argument("--max-atoms", type=int, default=2)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    allowed = tuple(INPUT_NAMES.index(x.strip()) for x in args.inputs.split(","))
    t0 = time.time()
    atoms, agents = build_family(allowed, args.max_inputs, args.max_atoms)
    self_test(atoms)
    precompute_constants(agents, atoms)
    n = len(agents)
    levels = sorted({ag.level for ag in agents})
    print(f"inputs={args.inputs} atoms={len(atoms)} distinct agents={n} levels={levels} ({time.time()-t0:.1f}s)")
    for lvl in levels:
        print(f"  level {lvl}: {sum(1 for ag in agents if ag.level == lvl)} new agents, {sum(1 for ag in agents if ag.level <= lvl)} cumulative")
    # full outcome matrix
    outcome: list[list[tuple[int, int]]] = [[(0, 0)] * n for _ in range(n)]
    t1 = time.time()
    for a in range(n):
        for b in range(a, n):
            sa, sb, _ = run_match(agents[a], agents[b], atoms)
            outcome[a][b] = (sa[-1], sb[-1])
            outcome[b][a] = (sb[-1], sa[-1])
    print(f"outcome matrix: {n*n} entries ({time.time()-t1:.1f}s)")
    # consistency: agent vs constants must agree with precomputed
    db = next(i for i, ag in enumerate(agents) if ag.level == (0, 0) and ag.ftable == 0)
    cb = next(i for i, ag in enumerate(agents) if ag.level == (0, 0) and ag.ftable == 1)
    for a in range(n):
        assert outcome[a][db][0] == agents[a].actDB and outcome[a][cb][0] == agents[a].actCB
    orders = ["".join(p) for p in itertools.permutations("TRPS")]
    # Stratification A: (atoms, max inputs per atom).  Stratification B: formula size
    # = atoms + total inputs over atoms (constants 0, Box(F) 1, FairBot 2, PrudentBot 5).
    level_atoms = [ag.level for ag in agents]
    level_size = [len(ag.atoms) + sum(atoms[i].n_inputs for i in ag.atoms) for ag in agents]
    size_levels = sorted(set(level_size))
    strata = {
        "by_atoms_inputs": (level_atoms, levels),
        "by_size": (level_size, size_levels),
    }
    games_by = {}
    for sname, (lv, lvls) in strata.items():
        t2 = time.time()
        games = {}
        for order in orders:
            games[order] = analyse_game(order, agents, outcome, lv, lvls)
            games[order]["pure_individually_rational_payoffs"] = pure_ir_outcomes(order)
        games_by[sname] = games
        print(f"equilibrium analysis [{sname}]: {len(orders)} orderings x {len(lvls)} levels ({time.time()-t2:.1f}s)")
    # exploitability in the top family: agents against which nobody obtains (D,C)
    unexploitable = [agents[b].name for b in range(n) if all(outcome[a][b] != (0, 1) for a in range(n))]
    coop_unexploitable = [agents[b].name for b in range(n)
                          if all(outcome[a][b] != (0, 1) for a in range(n)) and outcome[b][b] == (1, 1)]
    summary = {
        "inputs": args.inputs,
        "max_inputs": args.max_inputs,
        "max_atoms": args.max_atoms,
        "atoms": len(atoms),
        "distinct_agents": n,
        "levels_by_atoms_inputs": [list(l) for l in levels],
        "agents_per_level_by_atoms_inputs": {str(l): sum(1 for ag in agents if ag.level == l) for l in levels},
        "levels_by_size": size_levels,
        "agents_per_level_by_size": {str(s): sum(1 for x in level_size if x == s) for s in size_levels},
        "unexploitable_agents": unexploitable,
        "unexploitable_and_self_cooperating": coop_unexploitable,
        "games": games_by,
        "agent_names": [ag.name for ag in agents],
        "agent_levels_by_atoms_inputs": [list(ag.level) for ag in agents],
        "agent_levels_by_size": level_size,
    }
    for sname, games in games_by.items():
        print()
        print(f"=== stratification {sname} ===")
        print("game  | level | agents | PE pairs | PE payoff set | CC pairs | deaths | births")
        for order in ["TRPS", "TRSP", "RTPS", "TPRS", "RTSP"]:
            g = games[order]
            for L in g["levels"]:
                print(f"{order} {g['name'][:14]:14s} | {L['level']} | {L['agents']:4d} | {L['equilibrium_pairs']:7d} | {L['equilibrium_payoffs']} | {L['mutual_cooperation_pairs']:7d} | {L['deaths_from_previous']:4d} | {L['births']:7d}")
        print()
        print("deaths summary over all 24 orderings:")
        total_deaths = 0
        eq_ir = 0
        for order in orders:
            g = games[order]
            d = sum(L["deaths_from_previous"] for L in g["levels"])
            total_deaths += d
            top = g["levels"][-1]
            if top["equilibrium_payoffs"] == [list(x) for x in g["pure_individually_rational_payoffs"]] or top["equilibrium_payoffs"] == g["pure_individually_rational_payoffs"]:
                eq_ir += 1
            if d:
                ex = next((L["death_examples"][0] for L in g["levels"] if L["death_examples"]), None)
                lvl = next((L["level"] for L in g["levels"] if L["deaths_from_previous"]), None)
                print(f"  {order} {g['name'][:12]:12s}: {d} deaths; first at level {lvl}; example dying pair: {ex}")
        print(f"  total deaths: {total_deaths}; orderings with deaths: {sum(1 for o in orders if sum(L['deaths_from_previous'] for L in games[o]['levels']))}/24")
        print(f"  orderings whose top-level PE payoff set equals the pure individually-rational set: {eq_ir}/24")
    print()
    print(f"unexploitable agents in the top family ({len(unexploitable)}):", ", ".join(unexploitable[:12]), "..." if len(unexploitable) > 12 else "")
    print(f"unexploitable and self-cooperating ({len(coop_unexploitable)}):", ", ".join(coop_unexploitable[:12]), "..." if len(coop_unexploitable) > 12 else "")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1, sort_keys=True)
        print("wrote", args.out)
    print(f"total {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
