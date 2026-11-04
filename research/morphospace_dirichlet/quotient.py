"""QD-01: exact energy pullback and spectral autonomy defect on finite graphs."""
from fractions import Fraction

def energy(edges, values):
    """Undirected edges listed once as (u, v, nonnegative rational weight)."""
    return sum((Fraction(w) * (values[u] - values[v]) ** 2
                for u, v, w in edges), Fraction(0))

def quotient_edges(edges, grouping):
    weights = {}
    for u, v, raw_weight in edges:
        a, b = grouping[u], grouping[v]
        if a == b:
            continue
        pair = tuple(sorted((a, b)))
        weights[pair] = weights.get(pair, Fraction(0)) + Fraction(raw_weight)
    return tuple((a, b, w) for (a, b), w in sorted(weights.items()))

def laplacian_action(vertices, edges, values):
    answer = {u: Fraction(0) for u in vertices}
    for u, v, weight in edges:
        dx = Fraction(weight) * (values[u] - values[v])
        answer[u] += dx
        answer[v] -= dx
    return answer

def squared_autonomy_defect(vertices, edges, grouping, macro_values):
    values = {u: macro_values[grouping[u]] for u in vertices}
    lap = laplacian_action(vertices, edges, values)
    fibres = {}
    for u in vertices:
        fibres.setdefault(grouping[u], []).append(u)
    mean = {
        a: sum((lap[u] for u in fibre), Fraction(0)) / len(fibre)
        for a, fibre in fibres.items()
    }
    return sum(((lap[u] - mean[grouping[u]]) ** 2 for u in vertices), Fraction(0))

def externally_equitable(vertices, edges, grouping):
    labels = set(grouping[u] for u in vertices)
    outgoing = {u: {b: Fraction(0) for b in labels if b != grouping[u]}
                for u in vertices}
    for u, v, weight in edges:
        if grouping[u] == grouping[v]:
            continue
        outgoing[u][grouping[v]] += Fraction(weight)
        outgoing[v][grouping[u]] += Fraction(weight)
    reference = {}
    for u in vertices:
        a = grouping[u]
        if a in reference and reference[a] != outgoing[u]:
            return False
        reference[a] = outgoing[u]
    return True
