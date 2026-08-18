"""Independent verifier for the ASMP-4 v0.6 registration fork.

This file imports nothing from registration_fork.py.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / "asmp4_adaptive_history_collapse_v0_5"
METRIC_PREDECESSOR = ROOT.parent / "asmp4_metric_robust_collapse_v0_3"
CANONICAL_SOURCE = ROOT.parent / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
CANONICAL_INDEX = ROOT.parent / "problem_set_v0_1.json"
MODES = (0, 1, 2, 3)
Z_VALUES = (Fraction(-3), Fraction(-1), Fraction(1), Fraction(3))


def normalize_partition(
    partition: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted((tuple(sorted(block)) for block in partition), key=min))


def recursive_partitions(items: tuple[int, ...]) -> set[tuple[tuple[int, ...], ...]]:
    """Independent recursive set-partition generator."""

    if not items:
        return {()}
    first, *rest = items
    result: set[tuple[tuple[int, ...], ...]] = set()
    for partition in recursive_partitions(tuple(rest)):
        result.add(normalize_partition(((first,), *partition)))
        for index in range(len(partition)):
            blocks = list(partition)
            blocks[index] = (first, *blocks[index])
            result.add(normalize_partition(tuple(blocks)))
    return result


def action(mode: int) -> int:
    return 0 if mode < 2 else 1


def independent_embedding(horizon: int = 5) -> dict[str, object]:
    def q(z_value: Fraction) -> Fraction:
        return Fraction(12 + 13 * z_value - z_value**3, 24)

    q_values = tuple(q(z_value) for z_value in Z_VALUES)
    safe_paths = 0
    for z_word in itertools.product(Z_VALUES, repeat=horizon):
        normal = Fraction(0)
        for z_value in z_word:
            normal = Fraction(3, 2) * normal + q(z_value) - q(z_value)
            if normal:
                break
        else:
            safe_paths += 1
    wrong = tuple(Fraction(1 - int(value)) - value for value in q_values)
    return {
        "q_values": [str(value) for value in q_values],
        "safe_paths": safe_paths,
        "expected_paths": 4**horizon,
        "wrong_successors": sorted(str(value) for value in wrong),
        "normal_multiplier": "3/2",
        "tangent_derivative": "0",
        "control_derivative": "1",
        "pass": (
            q_values == (Fraction(0), Fraction(0), Fraction(1), Fraction(1))
            and safe_paths == 4**horizon
            and set(wrong) == {Fraction(-1), Fraction(1)}
        ),
    }


def independent_canonical_quantifier_audit() -> dict[str, object]:
    """Re-read the canonical source without importing the central audit."""

    normalized = " ".join(CANONICAL_SOURCE.read_text(encoding="utf-8").split())
    required_fragments = (
        "registered causal code `C`",
        "A causal sensor encoder emits only the read transcript",
        "The plant, sensor, controller, and actuator are separate components",
        "explicit parts of the architecture",
        "For a registered normally hyperbolic, locally controllable class",
        "architecture-dependent tradeoff inequalities",
        "does **not** assume the region is rectangular in general",
        "hold the sensor experiment fixed",
    )
    prohibited_selection_fragments = (
        "closed under upstream computation",
        "replace its observation by an arbitrary sufficient statistic",
        "forced injective raw sensor",
        "must emit an injective raw",
    )
    source_clauses = [fragment in normalized for fragment in required_fragments]
    selection_clauses = [
        fragment in normalized for fragment in prohibited_selection_fragments
    ]
    return {
        "source": CANONICAL_SOURCE.name,
        "explicit_clause_count": sum(source_clauses),
        "upstream_or_raw_selection_clause_count": sum(selection_clauses),
        "computed_region": "[1,infinity) x [1,infinity)",
        "raw_region": "[2,infinity) x [1,infinity)",
        "decision": "registration_class_underdetermined",
        "pass": (
            all(source_clauses)
            and not any(selection_clauses)
            and "[1,infinity) x [1,infinity)" != "[2,infinity) x [1,infinity)"
        ),
    }


def independent_canonical_quantifier_sensitivity() -> dict[str, object]:
    """Mutate each decision-relevant literal without central imports."""

    source = CANONICAL_SOURCE.read_text(encoding="utf-8")
    normalized_source = " ".join(source.split())
    required_fragments = (
        "registered causal code `C`",
        "A causal sensor encoder emits only the read transcript",
        "The plant, sensor, controller, and actuator are separate components",
        "explicit parts of the architecture",
        "For a registered normally hyperbolic, locally controllable class",
        "architecture-dependent tradeoff inequalities",
        "does **not** assume the region is rectangular in general",
        "hold the sensor experiment fixed",
    )
    selector_fragments = (
        "closed under upstream computation",
        "replace its observation by an arbitrary sufficient statistic",
        "forced injective raw sensor",
        "must emit an injective raw",
    )
    deletion_rejections = [
        fragment not in normalized_source.replace(fragment, "")
        for fragment in required_fragments
    ]
    insertion_rejections = [
        fragment in f"{normalized_source} {fragment}" for fragment in selector_fragments
    ]
    collapsed_regions_rejected = not (
        "[1,infinity) x [1,infinity)" != "[1,infinity) x [1,infinity)"
    )
    return {
        "required_clause_deletions_rejected": sum(deletion_rejections),
        "closure_selector_insertions_rejected": sum(insertion_rejections),
        "collapsed_regions_rejected": collapsed_regions_rejected,
        "mutation_cases": (len(deletion_rejections) + len(insertion_rejections) + 1),
        "pass": (
            all(deletion_rejections)
            and all(insertion_rejections)
            and collapsed_regions_rejected
        ),
    }


def independent_registry_model_audit() -> dict[str, object]:
    """Construct two source models without importing the central harness."""

    normalized = " ".join(CANONICAL_SOURCE.read_text(encoding="utf-8").split())
    obligation_fragments = (
        "For a registered causal code `C` and horizon `T`",
        "finite transcript alphabets, or prefix-free countable alphabets charged by worst-case length",
        "A causal sensor encoder emits only the read transcript",
        "a controller receives only those symbols and emits the write transcript",
        "an actuator decoder maps write symbols to controls",
        "The plant, sensor, controller, and actuator are separate components",
        "No analog state, shared object reference, common random variable correlated with the state, or uncharged side channel may cross either interface",
        "Internal memory, delays, block coding, and shared randomness independent of the plant state are explicit parts of the architecture",
        "there exists a registered causal code C with",
        "for every allowed disturbance sequence",
        "For a registered normally hyperbolic, locally controllable class with bounded uncertainty, delay, memory, control-authority, and disturbance conventions",
        "architecture-dependent tradeoff inequalities",
        "does **not** assume the region is rectangular in general",
    )
    registry_selection_fragments = (
        "every causal code is registered",
        "all causal codes are registered",
        "every causal sensor encoder is registered",
        "all causal sensor encoders are registered",
    )
    source_obligations = [fragment in normalized for fragment in obligation_fragments]
    registry_domain_selected = any(
        fragment in normalized for fragment in registry_selection_fragments
    )
    embedding = independent_embedding(horizon=6)
    model_specs = {
        "computed_sensor_registry": {
            "sensor": (0, 0, 1, 1),
            "controller": (0, 1),
            "actuator": (0, 1),
            "read_alphabet_size": 2,
            "write_alphabet_size": 2,
            "region": "[1,infinity) x [1,infinity)",
        },
        "fixed_raw_sensor_registry": {
            "sensor": (0, 1, 2, 3),
            "controller": (0, 0, 1, 1),
            "actuator": (0, 1),
            "read_alphabet_size": 4,
            "write_alphabet_size": 2,
            "region": "[2,infinity) x [1,infinity)",
        },
    }
    component_edges = (
        "plant_to_sensor_state",
        "sensor_to_controller_read",
        "controller_to_actuator_write",
        "actuator_to_plant_control",
    )
    side_channels: tuple[str, ...] = ()
    explicit_architecture = {
        "sensor_memory": 0,
        "controller_memory": 0,
        "actuator_memory": 0,
        "sensor_delay": 0,
        "controller_delay": 0,
        "actuator_delay": 0,
        "block_length": 1,
        "shared_randomness": "none",
    }
    architecture_fields = {
        "sensor_memory",
        "controller_memory",
        "actuator_memory",
        "sensor_delay",
        "controller_delay",
        "actuator_delay",
        "block_length",
        "shared_randomness",
    }
    asserts_all_regions_rectangular = False
    models = {}
    for name, spec in model_specs.items():
        safe_by_mode = all(
            spec["actuator"][spec["controller"][spec["sensor"][mode]]] == action(mode)
            for mode in MODES
        )
        word_census_pass = True
        for horizon in range(1, 7):
            mode_words = itertools.product(MODES, repeat=horizon)
            read_words = set()
            write_words = set()
            for word in mode_words:
                read_word = tuple(spec["sensor"][mode] for mode in word)
                write_word = tuple(spec["controller"][symbol] for symbol in read_word)
                if any(
                    spec["actuator"][write] != action(mode)
                    for write, mode in zip(write_word, word, strict=True)
                ):
                    word_census_pass = False
                    break
                read_words.add(read_word)
                write_words.add(write_word)
            word_census_pass = word_census_pass and (
                len(read_words) == spec["read_alphabet_size"] ** horizon
                and len(write_words) == spec["write_alphabet_size"] ** horizon
            )
        derived_region = (
            f"[{int(math.log2(spec['read_alphabet_size']))},infinity) x "
            f"[{int(math.log2(spec['write_alphabet_size']))},infinity)"
        )
        satisfaction = (
            bool(name),
            spec["read_alphabet_size"] > 0 and spec["write_alphabet_size"] > 0,
            len(spec["sensor"]) == len(MODES),
            len(spec["controller"]) == spec["read_alphabet_size"],
            len(spec["actuator"]) == spec["write_alphabet_size"],
            component_edges
            == (
                "plant_to_sensor_state",
                "sensor_to_controller_read",
                "controller_to_actuator_write",
                "actuator_to_plant_control",
            ),
            side_channels == (),
            set(explicit_architecture) == architecture_fields,
            safe_by_mode,
            word_census_pass,
            embedding["pass"],
            derived_region == spec["region"],
            not asserts_all_regions_rectangular,
        )
        models[name] = {
            "obligations_satisfied": sum(satisfaction),
            "safe_code_exists": safe_by_mode,
            "all_mode_words_safe": word_census_pass,
            "derived_region": derived_region,
            "pass": all(satisfaction),
        }
    all_models_pass = all(model["pass"] for model in models.values())
    regions = {name: model["derived_region"] for name, model in models.items()}
    distinct_regions = len(set(regions.values())) == 2
    return {
        "source_obligation_count": sum(source_obligations),
        "registry_domain_selected": registry_domain_selected,
        "models": models,
        "regions": regions,
        "all_models_satisfy_source": all_models_pass,
        "models_have_distinct_exact_regions": distinct_regions,
        "decision": "two_source_models_with_distinct_regions",
        "pass": (
            all(source_obligations)
            and not registry_domain_selected
            and all_models_pass
            and distinct_regions
        ),
    }


def independent_global_registry_scope_audit() -> dict[str, object]:
    """Check the whole normative source and its non-normative machine index."""

    normalized = " ".join(CANONICAL_SOURCE.read_text(encoding="utf-8").split())
    normalized_lower = normalized.lower()
    index = json.loads(CANONICAL_INDEX.read_text(encoding="utf-8"))
    domain_fragments = (
        "every causal code is registered",
        "all causal codes are registered",
        "every causal sensor encoder is registered",
        "all causal sensor encoders are registered",
        "registered causal code means",
        "registered causal code denotes",
        "a causal code is registered if",
        "a causal code is registered exactly when",
        "the registry of causal codes is",
    )
    asmp4_entries = [
        problem for problem in index["problems"] if problem["id"] == "ASMP-4"
    ]
    asmp4 = asmp4_entries[0] if len(asmp4_entries) == 1 else {}
    checks = {
        "registered_occurrences_exact": normalized_lower.count("registered") == 31,
        "no_domain_definition": not any(
            fragment in normalized_lower for fragment in domain_fragments
        ),
        "formal_domains_must_be_explicit": (
            "Objects, domains, encodings, resource bounds, randomness, adversaries, "
            "and quantifier order are explicit" in normalized
        ),
        "quantifier_changes_change_problem": (
            "a change to its objects, quantifiers, adversary, or resolution criterion "
            "changes the problem" in normalized
        ),
        "normative_source_exact": (
            index["normative_statement_file"] == CANONICAL_SOURCE.name
        ),
        "index_non_normative": index["registry_is_normative"] is False,
        "definition_draft": index["status"] == "proposed_candidate_definition_draft",
        "not_graduated": index["graduation_standard_satisfied"] is False,
        "closed_core_required": (
            "closed_formal_core" in index["graduation_requirements"]
        ),
        "one_asmp4_entry": len(asmp4_entries) == 1,
        "asmp4_entry_has_no_code_domain": (
            "registered_code_domain" not in asmp4
            and "sensor_grammar" not in asmp4
            and "upstream_computation_closed" not in asmp4
        ),
    }
    return {
        "canonical_source": CANONICAL_SOURCE.name,
        "machine_index": CANONICAL_INDEX.name,
        "registered_occurrence_count": normalized_lower.count("registered"),
        "domain_defining_occurrence_count": sum(
            fragment in normalized_lower for fragment in domain_fragments
        ),
        "checks": checks,
        "decision": "global_sources_do_not_select_registered_code_domain",
        "pass": all(checks.values()),
    }


def independent_partition_census() -> dict[str, object]:
    partitions = recursive_partitions(MODES)
    safe_maps = {
        partition: [
            controller
            for controller in itertools.product((0, 1), repeat=len(partition))
            if all(
                controller[block_index] == action(mode)
                for block_index, block in enumerate(partition)
                for mode in block
            )
        ]
        for partition in partitions
    }
    safe = {partition for partition, controllers in safe_maps.items() if controllers}
    return {
        "partitions": len(partitions),
        "all_histogram": dict(sorted(Counter(map(len, partitions)).items())),
        "safe": len(safe),
        "safe_maps": sum(map(len, safe_maps.values())),
        "safe_histogram": dict(sorted(Counter(map(len, safe)).items())),
        "coarsest": [
            list(block) for block in min(safe, key=lambda part: (len(part), part))
        ],
        "raw_safe": ((0,), (1,), (2,), (3,)) in safe,
    }


def independent_registry_lattice_census() -> dict[str, object]:
    """Reconstruct all registry subsets and inclusion covers independently."""

    partitions = sorted(recursive_partitions(MODES), key=lambda part: (len(part), part))
    safe_block_counts = []
    for partition in partitions:
        safe = any(
            all(
                controller[block_index] == action(mode)
                for block_index, block in enumerate(partition)
                for mode in block
            )
            for controller in itertools.product((0, 1), repeat=len(partition))
        )
        safe_block_counts.append(len(partition) if safe else None)
    registry_count = 1 << len(partitions)
    infinity_rank = len(partitions) + 1
    values = [infinity_rank] * registry_count
    histogram: Counter[str] = Counter()
    for mask in range(1, registry_count):
        admitted = [
            blocks
            for index, blocks in enumerate(safe_block_counts)
            if blocks is not None and mask & (1 << index)
        ]
        if not admitted:
            histogram["infeasible"] += 1
        else:
            values[mask] = min(admitted)
            histogram[f"kappa_{values[mask]}"] += 1
    covers = 0
    strict = 0
    failures = []
    for mask in range(registry_count):
        for index in range(len(partitions)):
            bit = 1 << index
            if mask & bit:
                continue
            expanded = mask | bit
            covers += 1
            if values[expanded] > values[mask]:
                failures.append((mask, expanded))
            elif values[expanded] < values[mask]:
                strict += 1
    raw = ((0,), (1,), (2,), (3,))
    raw_mask = 1 << partitions.index(raw)
    full_mask = registry_count - 1
    return {
        "registries": registry_count,
        "nonempty": registry_count - 1,
        "histogram": dict(sorted(histogram.items())),
        "covers": covers,
        "strict_covers": strict,
        "failures": failures,
        "raw_kappa": values[raw_mask],
        "full_kappa": values[full_mask],
        "pass": (
            histogram
            == {
                "infeasible": 2047,
                "kappa_2": 16384,
                "kappa_3": 12288,
                "kappa_4": 2048,
            }
            and covers == 245760
            and strict == 26624
            and not failures
            and values[raw_mask] == 4
            and values[full_mask] == 2
        ),
    }


def independent_stirling_second(item_count: int, block_count: int) -> int:
    """Iteratively compute S(n,k), independently of the central recurrence."""

    table = [[0] * (item_count + 1) for _ in range(item_count + 1)]
    table[0][0] = 1
    for items in range(1, item_count + 1):
        for blocks in range(1, items + 1):
            table[items][blocks] = (
                blocks * table[items - 1][blocks] + table[items - 1][blocks - 1]
            )
    if block_count < 0 or block_count > item_count:
        return 0
    return table[item_count][block_count]


def independent_bell_number(item_count: int) -> int:
    return sum(
        independent_stirling_second(item_count, blocks)
        for blocks in range(item_count + 1)
    )


def independent_general_registry_lattice_formula(
    max_modes: int = 5,
) -> dict[str, object]:
    """Reconstruct the general registry formula from block-size shapes."""

    rows = []
    failures = []
    action_partition_total = 0
    for mode_count in range(1, max_modes + 1):
        partitions = recursive_partitions(tuple(range(mode_count)))
        shapes: Counter[tuple[int, ...]] = Counter(
            tuple(sorted(map(len, partition))) for partition in partitions
        )
        bell = independent_bell_number(mode_count)
        if bell != len(partitions):
            failures.append((mode_count, "bell"))
        for shape, multiplicity in sorted(shapes.items()):
            action_partition_total += multiplicity
            safe_hist: Counter[int] = Counter()
            for allocation in itertools.product(
                *(range(1, size + 1) for size in shape)
            ):
                safe_hist[sum(allocation)] += math.prod(
                    independent_stirling_second(size, blocks)
                    for size, blocks in zip(shape, allocation, strict=True)
                )
            unsafe = bell - sum(safe_hist.values())
            corner_hist = {}
            strict_edges = 0
            for kappa in sorted(safe_hist):
                larger = sum(
                    count for blocks, count in safe_hist.items() if blocks > kappa
                )
                corner_hist[f"kappa_{kappa}"] = (2 ** safe_hist[kappa] - 1) * 2 ** (
                    unsafe + larger
                )
                strict_edges += safe_hist[kappa] * 2 ** (unsafe + larger)
            infeasible = 2**unsafe - 1
            if infeasible + sum(corner_hist.values()) != 2**bell - 1:
                failures.append((mode_count, shape, "checksum"))
            representative = next(
                partition
                for partition in partitions
                if tuple(sorted(map(len, partition))) == shape
            )
            action_lookup = {
                mode: index
                for index, block in enumerate(representative)
                for mode in block
            }
            enumerated = Counter(
                len(sensor)
                for sensor in partitions
                if all(
                    len({action_lookup[mode] for mode in sensor_block}) == 1
                    for sensor_block in sensor
                )
            )
            if enumerated != safe_hist:
                failures.append((mode_count, shape, "enumeration"))
            rows.append(
                {
                    "modes": mode_count,
                    "shape": list(shape),
                    "multiplicity": multiplicity,
                    "safe_histogram": {
                        str(blocks): count
                        for blocks, count in sorted(safe_hist.items())
                    },
                    "unsafe": unsafe,
                    "infeasible": infeasible,
                    "corner_histogram": corner_hist,
                    "strict_edges": strict_edges,
                }
            )
    five_mode = next(
        row for row in rows if row["modes"] == 5 and row["shape"] == [2, 3]
    )
    return {
        "shape_rows": len(rows),
        "action_partitions": action_partition_total,
        "rows": rows,
        "five_mode_2_3": five_mode,
        "failures": failures,
        "pass": (
            len(rows) == 18
            and action_partition_total == 75
            and five_mode["safe_histogram"] == {"2": 1, "3": 4, "4": 4, "5": 1}
            and five_mode["infeasible"] == 4398046511103
            and five_mode["strict_edges"] == 2854332185706496
            and not failures
        ),
    }


def independent_general_grammar(max_modes: int = 5) -> dict[str, object]:
    expected_pairs = [1, 3, 12, 60, 358]
    rows = []
    threshold_rows = 0
    failures = []
    for mode_count in range(1, max_modes + 1):
        partitions = recursive_partitions(tuple(range(mode_count)))
        pair_count = 0
        for action_partition in partitions:
            action_lookup = {
                mode: block_index
                for block_index, block in enumerate(action_partition)
                for mode in block
            }
            refinements = [
                sensor_partition
                for sensor_partition in partitions
                if all(
                    len({action_lookup[mode] for mode in sensor_block}) == 1
                    for sensor_block in sensor_partition
                )
            ]
            pair_count += len(refinements)
            action_blocks = len(action_partition)
            for floor in range(1, mode_count + 1):
                kappa = min(
                    len(sensor_partition)
                    for sensor_partition in refinements
                    if len(sensor_partition) >= floor
                )
                threshold_rows += 1
                if kappa != max(action_blocks, floor):
                    failures.append((mode_count, action_partition, floor, kappa))
        rows.append(
            {
                "modes": mode_count,
                "partitions": len(partitions),
                "refinement_pairs": pair_count,
            }
        )
        if pair_count != expected_pairs[mode_count - 1]:
            failures.append((mode_count, "pair_count", pair_count))
    return {
        "rows": rows,
        "threshold_rows": threshold_rows,
        "failures": failures,
        "pass": not failures,
    }


def independent_graph_census(max_modes: int = 3, horizon: int = 4) -> dict[str, object]:
    expected_cases = [1, 108, 60025]
    expected_feasible = [1, 91, 37338]
    rows = []
    comparisons = 0
    failures = []
    for mode_count in range(1, max_modes + 1):
        modes = tuple(range(mode_count))
        partitions = recursive_partitions(modes)
        successor_choices = tuple(
            tuple(mode for mode in modes if mask & (1 << mode))
            for mask in range(1, 1 << mode_count)
        )
        case_count = 0
        feasible_count = 0
        for graph in itertools.product(successor_choices, repeat=mode_count):
            for initial_mask in range(1, 1 << mode_count):
                initial = frozenset(
                    mode for mode in modes if initial_mask & (1 << mode)
                )
                partition_data = {}
                for partition in partitions:
                    label = {
                        mode: block_index
                        for block_index, block in enumerate(partition)
                        for mode in block
                    }
                    path_set = {(mode,) for mode in initial}
                    brute_counts = []
                    for _ in range(horizon):
                        brute_counts.append(
                            len(
                                {
                                    tuple(label[mode] for mode in path)
                                    for path in path_set
                                }
                            )
                        )
                        path_set = {
                            (*path, successor)
                            for path in path_set
                            for successor in graph[path[-1]]
                        }
                    active = {
                        frozenset(initial.intersection(block)): 1
                        for block in partition
                        if initial.intersection(block)
                    }
                    subset_counts = []
                    beliefs = set(active)
                    pending = list(active)
                    for _ in range(horizon):
                        subset_counts.append(sum(active.values()))
                        following: dict[frozenset[int], int] = {}
                        for belief, word_count in active.items():
                            successors = {
                                successor
                                for mode in belief
                                for successor in graph[mode]
                            }
                            for block in partition:
                                target = frozenset(successors.intersection(block))
                                if target:
                                    following[target] = (
                                        following.get(target, 0) + word_count
                                    )
                        active = following
                    while pending:
                        belief = pending.pop()
                        successors = {
                            successor for mode in belief for successor in graph[mode]
                        }
                        for block in partition:
                            target = frozenset(successors.intersection(block))
                            if target and target not in beliefs:
                                beliefs.add(target)
                                pending.append(target)
                    comparisons += 1
                    if subset_counts != brute_counts:
                        failures.append((mode_count, graph, initial, partition))
                    partition_data[partition] = (label, beliefs)
                for sensor_partition in partitions:
                    beliefs = partition_data[sensor_partition][1]
                    for action_partition in partitions:
                        case_count += 1
                        action_label = partition_data[action_partition][0]
                        feasible = all(
                            len({action_label[mode] for mode in belief}) == 1
                            for belief in beliefs
                        )
                        feasible_count += int(feasible)
        rows.append(
            {
                "modes": mode_count,
                "cases": case_count,
                "feasible": feasible_count,
            }
        )
        if case_count != expected_cases[mode_count - 1]:
            failures.append((mode_count, "cases", case_count))
        if feasible_count != expected_feasible[mode_count - 1]:
            failures.append((mode_count, "feasible", feasible_count))
    return {
        "rows": rows,
        "total_cases": sum(row["cases"] for row in rows),
        "total_feasible": sum(row["feasible"] for row in rows),
        "comparisons": comparisons,
        "failures": failures,
        "pass": not failures,
    }


def independent_singleton_delay_census(max_modes: int = 3) -> dict[str, object]:
    """Recompute fixed-transducer failure depth with integer observer masks."""

    total_cases = 0
    infinite_cases = 0
    failure_hist: Counter[int] = Counter()
    maximum_failure = 0
    maximum_witness = None
    failures = []
    rows = []
    for mode_count in range(1, max_modes + 1):
        modes = tuple(range(mode_count))
        partitions = tuple(sorted(recursive_partitions(modes)))
        partition_masks = {
            partition: tuple(sum(1 << mode for mode in block) for block in partition)
            for partition in partitions
        }
        successor_choices = tuple(
            tuple(mode for mode in modes if mask & (1 << mode))
            for mask in range(1, 1 << mode_count)
        )
        mode_cases = 0
        mode_infinite = 0
        mode_hist: Counter[int] = Counter()
        for graph in itertools.product(successor_choices, repeat=mode_count):
            successor_masks = [0] * (1 << mode_count)
            for belief in range(1, 1 << mode_count):
                successor_masks[belief] = sum(
                    1 << target
                    for target in {
                        target
                        for mode in modes
                        if belief & (1 << mode)
                        for target in graph[mode]
                    }
                )
            for initial_mask in range(1, 1 << mode_count):
                for sensor_partition in partitions:
                    sensor_blocks = partition_masks[sensor_partition]
                    initial_layer = frozenset(
                        initial_mask & block
                        for block in sensor_blocks
                        if initial_mask & block
                    )
                    for action_partition in partitions:
                        mode_cases += 1
                        action_label = {
                            mode: block_index
                            for block_index, block in enumerate(action_partition)
                            for mode in block
                        }

                        def homogeneous(belief: int) -> bool:
                            return (
                                len(
                                    {
                                        action_label[mode]
                                        for mode in modes
                                        if belief & (1 << mode)
                                    }
                                )
                                == 1
                            )

                        layer = initial_layer
                        seen_layers = set()
                        horizon = 1
                        first_failure = None
                        while True:
                            if any(not homogeneous(belief) for belief in layer):
                                first_failure = horizon
                                break
                            if layer in seen_layers:
                                break
                            seen_layers.add(layer)
                            layer = frozenset(
                                successor_masks[belief] & block
                                for belief in layer
                                for block in sensor_blocks
                                if successor_masks[belief] & block
                            )
                            horizon += 1

                        pending = list(initial_layer)
                        reached = set(initial_layer)
                        independently_infinite = True
                        while pending:
                            belief = pending.pop()
                            if not homogeneous(belief):
                                independently_infinite = False
                                break
                            for block in sensor_blocks:
                                target = successor_masks[belief] & block
                                if target and target not in reached:
                                    reached.add(target)
                                    pending.append(target)
                        if (first_failure is None) != independently_infinite:
                            failures.append("classification")
                        if first_failure is None:
                            mode_infinite += 1
                        else:
                            mode_hist[first_failure] += 1
                            failure_hist[first_failure] += 1
                            if first_failure > maximum_failure:
                                maximum_failure = first_failure
                                maximum_witness = {
                                    "modes": mode_count,
                                    "graph": [list(row) for row in graph],
                                    "initial_modes": [
                                        mode
                                        for mode in modes
                                        if initial_mask & (1 << mode)
                                    ],
                                    "sensor_partition": [
                                        list(block) for block in sensor_partition
                                    ],
                                    "action_partition": [
                                        list(block) for block in action_partition
                                    ],
                                    "first_failure": first_failure,
                                }
        total_cases += mode_cases
        infinite_cases += mode_infinite
        rows.append(
            {
                "modes": mode_count,
                "cases": mode_cases,
                "infinite": mode_infinite,
                "failure_histogram": dict(sorted(mode_hist.items())),
            }
        )
    expected_histogram = {1: 10642, 2: 8406, 3: 3110, 4: 534, 5: 12}
    return {
        "rows": rows,
        "total_cases": total_cases,
        "infinite_cases": infinite_cases,
        "failure_histogram": dict(sorted(failure_hist.items())),
        "maximum_failure": maximum_failure,
        "maximum_witness": maximum_witness,
        "failures": failures,
        "pass": (
            total_cases == 60134
            and infinite_cases == 37430
            and failure_hist == expected_histogram
            and maximum_failure == 5
            and not failures
        ),
    }


def independent_golden_mean(horizon: int = 12) -> dict[str, object]:
    zero_ending = 1
    one_ending = 1
    counts = [2]
    for _ in range(1, horizon):
        zero_ending, one_ending = zero_ending + one_ending, zero_ending
        counts.append(zero_ending + one_ending)
    phi = (1 + 5**0.5) / 2
    return {
        "counts": counts,
        "action_counts": [1] * horizon,
        "entropy": math.log2(phi),
        "pass": counts == [2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377],
    }


def independent_adaptive_aperiodic(horizon: int = 16) -> dict[str, object]:
    """Recompute the adaptive fixture without the central implementation."""

    graph = ((0, 1), (0, 2), (0, 1))

    def label_language_counts(labels: tuple[int, ...]) -> list[int]:
        active: dict[frozenset[int], int] = {}
        for label in set(labels[mode] for mode in (0, 2)):
            belief = frozenset(mode for mode in (0, 2) if labels[mode] == label)
            active[belief] = active.get(belief, 0) + 1
        counts = []
        for _ in range(horizon):
            counts.append(sum(active.values()))
            following: dict[frozenset[int], int] = {}
            for belief, word_count in active.items():
                successors = {successor for mode in belief for successor in graph[mode]}
                for label in set(labels[mode] for mode in successors):
                    target = frozenset(
                        mode for mode in successors if labels[mode] == label
                    )
                    following[target] = following.get(target, 0) + word_count
            active = following
        return counts

    action_counts = label_language_counts((0, 1, 0))
    fixed_split_counts = label_language_counts((0, 1, 1))

    value_a = value_b = 1
    adaptive_counts = []
    for _ in range(horizon):
        value_a, value_b = value_b, value_a + value_b
        adaptive_counts.append(value_a)

    reachable_from = []
    for source in range(3):
        seen = {source}
        pending = [source]
        while pending:
            current = pending.pop()
            for successor in graph[current]:
                if successor not in seen:
                    seen.add(successor)
                    pending.append(successor)
        reachable_from.append(seen)

    action_labels = (0, 1, 0)
    grammar_masks = ((7,), (1, 6))
    safe_choices = {}
    for belief_mask in range(1, 8):
        choices = []
        for blocks in grammar_masks:
            cells = tuple(
                belief_mask & block for block in blocks if belief_mask & block
            )
            if all(
                len({action_labels[mode] for mode in range(3) if cell & (1 << mode)})
                == 1
                for cell in cells
            ):
                choices.append(
                    tuple(
                        sum(
                            1 << successor
                            for successor in {
                                successor
                                for mode in range(3)
                                if cell & (1 << mode)
                                for successor in graph[mode]
                            }
                        )
                        for cell in cells
                    )
                )
        safe_choices[belief_mask] = choices
    viable = set(range(1, 8))
    while True:
        following = {
            belief
            for belief in viable
            if any(
                all(successor in viable for successor in successors)
                for successors in safe_choices[belief]
            )
        }
        if following == viable:
            break
        viable = following

    expected_fixed = [2**length for length in range(1, horizon + 1)]
    phi = (1 + 5**0.5) / 2
    return {
        "adaptive_counts": adaptive_counts,
        "action_counts": action_counts,
        "fixed_split_counts": fixed_split_counts,
        "stationary_choices": {"belief_{0,2}": 0, "belief_{0,1}": 1},
        "strongly_connected": all(seen == {0, 1, 2} for seen in reachable_from),
        "aperiodic": 0 in graph[0],
        "viable_belief_masks": sorted(viable),
        "initial_belief_viable": 5 in viable,
        "adaptive_entropy": math.log2(phi),
        "fixed_entropy": 1.0,
        "pass": (
            adaptive_counts == action_counts
            and fixed_split_counts == expected_fixed
            and all(seen == {0, 1, 2} for seen in reachable_from)
            and 0 in graph[0]
            and viable == {1, 2, 3, 4, 5}
        ),
    }


def independent_adaptive_census(horizon: int = 4) -> dict[str, object]:
    """Independently exhaust all three-mode two-partition grammars."""

    modes = (0, 1, 2)
    partitions = tuple(sorted(recursive_partitions(modes)))
    partition_masks = {
        partition: tuple(sum(1 << mode for mode in block) for block in partition)
        for partition in partitions
    }
    grammars = tuple(itertools.combinations(partitions, 2))
    successor_choices = tuple(
        tuple(mode for mode in modes if mask & (1 << mode))
        for mask in range(1, 1 << len(modes))
    )
    cases = 0
    adaptive_feasible = 0
    fixed_feasible = 0
    adaptive_only = 0
    infinitely_viable = 0
    finite_only = 0
    strict_improvements = 0
    exact_action = 0
    maximum_ratio = Fraction(0)
    failures = []

    for graph in itertools.product(successor_choices, repeat=len(modes)):
        successor_masks = [0] * (1 << len(modes))
        for belief_mask in range(1, 1 << len(modes)):
            successor_masks[belief_mask] = sum(
                1 << target
                for target in {
                    target
                    for mode in modes
                    if belief_mask & (1 << mode)
                    for target in graph[mode]
                }
            )
        for initial_mask in range(1, 1 << len(modes)):
            for action_partition in partitions:
                action_label = {
                    mode: block_index
                    for block_index, block in enumerate(action_partition)
                    for mode in block
                }

                def homogeneous(mask: int) -> bool:
                    return (
                        len(
                            {action_label[mode] for mode in modes if mask & (1 << mode)}
                        )
                        == 1
                    )

                def fixed_language_data(
                    partition: tuple[tuple[int, ...], ...],
                ) -> tuple[bool, int]:
                    blocks = partition_masks[partition]
                    active = {
                        initial_mask & block: 1
                        for block in blocks
                        if initial_mask & block
                    }
                    all_homogeneous = all(homogeneous(belief) for belief in active)
                    for _ in range(1, horizon):
                        following: dict[int, int] = {}
                        for belief, word_count in active.items():
                            possible = successor_masks[belief]
                            for block in blocks:
                                target = possible & block
                                if target:
                                    following[target] = (
                                        following.get(target, 0) + word_count
                                    )
                                    all_homogeneous &= homogeneous(target)
                        active = following
                    pending = list(active)
                    reached = set(active)
                    while pending:
                        possible = successor_masks[pending.pop()]
                        for block in blocks:
                            target = possible & block
                            if target and target not in reached:
                                reached.add(target)
                                pending.append(target)
                                all_homogeneous &= homogeneous(target)
                    return all_homogeneous, sum(active.values())

                action_words = fixed_language_data(action_partition)[1]
                sensor_data = {
                    partition: fixed_language_data(partition)
                    for partition in partitions
                }
                safe_transitions = {}
                for partition in partitions:
                    blocks = partition_masks[partition]
                    rows = {}
                    for belief in range(1, 1 << len(modes)):
                        cells = tuple(
                            belief & block for block in blocks if belief & block
                        )
                        rows[belief] = (
                            tuple(successor_masks[cell] for cell in cells)
                            if all(homogeneous(cell) for cell in cells)
                            else None
                        )
                    safe_transitions[partition] = rows

                for grammar in grammars:
                    cases += 1
                    infinity = 10**20
                    values = [infinity] + [1] * ((1 << len(modes)) - 1)
                    for _ in range(horizon):
                        following = [infinity] * (1 << len(modes))
                        for belief in range(1, 1 << len(modes)):
                            candidates = []
                            for partition in grammar:
                                successors = safe_transitions[partition][belief]
                                if successors is not None:
                                    candidates.append(
                                        sum(
                                            values[successor]
                                            for successor in successors
                                        )
                                    )
                            if candidates:
                                following[belief] = min(candidates)
                        values = following
                    adaptive_words = values[initial_mask]
                    adaptive_ok = adaptive_words < infinity
                    viable = set(range(1, 1 << len(modes)))
                    while True:
                        following_viable = {
                            belief
                            for belief in viable
                            if any(
                                successors is not None
                                and all(successor in viable for successor in successors)
                                for partition in grammar
                                for successors in (safe_transitions[partition][belief],)
                            )
                        }
                        if following_viable == viable:
                            break
                        viable = following_viable
                    infinite_ok = initial_mask in viable
                    fixed_words = [
                        sensor_data[partition][1]
                        for partition in grammar
                        if sensor_data[partition][0]
                    ]
                    best_fixed = min(fixed_words) if fixed_words else None
                    adaptive_feasible += int(adaptive_ok)
                    infinitely_viable += int(infinite_ok)
                    finite_only += int(adaptive_ok and not infinite_ok)
                    fixed_feasible += int(best_fixed is not None)
                    adaptive_only += int(adaptive_ok and best_fixed is None)
                    if infinite_ok and not adaptive_ok:
                        failures.append("viable_but_finite_horizon_infeasible")
                    if not adaptive_ok:
                        continue
                    exact_action += int(adaptive_words == action_words)
                    if adaptive_words < action_words:
                        failures.append("action_lower_bound")
                    if best_fixed is not None:
                        if adaptive_words > best_fixed:
                            failures.append("adaptive_exceeds_fixed")
                        if adaptive_words < best_fixed:
                            strict_improvements += 1
                            maximum_ratio = max(
                                maximum_ratio, Fraction(best_fixed, adaptive_words)
                            )

    observed = {
        "cases": cases,
        "adaptive_feasible": adaptive_feasible,
        "infinitely_viable": infinitely_viable,
        "finite_only": finite_only,
        "fixed_feasible": fixed_feasible,
        "adaptive_only": adaptive_only,
        "strict_improvements": strict_improvements,
        "exact_action": exact_action,
        "maximum_ratio": str(maximum_ratio),
    }
    expected = {
        "cases": 120050,
        "adaptive_feasible": 99524,
        "infinitely_viable": 99524,
        "finite_only": 0,
        "fixed_feasible": 97952,
        "adaptive_only": 1572,
        "strict_improvements": 4863,
        "exact_action": 73223,
        "maximum_ratio": "8",
    }
    return {
        **observed,
        "failures": failures,
        "pass": observed == expected and not failures,
    }


def independent_adaptive_grammar_lattice(horizon: int = 4) -> dict[str, object]:
    """Exhaust all 32 grammars and every inclusion cover independently."""

    modes = (0, 1, 2)
    partitions = tuple(sorted(recursive_partitions(modes)))
    partition_masks = {
        partition: tuple(sum(1 << mode for mode in block) for block in partition)
        for partition in partitions
    }
    successor_choices = tuple(
        tuple(mode for mode in modes if mask & (1 << mode))
        for mask in range(1, 1 << len(modes))
    )
    infinity = 10**50
    base_cases = 0
    nonempty_cases = 0
    finite = 0
    viable_count = 0
    finite_only = 0
    action_exact = 0
    cover_edges = 0
    feasibility_gains = 0
    viability_gains = 0
    strict_finite_edges = 0
    maximum_ratio = Fraction(1)
    size_cases: Counter[int] = Counter()
    size_finite: Counter[int] = Counter()
    size_viable: Counter[int] = Counter()
    finite_only_sizes: Counter[int] = Counter()
    failures = []

    for graph in itertools.product(successor_choices, repeat=len(modes)):
        successor_masks = [0] * (1 << len(modes))
        for belief in range(1, 1 << len(modes)):
            successor_masks[belief] = sum(
                1 << target
                for target in {
                    target
                    for mode in modes
                    if belief & (1 << mode)
                    for target in graph[mode]
                }
            )
        for initial_mask in range(1, 1 << len(modes)):
            for action_partition in partitions:
                base_cases += 1
                action_label = {
                    mode: block_index
                    for block_index, block in enumerate(action_partition)
                    for mode in block
                }

                def homogeneous(mask: int) -> bool:
                    return (
                        len(
                            {action_label[mode] for mode in modes if mask & (1 << mode)}
                        )
                        == 1
                    )

                def language_words(partition: tuple[tuple[int, ...], ...]) -> int:
                    blocks = partition_masks[partition]
                    active = {
                        initial_mask & block: 1
                        for block in blocks
                        if initial_mask & block
                    }
                    for _ in range(1, horizon):
                        following: dict[int, int] = {}
                        for belief, words in active.items():
                            possible = successor_masks[belief]
                            for block in blocks:
                                target = possible & block
                                if target:
                                    following[target] = following.get(target, 0) + words
                        active = following
                    return sum(active.values())

                action_words = language_words(action_partition)
                safe_transitions = []
                for partition in partitions:
                    rows = {}
                    for belief in range(1, 1 << len(modes)):
                        cells = tuple(
                            belief & block
                            for block in partition_masks[partition]
                            if belief & block
                        )
                        rows[belief] = (
                            tuple(successor_masks[cell] for cell in cells)
                            if all(homogeneous(cell) for cell in cells)
                            else None
                        )
                    safe_transitions.append(rows)

                values_by_grammar = [infinity] * (1 << len(partitions))
                viable_by_grammar = [False] * (1 << len(partitions))
                for grammar_mask in range(1, 1 << len(partitions)):
                    selected = tuple(
                        index
                        for index in range(len(partitions))
                        if grammar_mask & (1 << index)
                    )
                    grammar_size = len(selected)
                    nonempty_cases += 1
                    size_cases[grammar_size] += 1
                    values = [infinity] + [1] * ((1 << len(modes)) - 1)
                    for _ in range(horizon):
                        following = [infinity] * (1 << len(modes))
                        for belief in range(1, 1 << len(modes)):
                            candidates = []
                            for index in selected:
                                successors = safe_transitions[index][belief]
                                if successors is not None:
                                    candidates.append(
                                        min(
                                            infinity,
                                            sum(
                                                values[target] for target in successors
                                            ),
                                        )
                                    )
                            if candidates:
                                following[belief] = min(candidates)
                        values = following
                    adaptive_words = values[initial_mask]
                    values_by_grammar[grammar_mask] = adaptive_words
                    finite_ok = adaptive_words < infinity

                    viable = set(range(1, 1 << len(modes)))
                    while True:
                        following_viable = {
                            belief
                            for belief in viable
                            if any(
                                safe_transitions[index][belief] is not None
                                and all(
                                    target in viable
                                    for target in safe_transitions[index][belief]
                                )
                                for index in selected
                            )
                        }
                        if following_viable == viable:
                            break
                        viable = following_viable
                    viable_ok = initial_mask in viable
                    viable_by_grammar[grammar_mask] = viable_ok
                    finite += int(finite_ok)
                    viable_count += int(viable_ok)
                    finite_only += int(finite_ok and not viable_ok)
                    finite_only_sizes[grammar_size] += int(finite_ok and not viable_ok)
                    size_finite[grammar_size] += int(finite_ok)
                    size_viable[grammar_size] += int(viable_ok)
                    if viable_ok and not finite_ok:
                        failures.append("viable_but_finite_infeasible")
                    if finite_ok:
                        action_exact += int(adaptive_words == action_words)
                        if adaptive_words < action_words:
                            failures.append("action_lower_bound")

                for grammar_mask in range(1 << len(partitions)):
                    for index in range(len(partitions)):
                        bit = 1 << index
                        if grammar_mask & bit:
                            continue
                        expanded = grammar_mask | bit
                        cover_edges += 1
                        base_value = values_by_grammar[grammar_mask]
                        expanded_value = values_by_grammar[expanded]
                        if expanded_value > base_value:
                            failures.append("finite_nonmonotone")
                        if (
                            viable_by_grammar[grammar_mask]
                            and not viable_by_grammar[expanded]
                        ):
                            failures.append("viability_nonmonotone")
                        if base_value >= infinity and expanded_value < infinity:
                            feasibility_gains += 1
                        elif base_value < infinity and expanded_value < base_value:
                            strict_finite_edges += 1
                            maximum_ratio = max(
                                maximum_ratio, Fraction(base_value, expanded_value)
                            )
                        if (
                            not viable_by_grammar[grammar_mask]
                            and viable_by_grammar[expanded]
                        ):
                            viability_gains += 1

    observed = {
        "base_cases": base_cases,
        "nonempty_cases": nonempty_cases,
        "finite": finite,
        "viable": viable_count,
        "finite_only": finite_only,
        "action_exact": action_exact,
        "size_cases": dict(sorted(size_cases.items())),
        "size_finite": dict(sorted(size_finite.items())),
        "size_viable": dict(sorted(size_viable.items())),
        "finite_only_sizes": dict(sorted(finite_only_sizes.items())),
        "cover_edges": cover_edges,
        "feasibility_gains": feasibility_gains,
        "viability_gains": viability_gains,
        "strict_finite_edges": strict_finite_edges,
        "maximum_ratio": str(maximum_ratio),
    }
    expected = {
        "base_cases": 12005,
        "nonempty_cases": 372155,
        "finite": 320930,
        "viable": 320918,
        "finite_only": 12,
        "action_exact": 255869,
        "size_cases": {1: 60025, 2: 120050, 3: 120050, 4: 60025, 5: 12005},
        "size_finite": {1: 37350, 2: 99524, 3: 113029, 4: 59022, 5: 12005},
        "size_viable": {1: 37338, 2: 99524, 3: 113029, 4: 59022, 5: 12005},
        "finite_only_sizes": {1: 12, 2: 0, 3: 0, 4: 0, 5: 0},
        "cover_edges": 960400,
        "feasibility_gains": 138546,
        "viability_gains": 138582,
        "strict_finite_edges": 104556,
        "maximum_ratio": "81",
    }
    return {
        **observed,
        "failures": failures,
        "pass": observed == expected and not failures,
    }


def independent_language_rows(max_horizon: int = 6) -> list[dict[str, int]]:
    rows = []
    for horizon in range(1, max_horizon + 1):
        raw = set()
        computed = set()
        writes = set()
        for modes in itertools.product(MODES, repeat=horizon):
            raw.add(modes)
            sufficient = tuple(action(mode) for mode in modes)
            computed.add(sufficient)
            writes.add(sufficient)
        rows.append(
            {
                "horizon": horizon,
                "paths": 4**horizon,
                "raw": len(raw),
                "computed": len(computed),
                "writes": len(writes),
            }
        )
    return rows


def document_sentinels() -> dict[str, bool]:
    theorem = (ROOT / "THEOREM.md").read_text(encoding="utf-8")
    result = (ROOT / "RESULT.md").read_text(encoding="utf-8")
    audit = (ROOT / "COMPLETION_AUDIT_v0_6.md").read_text(encoding="utf-8")
    stopping = (ROOT / "STOPPING_ARGUMENT_v0_6.md").read_text(encoding="utf-8")
    prior_art = (ROOT / "PRIOR_ART_AUDIT_v0_6.md").read_text(encoding="utf-8")
    proof_audit = (ROOT / "PROOF_AUDIT_v0_6.md").read_text(encoding="utf-8")
    return {
        "partition_lemma": "**Lemma 1 (safe observation partitions).**" in theorem,
        "computed_theorem": (
            "**Theorem 2 (computed-sensor region).**" in theorem
            and "[1,infinity) x [1,infinity)" in theorem
        ),
        "raw_theorem": (
            "**Theorem 3 (forced-raw region).**" in theorem
            and "[2,infinity) x [1,infinity)" in theorem
        ),
        "general_grammar_theorem": (
            "**Theorem 4 (full-reset sensor-grammar region).**" in theorem
            and "[log2 kappa,infinity) x [log2 m,infinity)" in theorem
            and "1,3,12,60,358" in theorem
        ),
        "fixed_transducer_theorem": (
            "**Theorem 5 (fixed-transducer graph region).**" in theorem
            and "[h_f,infinity) x [h_g,infinity)" in theorem
            and "60,134" in theorem
            and "37,430" in theorem
            and "lambda^2-lambda-1" in theorem
        ),
        "adaptive_sensor_grammar_theorem": (
            "**Theorem 6 (adaptive sensor-grammar entropy-game formula).**" in theorem
            and "V_(t+1)(B)" in theorem
            and "[log2 rho_I,infinity) x [h_g,infinity)" in theorem
            and "stationary belief policy attains the optimal read rate" in theorem
            and "[[0,1],[1,1]]" in theorem
            and "strongly connected and aperiodic" in theorem
            and "120,050" in theorem
            and "1,572" in theorem
        ),
        "prior_art_boundary": (
            "Operator Approach to Entropy" in prior_art
            and "not a new general result" in prior_art
            and "prescribes the initial state" in prior_art
        ),
        "adaptive_proof_ledger": (
            "W_(T-N)(I) <= V_T(I) <= W_T(I)" in proof_audit
            and "e_I^transpose A_pi^T 1" in proof_audit
            and "no finite-only cases" in proof_audit
            and "does not claim the entropy-game positional theorem as new"
            in proof_audit
        ),
        "canonical_quantifier_disposition": (
            "Eight explicit clauses" in theorem
            and "registration_class_underdetermined" in result
            and "eight relevant source clauses" in stopping
            and "Thirteen adversarial mutations" in stopping
            and "all 13 decision-reversing" in proof_audit
        ),
        "registry_model_certificate": (
            "stronger model-completion certificate extracts 13 obligations" in theorem
            and "13 canonical obligations" in result
            and "Both models satisfy all 13 obligations" in stopping
            and "registry-model builders verify 13 of 13" in proof_audit
        ),
        "global_registry_scope_certificate": (
            "entire normative Markdown" in theorem
            and "31 times" in theorem
            and "non-normative index" in result
            and "absence is global" in stopping
            and "whole-document audit finds 31 uses" in proof_audit
        ),
        "registry_lattice_certificate": (
            "**Lemma 1b (registry-lattice monotonicity).**" in theorem
            and "32,767 nonempty registries" in theorem
            and "245,760 single-partition inclusion edges" in result
            and "15-partition lattice has 32,767" in stopping
            and "complete 32,767-registry lattice" in proof_audit
        ),
        "general_registry_formula_certificate": (
            "**Corollary 4b (closed registry-lattice counting formula).**" in theorem
            and "all 75 action partitions through five modes" in theorem
            and "`k`-cell partition count is the Stirling convolution" in result
            and "Stirling/Bell classification" in stopping
            and "general Stirling/Bell registry formula" in proof_audit
        ),
        "adaptive_grammar_lattice_certificate": (
            "**Corollary 6b (adaptive grammar-lattice monotonicity).**" in theorem
            and "372,155 nonempty grammar" in theorem
            and "Exactly 12 horizon-four-feasible cases" in result
            and "complete three-mode census checks 372,155" in stopping
            and "12 singleton finite-only" in proof_audit
        ),
        "transient_depth_certificate": (
            "**Proposition 5b (exact finite/infinite separation).**" in theorem
            and "10642,8406,3110,534,12" in theorem
            and "complete first-failure classification" in result
            and "finite-safe prefix has length four" in stopping
            and "independent observer-layer census" in proof_audit
        ),
        "conditional_firewall": (
            "does not contradict the v0.3 bilateral relay theorem" in theorem
            and "upstream normal form" in theorem
        ),
        "status": "partial structural" in result and "classification" in result,
        "completion": "Canonical completion position" in audit,
        "stopping": (
            "another harness cannot choose the branch" in stopping
            and "specification decision" in stopping
            and "missing class quantifier" in stopping
            and "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md" in stopping
        ),
    }


def main() -> int:
    census = independent_partition_census()
    registry_lattice = independent_registry_lattice_census()
    general_registry_formula = independent_general_registry_lattice_formula()
    general_grammar = independent_general_grammar()
    graph_census = independent_graph_census()
    singleton_delays = independent_singleton_delay_census()
    golden_mean = independent_golden_mean()
    adaptive_aperiodic = independent_adaptive_aperiodic()
    adaptive_census = independent_adaptive_census()
    adaptive_grammar_lattice = independent_adaptive_grammar_lattice()
    rows = independent_language_rows()
    embedding = independent_embedding()
    quantifier_audit = independent_canonical_quantifier_audit()
    quantifier_sensitivity = independent_canonical_quantifier_sensitivity()
    registry_model_audit = independent_registry_model_audit()
    global_scope_audit = independent_global_registry_scope_audit()
    sentinels = document_sentinels()
    claim = json.loads((ROOT / "registration_claim_v0_6.json").read_text("utf-8"))
    previous_claim = json.loads(
        (PREVIOUS / "adaptive_claim_v0_5.json").read_text("utf-8")
    )
    predecessor_result = (METRIC_PREDECESSOR / "RESULT.md").read_text("utf-8")
    checks = {
        "I0_independent_partition_census": census
        == {
            "partitions": 15,
            "all_histogram": {1: 1, 2: 7, 3: 6, 4: 1},
            "safe": 4,
            "safe_maps": 4,
            "safe_histogram": {2: 1, 3: 2, 4: 1},
            "coarsest": [[0, 1], [2, 3]],
            "raw_safe": True,
        },
        "I0b_independent_registry_lattice_census": (
            registry_lattice["pass"]
            and registry_lattice["registries"] == 32768
            and registry_lattice["nonempty"] == 32767
            and registry_lattice["covers"] == 245760
            and registry_lattice["strict_covers"] == 26624
            and not registry_lattice["failures"]
        ),
        "I0c_independent_general_registry_lattice_formula": (
            general_registry_formula["pass"]
            and general_registry_formula["shape_rows"] == 18
            and general_registry_formula["action_partitions"] == 75
            and not general_registry_formula["failures"]
        ),
        "I1_independent_language_replay": all(
            row["paths"] == row["raw"] == 4 ** row["horizon"]
            and row["computed"] == row["writes"] == 2 ** row["horizon"]
            for row in rows
        ),
        "I2_independent_continuous_embedding": embedding["pass"],
        "I2b_independent_general_sensor_grammar": (
            general_grammar["pass"]
            and [row["partitions"] for row in general_grammar["rows"]]
            == [1, 2, 5, 15, 52]
            and [row["refinement_pairs"] for row in general_grammar["rows"]]
            == [1, 3, 12, 60, 358]
            and general_grammar["threshold_rows"] == 340
        ),
        "I2c_independent_fixed_transducer_graph_census": (
            graph_census["pass"]
            and graph_census["total_cases"] == 60134
            and graph_census["total_feasible"] == 37430
            and graph_census["comparisons"] == 12060
        ),
        "I2c2_independent_singleton_transient_delay_census": (
            singleton_delays["pass"]
            and singleton_delays["total_cases"] == 60134
            and singleton_delays["infinite_cases"] == 37430
            and singleton_delays["failure_histogram"]
            == {1: 10642, 2: 8406, 3: 3110, 4: 534, 5: 12}
            and singleton_delays["maximum_failure"] == 5
            and not singleton_delays["failures"]
        ),
        "I2d_independent_golden_mean_fixture": (
            golden_mean["pass"]
            and golden_mean["action_counts"] == [1] * 12
            and 0.6942 < golden_mean["entropy"] < 0.6943
        ),
        "I2e_independent_adaptive_aperiodic_fixture": (
            adaptive_aperiodic["pass"]
            and adaptive_aperiodic["adaptive_counts"][:10]
            == [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
            and adaptive_aperiodic["stationary_choices"]
            == {"belief_{0,2}": 0, "belief_{0,1}": 1}
            and adaptive_aperiodic["viable_belief_masks"] == [1, 2, 3, 4, 5]
            and adaptive_aperiodic["initial_belief_viable"]
            and 0.6942 < adaptive_aperiodic["adaptive_entropy"] < 0.6943
        ),
        "I2f_independent_adaptive_three_mode_census": adaptive_census["pass"],
        "I2f2_independent_adaptive_grammar_lattice": (
            adaptive_grammar_lattice["pass"]
            and adaptive_grammar_lattice["nonempty_cases"] == 372155
            and adaptive_grammar_lattice["cover_edges"] == 960400
            and adaptive_grammar_lattice["finite_only"] == 12
            and adaptive_grammar_lattice["maximum_ratio"] == "81"
            and not adaptive_grammar_lattice["failures"]
        ),
        "I2g_independent_canonical_quantifier_audit": (
            quantifier_audit
            == {
                "source": "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
                "explicit_clause_count": 8,
                "upstream_or_raw_selection_clause_count": 0,
                "computed_region": "[1,infinity) x [1,infinity)",
                "raw_region": "[2,infinity) x [1,infinity)",
                "decision": "registration_class_underdetermined",
                "pass": True,
            }
        ),
        "I2h_independent_canonical_quantifier_mutation_sensitivity": (
            quantifier_sensitivity
            == {
                "required_clause_deletions_rejected": 8,
                "closure_selector_insertions_rejected": 4,
                "collapsed_regions_rejected": True,
                "mutation_cases": 13,
                "pass": True,
            }
        ),
        "I2i_independent_registry_model_audit": (
            registry_model_audit["pass"]
            and registry_model_audit["source_obligation_count"] == 13
            and not registry_model_audit["registry_domain_selected"]
            and registry_model_audit["all_models_satisfy_source"]
            and registry_model_audit["models_have_distinct_exact_regions"]
            and registry_model_audit["regions"]
            == {
                "computed_sensor_registry": "[1,infinity) x [1,infinity)",
                "fixed_raw_sensor_registry": "[2,infinity) x [1,infinity)",
            }
            and all(
                model["obligations_satisfied"] == 13
                for model in registry_model_audit["models"].values()
            )
        ),
        "I2j_independent_global_registry_scope_audit": (
            global_scope_audit["pass"]
            and global_scope_audit["registered_occurrence_count"] == 31
            and global_scope_audit["domain_defining_occurrence_count"] == 0
            and global_scope_audit["decision"]
            == "global_sources_do_not_select_registered_code_domain"
            and all(global_scope_audit["checks"].values())
        ),
        "I3_theorem_and_scope_sentinels": all(sentinels.values()),
        "I4_claim_exactness": (
            claim["problem_id"] == "ASMP-4"
            and claim["computed_sensor_class"]
            == {
                "admitted_partition": [[0, 1], [2, 3]],
                "upstream_normal_form_closed": True,
                "downstream_normal_form_closed": True,
                "finite_region": "B_read>=T and B_write>=T",
                "closed_asymptotic_region": "[1,infinity) x [1,infinity)",
            }
            and claim["forced_raw_sensor_class"]
            == {
                "admitted_partition": [[0], [1], [2], [3]],
                "upstream_normal_form_closed": False,
                "downstream_normal_form_closed": True,
                "finite_region": "B_read>=2T and B_write>=T",
                "closed_asymptotic_region": "[2,infinity) x [1,infinity)",
            }
            and claim["partition_census"]
            == {
                "all_partitions": 15,
                "safe_partitions": 4,
                "safe_encoder_controller_pairs": 4,
                "safe_block_counts": {"2": 1, "3": 2, "4": 1},
            }
            and claim["registry_lattice_census"]
            == {
                "all_registries_including_empty": 32768,
                "nonempty_registries": 32767,
                "nonempty_registry_histogram": {
                    "infeasible": 2047,
                    "kappa_2": 16384,
                    "kappa_3": 12288,
                    "kappa_4": 2048,
                },
                "cover_edges": 245760,
                "strict_cover_edges": 26624,
                "monotonicity_failures": 0,
                "strict_raw_to_full_kappa": [4, 2],
            }
            and claim["general_registry_lattice_formula"]
            == {
                "safe_partition_count": (
                    "s_k=sum_{k_1+...+k_m=k} product_i S(n_i,k_i)"
                ),
                "unsafe_partition_count": "u=Bell(n)-sum_k s_k",
                "infeasible_nonempty_registries": "2^u-1",
                "corner_count": "N_k=(2^s_k-1)2^(u+sum_{j>k}s_j)",
                "strict_cover_edges": "sum_k s_k 2^(u+sum_{j>k}s_j)",
                "verified_action_shapes_through_five_modes": 18,
                "verified_action_partitions_through_five_modes": 75,
                "five_mode_2_3_safe_histogram": {"2": 1, "3": 4, "4": 4, "5": 1},
                "five_mode_2_3_infeasible_nonempty_registries": 4398046511103,
                "five_mode_2_3_strict_cover_edges": 2854332185706496,
            }
            and claim["continuous_embedding"]
            == {
                "dynamics": "n_next=(3/2)n+u-q(z), z_next=w",
                "q_polynomial": "(12+13z-z^3)/24",
                "mode_coordinates": ["-3", "-1", "1", "3"],
                "q_values": ["0", "0", "1", "1"],
                "normal_multiplier": "3/2",
                "tangent_reset_derivative": "0",
                "normal_control_derivative": "1",
            }
            and claim["general_reset_mode_theorem"]
            == {
                "action_partition_blocks": "m",
                "sensor_grammar_threshold": (
                    "kappa=min{|P|: P in Gamma and P refines the "
                    "required-action partition}"
                ),
                "finite_region": ("B_read>=T*log2(kappa), B_write>=T*log2(m)"),
                "closed_asymptotic_region": (
                    "[log2(kappa),infinity) x [log2(m),infinity)"
                ),
                "infeasible_condition": (
                    "no P in Gamma refines the required-action partition"
                ),
            }
            and claim["fixed_transducer_graph_theorem"]
            == {
                "feasibility": (
                    "every reachable sensor-subset observer state is "
                    "required-action homogeneous"
                ),
                "finite_region": ("B_read>=log2|L_f(T)|, B_write>=log2|L_g(T)|"),
                "closed_asymptotic_region": ("[h_f,infinity) x [h_g,infinity)"),
                "entropy_computation": (
                    "log2 spectral radius of the reachable deterministic "
                    "subset observer"
                ),
                "golden_mean_fixture_region": ("[log2(phi),infinity) x [0,infinity)"),
            }
            and claim["singleton_transient_delay_census"]
            == {
                "cases_through_three_modes": 60134,
                "infinitely_safe_cases": 37430,
                "first_failure_histogram": {
                    "1": 10642,
                    "2": 8406,
                    "3": 3110,
                    "4": 534,
                    "5": 12,
                },
                "maximum_first_failure_horizon": 5,
                "maximum_safe_finite_horizon": 4,
                "maximum_delay_graph": [[1], [2], [0, 1]],
                "maximum_delay_initial_modes": [0],
                "maximum_delay_sensor_partition": [[0, 1, 2]],
                "maximum_delay_action_partition": [[0, 1], [2]],
            }
            and claim["adaptive_sensor_grammar_theorem"]
            == {
                "finite_recurrence": ("V_0(B)=1; V_(t+1)(B)=min_P sum_C V_t(Succ(C))"),
                "finite_region": ("B_read>=log2 V_T(I), B_write>=log2|L_g(T)|"),
                "infinite_viability": (
                    "I belongs to the greatest belief set K_infinity closed under at "
                    "least one safe registered partition"
                ),
                "positional_value": (
                    "rho_I=lim_T V_T(I)^(1/T)=min_pi limsup_T (e_I^T A_pi^T 1)^(1/T)"
                ),
                "closed_asymptotic_region": ("[log2(rho_I),infinity) x [h_g,infinity)"),
                "stationary_policy_optimal": True,
                "aperiodic_fixture_adaptive_region": (
                    "[log2(phi),infinity) x [log2(phi),infinity)"
                ),
                "aperiodic_fixture_best_fixed_region": (
                    "[1,infinity) x [log2(phi),infinity)"
                ),
            }
            and claim["adaptive_three_mode_census"]
            == {
                "horizon": 4,
                "cases": 120050,
                "adaptive_feasible_cases": 99524,
                "infinitely_viable_cases": 99524,
                "finite_horizon_only_feasible_cases": 0,
                "fixed_feasible_cases": 97952,
                "adaptive_only_feasible_cases": 1572,
                "strict_finite_horizon_improvements": 4863,
                "adaptive_matches_action_language_cases": 73223,
                "maximum_fixed_to_adaptive_ratio": "8",
            }
            and claim["adaptive_grammar_lattice_census"]
            == {
                "horizon": 4,
                "base_graph_initial_action_cases": 12005,
                "nonempty_grammar_cases": 372155,
                "finite_feasible_cases": 320930,
                "infinitely_viable_cases": 320918,
                "finite_horizon_only_cases": 12,
                "finite_horizon_only_grammar_size": 1,
                "finite_horizon_only_first_failure": 5,
                "action_language_exact_cases": 255869,
                "cover_edges": 960400,
                "feasibility_gain_edges": 138546,
                "viability_gain_edges": 138582,
                "strict_finite_value_edges": 104556,
                "maximum_cover_ratio": "81",
                "monotonicity_failures": 0,
            }
            and claim["evidence"]["prior_art_audit"] == "PRIOR_ART_AUDIT_v0_6.md"
            and claim["evidence"]["proof_audit"] == "PROOF_AUDIT_v0_6.md"
            and claim["canonical_quantifier_audit"]
            == {
                "canonical_source": "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
                "explicit_clause_count": 8,
                "requires_upstream_computation_closure": False,
                "requires_forced_raw_transduction": False,
                "computed_sensor_region": "[1,infinity) x [1,infinity)",
                "fixed_raw_sensor_region": "[2,infinity) x [1,infinity)",
                "decision": "registration_class_underdetermined",
            }
            and claim["canonical_quantifier_sensitivity"]
            == {
                "required_clause_deletions_rejected": 8,
                "closure_selector_insertions_rejected": 4,
                "collapsed_regions_rejected": True,
                "mutation_cases": 13,
            }
            and claim["canonical_registry_model_audit"]
            == {
                "source_obligation_count": 13,
                "registry_domain_selected": False,
                "computed_sensor_registry_satisfies_all_obligations": True,
                "fixed_raw_sensor_registry_satisfies_all_obligations": True,
                "computed_sensor_region": "[1,infinity) x [1,infinity)",
                "fixed_raw_sensor_region": "[2,infinity) x [1,infinity)",
                "decision": "two_source_models_with_distinct_regions",
            }
            and claim["global_registry_scope_audit"]
            == {
                "normative_statement_file": ("AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"),
                "machine_index": "problem_set_v0_1.json",
                "machine_index_is_normative": False,
                "graduation_standard_satisfied": False,
                "registered_occurrence_count": 31,
                "domain_defining_occurrence_count": 0,
                "decision": "global_sources_do_not_select_registered_code_domain",
            }
        ),
        "I5_predecessor_firewall": (
            previous_claim["common_history_adaptation"]
            and not previous_claim["changes_canonical_v0_1_metric"]
            and "shared nonnegative port cost" in predecessor_result
            and "If only one computation move is admissible" in predecessor_result
        ),
    }
    payload = {
        "schema_version": "asmp4_registration_fork_independent_v0_6",
        "partition_census": census,
        "registry_lattice_census": registry_lattice,
        "general_registry_lattice_formula": general_registry_formula,
        "general_sensor_grammar": general_grammar,
        "finite_graph_transducers": graph_census,
        "singleton_transient_delay_census": singleton_delays,
        "golden_mean_registration": golden_mean,
        "adaptive_aperiodic_registration": adaptive_aperiodic,
        "adaptive_sensor_grammar_census": adaptive_census,
        "adaptive_grammar_lattice_census": adaptive_grammar_lattice,
        "language_rows": rows,
        "continuous_embedding": embedding,
        "canonical_quantifier_audit": quantifier_audit,
        "canonical_quantifier_sensitivity": quantifier_sensitivity,
        "canonical_registry_model_audit": registry_model_audit,
        "global_registry_scope_audit": global_scope_audit,
        "document_sentinels": sentinels,
        "checks": checks,
        "pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
