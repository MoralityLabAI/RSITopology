from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import networkx as nx


HERE = Path(__file__).resolve().parent
ASMP9 = HERE.parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph_objects(
    value: Any, pointer: str = "$"
) -> Iterable[tuple[str, int, tuple[tuple[int, int], ...]]]:
    if isinstance(value, dict):
        node_count = value.get("node_count")
        raw_edges = value.get("edges")
        if (
            isinstance(node_count, int)
            and isinstance(raw_edges, list)
            and all(
                isinstance(edge, list)
                and len(edge) == 2
                and all(isinstance(vertex, int) for vertex in edge)
                for edge in raw_edges
            )
        ):
            yield (
                pointer,
                node_count,
                tuple(tuple(edge) for edge in raw_edges),
            )
        for key, child in value.items():
            yield from graph_objects(child, f"{pointer}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from graph_objects(child, f"{pointer}[{index}]")


def graph_record(
    path: Path,
    pointer: str,
    node_count: int,
    edges: tuple[tuple[int, int], ...],
) -> dict[str, Any]:
    graph = nx.Graph()
    graph.add_nodes_from(range(node_count))
    graph.add_edges_from(edges)
    return {
        "degree_sequence": sorted(
            (degree for _, degree in graph.degree()), reverse=True
        ),
        "edge_count": len(edges),
        "edges": [list(edge) for edge in edges],
        "node_count": node_count,
        "pointer": pointer,
        "protocol_path": path.relative_to(ASMP9).as_posix(),
        "protocol_sha256": sha256(path),
        "weisfeiler_lehman_hash": nx.weisfeiler_lehman_graph_hash(
            graph
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)

    records: list[dict[str, Any]] = []
    protocol_paths: list[Path] = []
    for path in sorted(ASMP9.rglob("protocol*.json")):
        if HERE in path.parents:
            continue
        protocol_paths.append(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        for pointer, node_count, edges in graph_objects(value):
            records.append(
                graph_record(
                    path, pointer, node_count, edges
                )
            )

    payload = {
        "graph_record_count": len(records),
        "method": (
            "recursive extraction of dictionaries containing integer "
            "node_count and simple edge-pair lists from every earlier "
            "ASMP-9 protocol*.json"
        ),
        "protocol_file_count": len(protocol_paths),
        "records": records,
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "graph_record_count": len(records),
                "output": str(output),
                "sha256": sha256(output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

