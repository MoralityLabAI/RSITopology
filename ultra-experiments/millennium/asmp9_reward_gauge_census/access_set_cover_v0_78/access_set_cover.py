"""Set Cover reduction for finite ASMP-9 access design v0.78."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Iterable, Sequence


@dataclass(frozen=True)
class AccessInstance:
    universe: tuple[Hashable, ...]
    cover_sets: tuple[frozenset[Hashable], ...]
    parameter_names: tuple[str, ...]
    target_labels: tuple[int, ...]
    queries: tuple[tuple[Hashable, ...], ...]
    anchor_query_index: int = 0


def normalize_cover(
    universe: Iterable[Hashable],
    cover_sets: Sequence[Iterable[Hashable]],
) -> tuple[tuple[Hashable, ...], tuple[frozenset[Hashable], ...]]:
    ordered_universe = tuple(universe)
    if not ordered_universe or len(set(ordered_universe)) != len(ordered_universe):
        raise ValueError("universe must be nonempty with unique elements")
    universe_set = set(ordered_universe)
    normalized = tuple(frozenset(item) for item in cover_sets)
    if any(not item <= universe_set for item in normalized):
        raise ValueError("cover set contains element outside universe")
    return ordered_universe, normalized


def build_access_instance(
    universe: Iterable[Hashable],
    cover_sets: Sequence[Iterable[Hashable]],
) -> AccessInstance:
    """Construct an access instance with optimum ``1 + cover optimum``."""

    ordered_universe, normalized = normalize_cover(universe, cover_sets)
    names = []
    for element in ordered_universe:
        names.extend((f"a[{element!r}]", f"b[{element!r}]"))
    names.extend(("anchor_c", "anchor_d"))
    parameter_names = tuple(names)
    target_labels = tuple(range(len(parameter_names)))

    anchor = []
    for index, _element in enumerate(ordered_universe):
        anchor.extend((("pair", index), ("pair", index)))
    anchor.extend((("special", "c"), ("special", "d")))
    queries: list[tuple[Hashable, ...]] = [tuple(anchor)]

    for cover_set in normalized:
        labels = []
        for element in ordered_universe:
            labels.extend((0, 1 if element in cover_set else 0))
        labels.extend((0, 0))
        queries.append(tuple(labels))

    return AccessInstance(
        universe=ordered_universe,
        cover_sets=normalized,
        parameter_names=parameter_names,
        target_labels=target_labels,
        queries=tuple(queries),
    )


def query_family_separates(
    target_labels: Sequence[Hashable],
    queries: Sequence[Sequence[Hashable]],
    indices: Sequence[int],
) -> bool:
    if not target_labels:
        raise ValueError("target registry must be nonempty")
    signatures = [
        tuple(queries[index][parameter] for index in indices)
        for parameter in range(len(target_labels))
    ]
    for left, right in combinations(range(len(target_labels)), 2):
        if target_labels[left] != target_labels[right] and signatures[left] == signatures[right]:
            return False
    return True


def minimum_set_cover(
    universe: Iterable[Hashable],
    cover_sets: Sequence[Iterable[Hashable]],
) -> tuple[int, ...] | None:
    ordered_universe, normalized = normalize_cover(universe, cover_sets)
    target = set(ordered_universe)
    for count in range(len(normalized) + 1):
        for indices in combinations(range(len(normalized)), count):
            covered = set().union(*(normalized[index] for index in indices))
            if covered == target:
                return indices
    return None


def minimum_access_family(instance: AccessInstance) -> tuple[int, ...] | None:
    for count in range(len(instance.queries) + 1):
        for indices in combinations(range(len(instance.queries)), count):
            if query_family_separates(
                instance.target_labels,
                instance.queries,
                indices,
            ):
                return indices
    return None
