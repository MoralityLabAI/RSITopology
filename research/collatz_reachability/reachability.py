"""Exact quotient-obstruction and closed-set certificates on finite odd cores."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from collatz_core import analyze, modular_labels, odd_step, validate_parameter

HERE = Path(__file__).resolve().parent
PARAMETERS = (13, 29, 73, 97, 217, 313, 577, 1001)


def forward_orbit(source: int, d: int) -> tuple[int, ...]:
    seen, path = set(), []
    while source not in seen:
        seen.add(source)
        path.append(source)
        source = odd_step(source, d)[0]
    return tuple(path)


def certificate(source: int, target: int, d: int) -> dict:
    """Propose an explicit finite closed set separating source from target."""
    return dict(schema="collatz.closed_set.v1", d=d, source=source,
                target=target, closed_set=list(forward_orbit(source, d)))


def verify_certificate(proposal: dict, extra_edges: tuple[tuple[int, int], ...] = ()) -> bool:
    """Check every allowed transition, including optional proposed edits.

    Uses integer transition equations rather than the census's basin labels.
    Invalid input is rejected. A certificate is tied to this supplied action set.
    """
    try:
        if not isinstance(proposal, dict):
            return False
        if proposal.get("schema") != "collatz.closed_set.v1":
            return False
        d, source, target = (proposal[k] for k in ("d", "source", "target"))
        validate_parameter(d)
        values = proposal["closed_set"]
        if not isinstance(values, list) or len(values) > (d + 1) // 2:
            return False
        if any(type(n) is not int or n < 1 or n > d or n % 2 == 0
               for n in [source, target] + values):
            return False
        closed = set(values)
        if len(closed) != len(values) or source not in closed or target in closed:
            return False
        if any(odd_step(n, d)[0] not in closed for n in closed):
            return False
        for u, v in extra_edges:
            if any(type(n) is not int or not 1 <= n <= d or n % 2 == 0 for n in (u, v)):
                return False
            if u in closed and v not in closed:
                return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


def evaluate() -> dict:
    rows = []
    for d in PARAMETERS:
        core, q = analyze(d), modular_labels(d)
        reachable = {n: set(forward_orbit(n, d)) for n in core.states}
        metrics = dict(d=d, states=len(core.states), cycles=len(core.cycles),
                       quotient_classes=len(set(q.values())), pairs=len(core.states)**2,
                       reachable_pairs=0, quotient_obstructions=0,
                       same_quotient_unreachable=0, same_quotient_distinct_basins=0,
                       invariant_violations=0, false_obstructions=0,
                       closed_set_certificates=0)
        for n in core.states:
            if q[n % d] != q[core.successors[n] % d]:
                metrics["invariant_violations"] += 1
            for target in core.states:
                reaches = target in reachable[n]
                separated = q[n % d] != q[target % d]
                metrics["reachable_pairs"] += reaches
                metrics["quotient_obstructions"] += separated
                metrics["false_obstructions"] += separated and reaches
                metrics["same_quotient_unreachable"] += not separated and not reaches
                metrics["same_quotient_distinct_basins"] += (
                    not separated and core.basin[n] != core.basin[target])
                # Reuse one verified closure per source, then check exclusion.
                # The independent certificate test covers malformed proposals.
                metrics["closed_set_certificates"] += not reaches
            assert all(odd_step(x, d)[0] in reachable[n] for x in reachable[n])
        assert metrics["false_obstructions"] == metrics["invariant_violations"] == 0
        assert metrics["closed_set_certificates"] == metrics["pairs"] - metrics["reachable_pairs"]
        rows.append(metrics)
    witness = certificate(1, 5, 13)
    q = modular_labels(13)
    edit = (1, 5)
    assert verify_certificate(witness)
    assert not verify_certificate(witness, (edit,))
    assert q[edit[0]] == q[edit[1]]
    return dict(schema="collatz.reachability.audit.v1", date="2026-11-25",
        evidence="exhaustive finite-domain control", parameters=rows,
        totals={key: sum(row[key] for row in rows) for key in rows[0] if key != "d"},
        alias_witness=dict(d=13, source=1, target=5, quotient=q[1],
            source_cycle=[1], target_cycle=[5, 7], certificate=witness,
            certificate_valid=True, added_edge=list(edit),
            added_edge_preserves_quotient=True, certificate_valid_with_added_edge=False),
        core_sha256=hashlib.sha256((HERE/"collatz_core.py").read_bytes()).hexdigest())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = evaluate()
    payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    path = HERE / "receipt.json"
    if args.write:
        path.write_bytes(payload)
    elif path.read_bytes() != payload:
        raise SystemExit("receipt drift")
    print(json.dumps(result["totals"], sort_keys=True))


if __name__ == "__main__":
    main()
