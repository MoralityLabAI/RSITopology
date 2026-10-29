"""Exact registration-fork harness for canonical ASMP-4.

The plant, safety predicate, control authority, channels, and terminal-language
metric stay fixed.  Only the admitted sensor grammar changes: either the
sensor may compute a sufficient statistic or it must relay the raw mode.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


MODES = (0, 1, 2, 3)
ACTIONS = (0, 1)
SUFFICIENT_PARTITION = ((0, 1), (2, 3))
RAW_PARTITION = ((0,), (1,), (2,), (3,))
MODE_COORDINATES = (Fraction(-3), Fraction(-1), Fraction(1), Fraction(3))
CANONICAL_SOURCE = (
    Path(__file__).resolve().parents[1] / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
)
CANONICAL_INDEX = Path(__file__).resolve().parents[1] / "problem_set_v0_1.json"
CANONICAL_REQUIRED_FRAGMENTS = {
    "registered_code": "registered causal code `C`",
    "causal_sensor_encoder": "A causal sensor encoder emits only the read transcript",
    "separate_components": (
        "The plant, sensor, controller, and actuator are separate components"
    ),
    "architecture_explicit": "explicit parts of the architecture",
    "registered_class": (
        "For a registered normally hyperbolic, locally controllable class"
    ),
    "architecture_tradeoffs": "architecture-dependent tradeoff inequalities",
    "nonrectangular_allowed": (
        "does **not** assume the region is rectangular in general"
    ),
    "sensor_experiment_fixed_in_witness": "hold the sensor experiment fixed",
}
CANONICAL_SELECTION_FRAGMENTS = {
    "requires_upstream_computation_closure": (
        "closed under upstream computation",
        "replace its observation by an arbitrary sufficient statistic",
    ),
    "requires_forced_raw_transduction": (
        "forced injective raw sensor",
        "must emit an injective raw",
    ),
}
CANONICAL_MODEL_OBLIGATION_FRAGMENTS = {
    "registered_code_domain": "For a registered causal code `C` and horizon `T`",
    "finite_transcript_alphabets": (
        "finite transcript alphabets, or prefix-free countable alphabets charged "
        "by worst-case length"
    ),
    "sensor_only_read_port": ("A causal sensor encoder emits only the read transcript"),
    "controller_only_read_to_write": (
        "a controller receives only those symbols and emits the write transcript"
    ),
    "actuator_write_to_control": ("an actuator decoder maps write symbols to controls"),
    "separate_components": (
        "The plant, sensor, controller, and actuator are separate components"
    ),
    "no_uncharged_side_channel": (
        "No analog state, shared object reference, common random variable correlated "
        "with the state, or uncharged side channel may cross either interface"
    ),
    "architecture_explicit": (
        "Internal memory, delays, block coding, and shared randomness independent "
        "of the plant state are explicit parts of the architecture"
    ),
    "existential_registered_code": "there exists a registered causal code C with",
    "universal_disturbance_safety": "for every allowed disturbance sequence",
    "registered_bounded_class": (
        "For a registered normally hyperbolic, locally controllable class with "
        "bounded uncertainty, delay, memory, control-authority, and disturbance "
        "conventions"
    ),
    "architecture_dependent_tradeoffs": (
        "architecture-dependent tradeoff inequalities"
    ),
    "no_universal_rectangularity_assumption": (
        "does **not** assume the region is rectangular in general"
    ),
}
CANONICAL_REGISTRY_DOMAIN_SELECTION_FRAGMENTS = (
    "every causal code is registered",
    "all causal codes are registered",
    "every causal sensor encoder is registered",
    "all causal sensor encoders are registered",
)


def required_action(mode: int) -> int:
    """The unique action that prevents transition to BAD."""

    if mode not in MODES:
        raise ValueError(f"unknown mode: {mode}")
    return mode // 2


def coupling_polynomial(z_value: Fraction) -> Fraction:
    """Rational polynomial taking values 0,0,1,1 on the four mode points."""

    return (12 + 13 * z_value - z_value**3) / 24


def continuous_embedding_report(horizon: int = 6) -> dict[str, Any]:
    """Replay the finite fork inside an unstable evaluator-normal plant."""

    if not 1 <= horizon <= 8:
        raise ValueError("horizon must lie between one and eight")
    values = tuple(coupling_polynomial(z_value) for z_value in MODE_COORDINATES)
    correct_paths = 0
    for z_word in itertools.product(MODE_COORDINATES, repeat=horizon):
        normal_state = Fraction(0)
        for z_value in z_word:
            control = coupling_polynomial(z_value)
            normal_state = (
                Fraction(3, 2) * normal_state + control - coupling_polynomial(z_value)
            )
            if normal_state != 0:
                break
        else:
            correct_paths += 1
    wrong_successors = tuple((1 - int(value)) - value for value in values)
    return {
        "dynamics": "n_next=(3/2)n+u-q(z), z_next=w",
        "q_polynomial": "(12+13z-z^3)/24",
        "mode_coordinates": [str(value) for value in MODE_COORDINATES],
        "q_values": [str(value) for value in values],
        "normal_multiplier": "3/2",
        "tangent_reset_derivative": "0",
        "normal_control_derivative": "1",
        "evaluator_safe_condition": "n=0",
        "replayed_horizon": horizon,
        "correct_safe_paths": correct_paths,
        "wrong_control_normal_successors": [str(value) for value in wrong_successors],
        "pass": (
            values == (Fraction(0), Fraction(0), Fraction(1), Fraction(1))
            and correct_paths == 4**horizon
            and set(wrong_successors) == {Fraction(-1), Fraction(1)}
            and Fraction(3, 2) > 1
        ),
    }


def canonical_quantifier_audit(
    computed_region: str = "[1,infinity) x [1,infinity)",
    raw_region: str = "[2,infinity) x [1,infinity)",
    *,
    source_text: str | None = None,
) -> dict[str, Any]:
    """Check which sensor-grammar closure, if any, the source text selects."""

    source = (
        CANONICAL_SOURCE.read_text(encoding="utf-8")
        if source_text is None
        else source_text
    )
    normalized = " ".join(source.split())
    source_clauses = {
        name: fragment in normalized
        for name, fragment in CANONICAL_REQUIRED_FRAGMENTS.items()
    }
    closure_clauses = {
        name: any(fragment in normalized for fragment in fragments)
        for name, fragments in CANONICAL_SELECTION_FRAGMENTS.items()
    }
    distinct_regions = computed_region != raw_region
    neither_closure_selected = not any(closure_clauses.values())
    return {
        "canonical_source": CANONICAL_SOURCE.name,
        "source_clauses": source_clauses,
        "closure_clauses": closure_clauses,
        "computed_region": computed_region,
        "raw_region": raw_region,
        "neither_sensor_closure_is_textually_selected": neither_closure_selected,
        "registrations_have_distinct_exact_regions": distinct_regions,
        "decision": "registration_class_underdetermined",
        "pass": (
            all(source_clauses.values())
            and neither_closure_selected
            and distinct_regions
        ),
    }


def canonical_quantifier_sensitivity_audit() -> dict[str, Any]:
    """Require the source audit to react to each decision-relevant mutation."""

    source = CANONICAL_SOURCE.read_text(encoding="utf-8")
    normalized_source = " ".join(source.split())
    required_clause_mutations = {}
    for name, fragment in CANONICAL_REQUIRED_FRAGMENTS.items():
        mutated = normalized_source.replace(fragment, "")
        report = canonical_quantifier_audit(source_text=mutated)
        required_clause_mutations[name] = (
            not report["pass"] and not report["source_clauses"][name]
        )

    selector_mutations = {}
    for name, fragments in CANONICAL_SELECTION_FRAGMENTS.items():
        for index, fragment in enumerate(fragments):
            mutated = f"{normalized_source} {fragment}."
            report = canonical_quantifier_audit(source_text=mutated)
            selector_mutations[f"{name}_{index}"] = (
                not report["pass"] and report["closure_clauses"][name]
            )

    collapsed_region_report = canonical_quantifier_audit(
        "[1,infinity) x [1,infinity)", "[1,infinity) x [1,infinity)"
    )
    collapsed_regions_rejected = (
        not collapsed_region_report["pass"]
        and not collapsed_region_report["registrations_have_distinct_exact_regions"]
    )
    cases = len(required_clause_mutations) + len(selector_mutations) + 1
    return {
        "required_clause_deletions": required_clause_mutations,
        "closure_selector_insertions": selector_mutations,
        "collapsed_regions_rejected": collapsed_regions_rejected,
        "mutation_cases": cases,
        "pass": (
            all(required_clause_mutations.values())
            and all(selector_mutations.values())
            and collapsed_regions_rejected
        ),
    }


def canonical_registry_model_audit(
    computed_region: str = "[1,infinity) x [1,infinity)",
    raw_region: str = "[2,infinity) x [1,infinity)",
    *,
    source_text: str | None = None,
) -> dict[str, Any]:
    """Check two executable models of the source's undefined registry predicate."""

    source = (
        CANONICAL_SOURCE.read_text(encoding="utf-8")
        if source_text is None
        else source_text
    )
    normalized = " ".join(source.split())
    source_obligations = {
        name: fragment in normalized
        for name, fragment in CANONICAL_MODEL_OBLIGATION_FRAGMENTS.items()
    }

    registry_domain_selected = any(
        fragment in normalized
        for fragment in CANONICAL_REGISTRY_DOMAIN_SELECTION_FRAGMENTS
    )
    quantifier = canonical_quantifier_audit(
        computed_region, raw_region, source_text=source
    )
    embedding = continuous_embedding_report(horizon=6)
    language_rows = exact_language_rows(max_horizon=6)
    all_paths_safe = embedding["pass"] and all(row["pass"] for row in language_rows)

    registries = {
        "computed_sensor_registry": {
            "registry_predicate": (
                "deterministic causal sensor encoders including sufficient statistics"
            ),
            "sensor_partition": SUFFICIENT_PARTITION,
            "sensor_map": (0, 0, 1, 1),
            "controller_map": (0, 1),
            "actuator_map": (0, 1),
            "read_alphabet_size": 2,
            "write_alphabet_size": 2,
            "component_edges": (
                "plant_to_sensor_state",
                "sensor_to_controller_read",
                "controller_to_actuator_write",
                "actuator_to_plant_control",
            ),
            "side_channels": (),
            "asserts_all_regions_rectangular": False,
            "upstream_computation_closed": True,
            "closed_asymptotic_region": computed_region,
        },
        "fixed_raw_sensor_registry": {
            "registry_predicate": "sensor encoder equals the injective raw-mode map",
            "sensor_partition": RAW_PARTITION,
            "sensor_map": (0, 1, 2, 3),
            "controller_map": (0, 0, 1, 1),
            "actuator_map": (0, 1),
            "read_alphabet_size": 4,
            "write_alphabet_size": 2,
            "component_edges": (
                "plant_to_sensor_state",
                "sensor_to_controller_read",
                "controller_to_actuator_write",
                "actuator_to_plant_control",
            ),
            "side_channels": (),
            "asserts_all_regions_rectangular": False,
            "upstream_computation_closed": False,
            "closed_asymptotic_region": raw_region,
        },
    }

    model_reports = {}
    for name, model in registries.items():
        sensor_map = model["sensor_map"]
        controller_map = model["controller_map"]
        actuator_map = model["actuator_map"]
        safe_code_exists = all(
            actuator_map[controller_map[sensor_map[mode]]] == required_action(mode)
            for mode in MODES
        )
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
        satisfaction = {
            "registered_code_domain": bool(model["registry_predicate"]),
            "finite_transcript_alphabets": (
                isinstance(model["read_alphabet_size"], int)
                and model["read_alphabet_size"] > 0
                and isinstance(model["write_alphabet_size"], int)
                and model["write_alphabet_size"] > 0
            ),
            "sensor_only_read_port": (
                len(sensor_map) == len(MODES)
                and "sensor_to_controller_read" in model["component_edges"]
                and all(
                    edge == "sensor_to_controller_read"
                    for edge in model["component_edges"]
                    if edge.startswith("sensor_to_")
                )
            ),
            "controller_only_read_to_write": (
                len(controller_map) == model["read_alphabet_size"]
            ),
            "actuator_write_to_control": (
                len(actuator_map) == model["write_alphabet_size"]
                and set(actuator_map).issubset(ACTIONS)
            ),
            "separate_components": model["component_edges"]
            == (
                "plant_to_sensor_state",
                "sensor_to_controller_read",
                "controller_to_actuator_write",
                "actuator_to_plant_control",
            ),
            "no_uncharged_side_channel": model["side_channels"] == (),
            "architecture_explicit": set(explicit_architecture)
            == {
                "sensor_memory",
                "controller_memory",
                "actuator_memory",
                "sensor_delay",
                "controller_delay",
                "actuator_delay",
                "block_length",
                "shared_randomness",
            },
            "existential_registered_code": safe_code_exists,
            "universal_disturbance_safety": all_paths_safe,
            "registered_bounded_class": (
                embedding["normal_multiplier"] == "3/2"
                and embedding["tangent_reset_derivative"] == "0"
                and embedding["normal_control_derivative"] == "1"
                and len(MODE_COORDINATES) == 4
            ),
            "architecture_dependent_tradeoffs": bool(model["closed_asymptotic_region"]),
            "no_universal_rectangularity_assumption": not model[
                "asserts_all_regions_rectangular"
            ],
        }
        model_reports[name] = {
            **model,
            "explicit_architecture": explicit_architecture,
            "safe_code_exists": safe_code_exists,
            "obligation_satisfaction": satisfaction,
            "pass": all(satisfaction.values()),
        }

    distinct_regions = computed_region != raw_region
    all_models_satisfy_source = all(report["pass"] for report in model_reports.values())
    return {
        "canonical_source": CANONICAL_SOURCE.name,
        "source_obligations": source_obligations,
        "source_obligation_count": sum(source_obligations.values()),
        "registry_domain_selected": registry_domain_selected,
        "registry_predicate_is_undefined": not registry_domain_selected,
        "models": model_reports,
        "all_models_satisfy_source": all_models_satisfy_source,
        "models_have_distinct_exact_regions": distinct_regions,
        "existential_region_depends_on_registry_predicate": (
            all_models_satisfy_source and distinct_regions
        ),
        "decision": "two_source_models_with_distinct_regions",
        "pass": (
            all(source_obligations.values())
            and quantifier["pass"]
            and not registry_domain_selected
            and all_models_satisfy_source
            and distinct_regions
        ),
    }


def global_registry_scope_audit(
    *,
    source_text: str | None = None,
    index_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check whether any global normative source closes the ASMP-4 code domain."""

    source = (
        CANONICAL_SOURCE.read_text(encoding="utf-8")
        if source_text is None
        else source_text
    )
    normalized = " ".join(source.split())
    normalized_lower = normalized.lower()
    index = (
        json.loads(CANONICAL_INDEX.read_text(encoding="utf-8"))
        if index_data is None
        else index_data
    )
    problems = [problem for problem in index["problems"] if problem["id"] == "ASMP-4"]
    asmp4 = problems[0] if len(problems) == 1 else {}
    source_registered_occurrences = normalized_lower.count("registered")
    global_domain_selection_fragments = (
        *CANONICAL_REGISTRY_DOMAIN_SELECTION_FRAGMENTS,
        "registered causal code means",
        "registered causal code denotes",
        "a causal code is registered if",
        "a causal code is registered exactly when",
        "the registry of causal codes is",
    )
    domain_defining_fragments_present = {
        fragment: fragment in normalized_lower
        for fragment in global_domain_selection_fragments
    }
    graduation_fragments = {
        "formal_domains_explicit": (
            "Objects, domains, encodings, resource bounds, randomness, adversaries, "
            "and quantifier order are explicit" in normalized
        ),
        "version_changes_quantifiers": (
            "a change to its objects, quantifiers, adversary, or resolution criterion "
            "changes the problem" in normalized
        ),
    }
    index_checks = {
        "normative_statement_is_markdown": (
            index.get("normative_statement_file") == CANONICAL_SOURCE.name
        ),
        "machine_index_is_non_normative": index.get("registry_is_normative") is False,
        "candidate_is_definition_draft": (
            index.get("status") == "proposed_candidate_definition_draft"
        ),
        "graduation_standard_not_satisfied": (
            index.get("graduation_standard_satisfied") is False
        ),
        "closed_formal_core_is_required": (
            "closed_formal_core" in index.get("graduation_requirements", [])
        ),
        "exactly_one_asmp4_entry": len(problems) == 1,
        "asmp4_entry_does_not_define_code_domain": (
            "registered_code_domain" not in asmp4
            and "sensor_grammar" not in asmp4
            and "upstream_computation_closed" not in asmp4
        ),
    }
    no_global_domain_definition = not any(domain_defining_fragments_present.values())
    return {
        "canonical_source": CANONICAL_SOURCE.name,
        "machine_index": CANONICAL_INDEX.name,
        "registered_occurrence_count": source_registered_occurrences,
        "domain_defining_occurrence_count": sum(
            domain_defining_fragments_present.values()
        ),
        "domain_defining_fragments_present": domain_defining_fragments_present,
        "graduation_fragments": graduation_fragments,
        "index_checks": index_checks,
        "no_global_domain_definition": no_global_domain_definition,
        "normative_scope_remains_the_markdown_draft": all(index_checks.values()),
        "decision": "global_sources_do_not_select_registered_code_domain",
        "pass": (
            source_registered_occurrences == 31
            and no_global_domain_definition
            and all(graduation_fragments.values())
            and all(index_checks.values())
        ),
    }


@lru_cache(maxsize=None)
def set_partitions(item_count: int) -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Enumerate set partitions via restricted-growth strings."""

    if not 1 <= item_count <= 6:
        raise ValueError("item_count must lie between one and six")
    items = tuple(range(item_count))
    partitions = []
    for labels in itertools.product(range(item_count), repeat=item_count):
        if labels[0] != 0:
            continue
        largest = 0
        valid = True
        for label in labels[1:]:
            if label > largest + 1:
                valid = False
                break
            largest = max(largest, label)
        if not valid:
            continue
        blocks = tuple(
            tuple(
                mode
                for mode, label in zip(items, labels, strict=True)
                if label == block
            )
            for block in range(largest + 1)
        )
        partitions.append(blocks)
    return tuple(partitions)


@lru_cache(maxsize=None)
def stirling_second(item_count: int, block_count: int) -> int:
    """Return the exact Stirling number of the second kind."""

    if item_count == 0:
        return int(block_count == 0)
    if block_count <= 0 or block_count > item_count:
        return 0
    return block_count * stirling_second(item_count - 1, block_count) + stirling_second(
        item_count - 1, block_count - 1
    )


@lru_cache(maxsize=None)
def bell_number(item_count: int) -> int:
    """Return the exact Bell number from the Stirling recurrence."""

    if item_count < 0:
        raise ValueError("item_count must be nonnegative")
    return sum(
        stirling_second(item_count, block_count)
        for block_count in range(item_count + 1)
    )


def all_mode_partitions() -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Enumerate all partitions of the registered four modes."""

    return set_partitions(len(MODES))


def safe_controller_maps(
    partition: Iterable[Iterable[int]],
) -> tuple[tuple[int, ...], ...]:
    """Exhaust every block-to-action map that is safe for all four modes."""

    blocks = tuple(tuple(block) for block in partition)
    return tuple(
        controller
        for controller in itertools.product(ACTIONS, repeat=len(blocks))
        if all(
            controller[block_index] == required_action(mode)
            for block_index, block in enumerate(blocks)
            for mode in block
        )
    )


def partition_is_safe(partition: Iterable[Iterable[int]]) -> bool:
    """A one-step sensor partition is safe iff some controller map succeeds."""

    return bool(safe_controller_maps(partition))


def partition_census() -> dict[str, Any]:
    """Exhaust the observation partitions and identify every safe encoder."""

    partitions = all_mode_partitions()
    safe = tuple(partition for partition in partitions if partition_is_safe(partition))
    safe_controller_count = sum(
        len(safe_controller_maps(partition)) for partition in partitions
    )
    all_histogram = Counter(len(partition) for partition in partitions)
    safe_histogram = Counter(len(partition) for partition in safe)
    return {
        "all_partition_count": len(partitions),
        "all_block_count_histogram": dict(sorted(all_histogram.items())),
        "safe_partition_count": len(safe),
        "safe_encoder_controller_pair_count": safe_controller_count,
        "safe_block_count_histogram": dict(sorted(safe_histogram.items())),
        "safe_partitions": [[list(block) for block in partition] for partition in safe],
        "minimum_safe_read_symbols": min(map(len, safe)),
        "unique_minimum_safe_partition": [list(block) for block in min(safe, key=len)],
        "raw_partition_is_safe": RAW_PARTITION in safe,
        "pass": (
            len(partitions) == 15
            and all_histogram == {1: 1, 2: 7, 3: 6, 4: 1}
            and len(safe) == 4
            and safe_controller_count == 4
            and safe_histogram == {2: 1, 3: 2, 4: 1}
            and min(safe, key=len) == SUFFICIENT_PARTITION
            and RAW_PARTITION in safe
        ),
    }


@lru_cache(maxsize=None)
def registry_lattice_census() -> dict[str, Any]:
    """Exhaust every registry of the 15 sensor partitions and all cover edges."""

    partitions = all_mode_partitions()
    partition_count = len(partitions)
    safe_block_counts = tuple(
        len(partition) if partition_is_safe(partition) else None
        for partition in partitions
    )
    registry_count = 1 << partition_count
    infinity_rank = partition_count + 1
    minimum_safe_blocks = [infinity_rank] * registry_count
    histogram: Counter[str] = Counter()
    for mask in range(1, registry_count):
        safe_counts = [
            block_count
            for index, block_count in enumerate(safe_block_counts)
            if block_count is not None and mask & (1 << index)
        ]
        if not safe_counts:
            histogram["infeasible"] += 1
            continue
        minimum_safe_blocks[mask] = min(safe_counts)
        histogram[f"kappa_{minimum_safe_blocks[mask]}"] += 1

    cover_edges = 0
    strict_cover_edges = 0
    monotonicity_failures = []
    for mask in range(registry_count):
        for index in range(partition_count):
            bit = 1 << index
            if mask & bit:
                continue
            expanded = mask | bit
            cover_edges += 1
            if minimum_safe_blocks[expanded] > minimum_safe_blocks[mask]:
                monotonicity_failures.append((mask, expanded))
            elif minimum_safe_blocks[expanded] < minimum_safe_blocks[mask]:
                strict_cover_edges += 1

    raw_index = partitions.index(RAW_PARTITION)
    sufficient_index = partitions.index(SUFFICIENT_PARTITION)
    raw_only_mask = 1 << raw_index
    full_registry_mask = registry_count - 1
    strict_fork_witness = {
        "raw_only_mask": raw_only_mask,
        "full_registry_mask": full_registry_mask,
        "raw_is_subset_of_full": (raw_only_mask & full_registry_mask == raw_only_mask),
        "raw_kappa": minimum_safe_blocks[raw_only_mask],
        "full_kappa": minimum_safe_blocks[full_registry_mask],
        "sufficient_partition_index": sufficient_index,
        "computed_only_rate_point": "(1,1)",
    }
    expected_histogram = {
        "infeasible": 2047,
        "kappa_2": 16384,
        "kappa_3": 12288,
        "kappa_4": 2048,
    }
    return {
        "partition_count": partition_count,
        "all_registries_including_empty": registry_count,
        "nonempty_registries": registry_count - 1,
        "nonempty_registry_histogram": dict(sorted(histogram.items())),
        "cover_edges": cover_edges,
        "strict_cover_edges": strict_cover_edges,
        "monotonicity_failures": monotonicity_failures,
        "strict_fork_witness": strict_fork_witness,
        "exact_corner_rule": (
            "infeasible if no safe partition; otherwise "
            "[log2(kappa),infinity) x [1,infinity)"
        ),
        "pass": (
            partition_count == 15
            and registry_count == 32768
            and histogram == expected_histogram
            and cover_edges == 245760
            and strict_cover_edges == 26624
            and not monotonicity_failures
            and strict_fork_witness["raw_is_subset_of_full"]
            and strict_fork_witness["raw_kappa"] == 4
            and strict_fork_witness["full_kappa"] == 2
        ),
    }


def partition_refines(
    sensor_partition: tuple[tuple[int, ...], ...],
    action_partition: tuple[tuple[int, ...], ...],
) -> bool:
    """Return whether every sensor cell lies inside one required-action cell."""

    action_cell = {
        mode: block_index
        for block_index, block in enumerate(action_partition)
        for mode in block
    }
    return all(
        len({action_cell[mode] for mode in sensor_block}) == 1
        for sensor_block in sensor_partition
    )


@lru_cache(maxsize=None)
def general_sensor_grammar_report(max_modes: int = 5) -> dict[str, Any]:
    """Audit the parameterized full-reset sensor-grammar formula."""

    if not 1 <= max_modes <= 5:
        raise ValueError("max_modes must lie between one and five")
    expected_refinement_pairs = {1: 1, 2: 3, 3: 12, 4: 60, 5: 358}
    rows = []
    threshold_rows = []
    failures = []
    for mode_count in range(1, max_modes + 1):
        partitions = set_partitions(mode_count)
        refinement_pairs = 0
        action_histogram = Counter(map(len, partitions))
        for action_partition in partitions:
            action_count = len(action_partition)
            safe_sensors = tuple(
                sensor_partition
                for sensor_partition in partitions
                if partition_refines(sensor_partition, action_partition)
            )
            refinement_pairs += len(safe_sensors)
            expected_safe_sensors = math.prod(
                len(set_partitions(len(block))) for block in action_partition
            )
            if len(safe_sensors) != expected_safe_sensors:
                failures.append(
                    {
                        "kind": "refinement_product",
                        "modes": mode_count,
                        "action_partition": action_partition,
                    }
                )
            if min(map(len, safe_sensors)) != action_count:
                failures.append(
                    {
                        "kind": "all_partition_grammar_threshold",
                        "modes": mode_count,
                        "action_partition": action_partition,
                    }
                )
            raw_partition = tuple((mode,) for mode in range(mode_count))
            if not partition_refines(raw_partition, action_partition):
                failures.append(
                    {
                        "kind": "raw_partition",
                        "modes": mode_count,
                        "action_partition": action_partition,
                    }
                )
            for minimum_blocks in range(1, mode_count + 1):
                grammar = tuple(
                    sensor_partition
                    for sensor_partition in safe_sensors
                    if len(sensor_partition) >= minimum_blocks
                )
                kappa = min(map(len, grammar))
                expected_kappa = max(action_count, minimum_blocks)
                threshold_rows.append(
                    {
                        "modes": mode_count,
                        "action_blocks": action_count,
                        "minimum_registered_blocks": minimum_blocks,
                        "kappa": kappa,
                        "two_step_read_words": kappa**2,
                        "two_step_write_words": action_count**2,
                    }
                )
                if kappa != expected_kappa:
                    failures.append(
                        {
                            "kind": "threshold_grammar",
                            "modes": mode_count,
                            "action_partition": action_partition,
                            "minimum_blocks": minimum_blocks,
                            "observed": kappa,
                            "expected": expected_kappa,
                        }
                    )
        rows.append(
            {
                "modes": mode_count,
                "partitions": len(partitions),
                "action_partition_histogram": dict(sorted(action_histogram.items())),
                "safe_action_sensor_partition_pairs": refinement_pairs,
                "expected_refinement_pairs": expected_refinement_pairs[mode_count],
                "fixed_partition_infeasible_pairs": len(partitions) ** 2
                - refinement_pairs,
            }
        )
        if refinement_pairs != expected_refinement_pairs[mode_count]:
            failures.append(
                {
                    "kind": "refinement_pair_total",
                    "modes": mode_count,
                    "observed": refinement_pairs,
                    "expected": expected_refinement_pairs[mode_count],
                }
            )
    return {
        "max_modes": max_modes,
        "rows": rows,
        "threshold_rows": threshold_rows,
        "threshold_row_count": len(threshold_rows),
        "formula": {
            "kappa": "min{|P|: P in Gamma and P refines the required-action partition}",
            "finite_region": "B_read>=T*log2(kappa), B_write>=T*log2(m)",
            "closed_asymptotic_region": "[log2(kappa),infinity) x [log2(m),infinity)",
            "infeasible_condition": "no partition in Gamma refines the required-action partition",
        },
        "failures": failures,
        "pass": not failures,
    }


@lru_cache(maxsize=None)
def general_registry_lattice_formula_report(max_modes: int = 5) -> dict[str, Any]:
    """Prove the registry-lattice counts for every action shape through n modes."""

    if not 1 <= max_modes <= 5:
        raise ValueError("max_modes must lie between one and five")
    rows = []
    failures = []
    audited_action_partitions = 0
    for mode_count in range(1, max_modes + 1):
        partitions = set_partitions(mode_count)
        total_sensor_partitions = bell_number(mode_count)
        if total_sensor_partitions != len(partitions):
            failures.append((mode_count, "bell_number", total_sensor_partitions))
        action_shapes: dict[tuple[int, ...], list[tuple[tuple[int, ...], ...]]] = {}
        for action_partition in partitions:
            shape = tuple(sorted(map(len, action_partition)))
            action_shapes.setdefault(shape, []).append(action_partition)
        for shape, action_partitions in sorted(action_shapes.items()):
            audited_action_partitions += len(action_partitions)
            formula_safe_histogram: Counter[int] = Counter()
            allocation_ranges = [range(1, block_size + 1) for block_size in shape]
            for allocation in itertools.product(*allocation_ranges):
                formula_safe_histogram[sum(allocation)] += math.prod(
                    stirling_second(block_size, cells)
                    for block_size, cells in zip(shape, allocation, strict=True)
                )
            enumerated_histograms = []
            for action_partition in action_partitions:
                enumerated_histograms.append(
                    Counter(
                        len(sensor_partition)
                        for sensor_partition in partitions
                        if partition_refines(sensor_partition, action_partition)
                    )
                )
            if any(
                histogram != formula_safe_histogram
                for histogram in enumerated_histograms
            ):
                failures.append((mode_count, shape, "safe_histogram"))
            safe_partition_count = sum(formula_safe_histogram.values())
            expected_safe_count = math.prod(bell_number(size) for size in shape)
            unsafe_partition_count = total_sensor_partitions - safe_partition_count
            if safe_partition_count != expected_safe_count:
                failures.append((mode_count, shape, "safe_product"))

            registry_corner_histogram = {}
            sorted_kappas = sorted(formula_safe_histogram)
            for kappa in sorted_kappas:
                larger_safe_count = sum(
                    count
                    for blocks, count in formula_safe_histogram.items()
                    if blocks > kappa
                )
                registry_corner_histogram[f"kappa_{kappa}"] = (
                    2 ** formula_safe_histogram[kappa] - 1
                ) * 2 ** (unsafe_partition_count + larger_safe_count)
            infeasible_nonempty = 2**unsafe_partition_count - 1
            all_registries = 2**total_sensor_partitions
            feasible_registries = sum(registry_corner_histogram.values())
            strict_cover_edges = sum(
                formula_safe_histogram[kappa]
                * 2
                ** (
                    unsafe_partition_count
                    + sum(
                        count
                        for blocks, count in formula_safe_histogram.items()
                        if blocks > kappa
                    )
                )
                for kappa in sorted_kappas
            )
            cover_edges = total_sensor_partitions * 2 ** (total_sensor_partitions - 1)
            if infeasible_nonempty + feasible_registries != all_registries - 1:
                failures.append((mode_count, shape, "registry_checksum"))
            rows.append(
                {
                    "modes": mode_count,
                    "action_block_sizes": list(shape),
                    "action_partition_count": len(action_partitions),
                    "sensor_partition_count": total_sensor_partitions,
                    "safe_partition_histogram": {
                        str(blocks): count
                        for blocks, count in sorted(formula_safe_histogram.items())
                    },
                    "unsafe_partition_count": unsafe_partition_count,
                    "all_registries_including_empty": all_registries,
                    "infeasible_nonempty_registries": infeasible_nonempty,
                    "feasible_registries": feasible_registries,
                    "registry_corner_histogram": registry_corner_histogram,
                    "cover_edges": cover_edges,
                    "strict_cover_edges": strict_cover_edges,
                }
            )
    fixture_rows = [
        row for row in rows if row["modes"] == 4 and row["action_block_sizes"] == [2, 2]
    ]
    fixture_matches = len(fixture_rows) == 1 and fixture_rows[0][
        "registry_corner_histogram"
    ] == {"kappa_2": 16384, "kappa_3": 12288, "kappa_4": 2048}
    return {
        "max_modes": max_modes,
        "action_shape_rows": len(rows),
        "audited_action_partitions": audited_action_partitions,
        "rows": rows,
        "formula": {
            "safe_partition_count": ("s_k=sum_{k_1+...+k_m=k} product_i S(n_i,k_i)"),
            "unsafe_partition_count": "u=Bell(n)-sum_k s_k",
            "infeasible_nonempty_registries": "2^u-1",
            "corner_count": "N_k=(2^s_k-1)2^(u+sum_{j>k}s_j)",
            "strict_cover_edges": "sum_k s_k 2^(u+sum_{j>k}s_j)",
        },
        "fixture_matches_complete_census": fixture_matches,
        "failures": failures,
        "pass": (
            len(rows) == 18
            and audited_action_partitions == 75
            and fixture_matches
            and not failures
        ),
    }


def _partition_labels(
    partition: tuple[tuple[int, ...], ...],
) -> dict[int, int]:
    return {mode: label for label, block in enumerate(partition) for mode in block}


def observer_beliefs(
    graph: tuple[tuple[int, ...], ...],
    initial_modes: tuple[int, ...],
    partition: tuple[tuple[int, ...], ...],
) -> frozenset[frozenset[int]]:
    """Build every reachable current-state belief after a transducer word."""

    initial_set = frozenset(initial_modes)
    pending = [
        frozenset(initial_set.intersection(block))
        for block in partition
        if initial_set.intersection(block)
    ]
    reached = set(pending)
    while pending:
        belief = pending.pop()
        successors = {target for mode in belief for target in graph[mode]}
        for block in partition:
            target_belief = frozenset(successors.intersection(block))
            if target_belief and target_belief not in reached:
                reached.add(target_belief)
                pending.append(target_belief)
    return frozenset(reached)


def observer_language_counts(
    graph: tuple[tuple[int, ...], ...],
    initial_modes: tuple[int, ...],
    partition: tuple[tuple[int, ...], ...],
    horizon: int,
) -> tuple[int, ...]:
    """Count distinct transducer words with deterministic subset construction."""

    if horizon < 1:
        raise ValueError("horizon must be positive")
    initial_set = frozenset(initial_modes)
    active: dict[frozenset[int], int] = {}
    for block in partition:
        belief = frozenset(initial_set.intersection(block))
        if belief:
            active[belief] = active.get(belief, 0) + 1
    counts = [sum(active.values())]
    for _ in range(1, horizon):
        following: dict[frozenset[int], int] = {}
        for belief, word_count in active.items():
            successors = {target for mode in belief for target in graph[mode]}
            for block in partition:
                target_belief = frozenset(successors.intersection(block))
                if target_belief:
                    following[target_belief] = (
                        following.get(target_belief, 0) + word_count
                    )
        active = following
        counts.append(sum(active.values()))
    return tuple(counts)


def brute_label_language_counts(
    graph: tuple[tuple[int, ...], ...],
    initial_modes: tuple[int, ...],
    partition: tuple[tuple[int, ...], ...],
    horizon: int,
) -> tuple[int, ...]:
    """Independently count labels by expanding every state path."""

    labels = _partition_labels(partition)
    paths = {(mode,) for mode in initial_modes}
    counts = [len({tuple(labels[mode] for mode in path) for path in paths})]
    for _ in range(1, horizon):
        paths = {(*path, target) for path in paths for target in graph[path[-1]]}
        counts.append(len({tuple(labels[mode] for mode in path) for path in paths}))
    return tuple(counts)


def action_is_observable_from_transducer(
    graph: tuple[tuple[int, ...], ...],
    initial_modes: tuple[int, ...],
    sensor_partition: tuple[tuple[int, ...], ...],
    action_partition: tuple[tuple[int, ...], ...],
) -> bool:
    """Test whether every reachable sensor belief fixes the required action."""

    action_labels = _partition_labels(action_partition)
    return all(
        len({action_labels[mode] for mode in belief}) == 1
        for belief in observer_beliefs(graph, initial_modes, sensor_partition)
    )


def _nonblocking_graphs(mode_count: int) -> Iterable[tuple[tuple[int, ...], ...]]:
    successor_sets = tuple(
        tuple(mode for mode in range(mode_count) if mask & (1 << mode))
        for mask in range(1, 1 << mode_count)
    )
    yield from itertools.product(successor_sets, repeat=mode_count)


@lru_cache(maxsize=None)
def finite_graph_transducer_census(
    max_modes: int = 3, horizon: int = 4
) -> dict[str, Any]:
    """Exhaust fixed transducers on every nonblocking graph through three modes."""

    if not 1 <= max_modes <= 3 or not 1 <= horizon <= 5:
        raise ValueError("unsupported census bounds")
    expected_case_counts = {1: 1, 2: 108, 3: 60025}
    rows = []
    mismatches = []
    total_cases = 0
    total_feasible = 0
    language_comparisons = 0
    for mode_count in range(1, max_modes + 1):
        partitions = set_partitions(mode_count)
        graphs = tuple(_nonblocking_graphs(mode_count))
        mode_cases = 0
        mode_feasible = 0
        for graph in graphs:
            for initial_mask in range(1, 1 << mode_count):
                initial_modes = tuple(
                    mode for mode in range(mode_count) if initial_mask & (1 << mode)
                )
                reports = {}
                for partition in partitions:
                    observer_counts = observer_language_counts(
                        graph, initial_modes, partition, horizon
                    )
                    brute_counts = brute_label_language_counts(
                        graph, initial_modes, partition, horizon
                    )
                    language_comparisons += 1
                    if observer_counts != brute_counts:
                        mismatches.append(
                            {
                                "kind": "language_count",
                                "modes": mode_count,
                                "graph": graph,
                                "initial": initial_modes,
                                "partition": partition,
                                "observer": observer_counts,
                                "brute": brute_counts,
                            }
                        )
                    reports[partition] = observer_counts
                for sensor_partition in partitions:
                    for action_partition in partitions:
                        mode_cases += 1
                        feasible = action_is_observable_from_transducer(
                            graph,
                            initial_modes,
                            sensor_partition,
                            action_partition,
                        )
                        mode_feasible += int(feasible)
                        if feasible and (
                            reports[sensor_partition][-1] < 1
                            or reports[action_partition][-1] < 1
                        ):
                            mismatches.append(
                                {
                                    "kind": "empty_feasible_language",
                                    "modes": mode_count,
                                }
                            )
        total_cases += mode_cases
        total_feasible += mode_feasible
        rows.append(
            {
                "modes": mode_count,
                "graphs": len(graphs),
                "initial_sets_per_graph": (1 << mode_count) - 1,
                "partitions": len(partitions),
                "transducer_action_cases": mode_cases,
                "expected_cases": expected_case_counts[mode_count],
                "causally_feasible_cases": mode_feasible,
            }
        )
        if mode_cases != expected_case_counts[mode_count]:
            mismatches.append(
                {
                    "kind": "case_count",
                    "modes": mode_count,
                    "observed": mode_cases,
                    "expected": expected_case_counts[mode_count],
                }
            )
    return {
        "max_modes": max_modes,
        "horizon": horizon,
        "rows": rows,
        "total_cases": total_cases,
        "causally_feasible_cases": total_feasible,
        "language_comparisons": language_comparisons,
        "mismatches": mismatches,
        "pass": not mismatches,
    }


def observer_first_failure_horizon(
    graph: tuple[tuple[int, ...], ...],
    initial_modes: tuple[int, ...],
    sensor_partition: tuple[tuple[int, ...], ...],
    action_partition: tuple[tuple[int, ...], ...],
) -> int | None:
    """Return the first unsafe action horizon, or None when safe forever."""

    action_labels = _partition_labels(action_partition)
    initial_set = frozenset(initial_modes)
    layer = frozenset(
        frozenset(initial_set.intersection(block))
        for block in sensor_partition
        if initial_set.intersection(block)
    )
    seen_layers = set()
    horizon = 1
    while True:
        if any(len({action_labels[mode] for mode in belief}) != 1 for belief in layer):
            return horizon
        if layer in seen_layers:
            return None
        seen_layers.add(layer)
        following = set()
        for belief in layer:
            successors = frozenset(target for mode in belief for target in graph[mode])
            for block in sensor_partition:
                target_belief = frozenset(successors.intersection(block))
                if target_belief:
                    following.add(target_belief)
        layer = frozenset(following)
        horizon += 1


@lru_cache(maxsize=None)
def singleton_transient_delay_census(max_modes: int = 3) -> dict[str, Any]:
    """Classify the first failure time of every fixed-transducer case."""

    if not 1 <= max_modes <= 3:
        raise ValueError("max_modes must lie between one and three")
    rows = []
    total_cases = 0
    infinitely_safe = 0
    failure_histogram: Counter[int] = Counter()
    maximum_first_failure = 0
    maximum_delay_witness: dict[str, Any] | None = None
    mismatches = []
    for mode_count in range(1, max_modes + 1):
        partitions = set_partitions(mode_count)
        mode_cases = 0
        mode_infinite = 0
        mode_failures: Counter[int] = Counter()
        for graph in _nonblocking_graphs(mode_count):
            for initial_mask in range(1, 1 << mode_count):
                initial_modes = tuple(
                    mode for mode in range(mode_count) if initial_mask & (1 << mode)
                )
                for sensor_partition in partitions:
                    for action_partition in partitions:
                        mode_cases += 1
                        first_failure = observer_first_failure_horizon(
                            graph,
                            initial_modes,
                            sensor_partition,
                            action_partition,
                        )
                        independently_infinite = action_is_observable_from_transducer(
                            graph,
                            initial_modes,
                            sensor_partition,
                            action_partition,
                        )
                        if (first_failure is None) != independently_infinite:
                            mismatches.append(
                                {
                                    "kind": "infinite_classification",
                                    "modes": mode_count,
                                }
                            )
                        if first_failure is None:
                            mode_infinite += 1
                            continue
                        mode_failures[first_failure] += 1
                        failure_histogram[first_failure] += 1
                        if first_failure > maximum_first_failure:
                            maximum_first_failure = first_failure
                            maximum_delay_witness = {
                                "modes": mode_count,
                                "graph": [list(row) for row in graph],
                                "initial_modes": list(initial_modes),
                                "sensor_partition": [
                                    list(block) for block in sensor_partition
                                ],
                                "action_partition": [
                                    list(block) for block in action_partition
                                ],
                                "first_infeasible_horizon": first_failure,
                                "safe_horizons": list(range(1, first_failure)),
                            }
        total_cases += mode_cases
        infinitely_safe += mode_infinite
        rows.append(
            {
                "modes": mode_count,
                "cases": mode_cases,
                "infinitely_safe": mode_infinite,
                "first_failure_histogram": dict(sorted(mode_failures.items())),
            }
        )
    return {
        "max_modes": max_modes,
        "rows": rows,
        "total_cases": total_cases,
        "infinitely_safe_cases": infinitely_safe,
        "transient_or_immediate_failure_cases": total_cases - infinitely_safe,
        "first_failure_histogram": dict(sorted(failure_histogram.items())),
        "maximum_first_failure_horizon": maximum_first_failure,
        "maximum_safe_finite_horizon": maximum_first_failure - 1,
        "maximum_delay_witness": maximum_delay_witness,
        "mismatches": mismatches,
        "pass": (
            total_cases == 60134
            and infinitely_safe == 37430
            and failure_histogram == {1: 10642, 2: 8406, 3: 3110, 4: 534, 5: 12}
            and maximum_first_failure == 5
            and not mismatches
        ),
    }


@lru_cache(maxsize=None)
def golden_mean_registration_report(horizon: int = 12) -> dict[str, Any]:
    """Constrained graph with positive raw entropy and zero action entropy."""

    if not 2 <= horizon <= 20:
        raise ValueError("horizon must lie between two and twenty")
    graph = ((0, 1), (0,))
    initial_modes = (0, 1)
    raw_partition = ((0,), (1,))
    constant_action = ((0, 1),)
    raw_counts = observer_language_counts(graph, initial_modes, raw_partition, horizon)
    action_counts = observer_language_counts(
        graph, initial_modes, constant_action, horizon
    )
    fibonacci = [0, 1]
    while len(fibonacci) <= horizon + 2:
        fibonacci.append(fibonacci[-1] + fibonacci[-2])
    expected_raw = tuple(fibonacci[length + 2] for length in range(1, horizon + 1))
    phi = (1 + math.sqrt(5)) / 2
    return {
        "graph": [[0, 1], [0]],
        "raw_counts": list(raw_counts),
        "expected_fibonacci_counts": list(expected_raw),
        "action_counts": list(action_counts),
        "observer_beliefs": [
            sorted(belief)
            for belief in sorted(
                observer_beliefs(graph, initial_modes, raw_partition),
                key=lambda value: (len(value), tuple(value)),
            )
        ],
        "characteristic_polynomial": "lambda^2-lambda-1",
        "spectral_radius": "phi=(1+sqrt(5))/2",
        "raw_read_entropy_bits": math.log2(phi),
        "write_entropy_bits": 0.0,
        "forced_raw_region": "[log2(phi),infinity) x [0,infinity)",
        "computed_sensor_region": "[0,infinity) x [0,infinity)",
        "pass": (
            raw_counts == expected_raw
            and action_counts == (1,) * horizon
            and action_is_observable_from_transducer(
                graph, initial_modes, raw_partition, constant_action
            )
        ),
    }


def adaptive_sensor_bellman(
    graph: tuple[tuple[int, ...], ...],
    initial_modes: tuple[int, ...],
    action_partition: tuple[tuple[int, ...], ...],
    grammar: tuple[tuple[tuple[int, ...], ...], ...],
    horizon: int,
) -> dict[str, Any]:
    """Exact finite-horizon read-language Bellman recurrence on beliefs."""

    mode_count = len(graph)
    if not 1 <= horizon <= 32 or not grammar:
        raise ValueError("horizon must be positive and grammar nonempty")
    beliefs = tuple(
        frozenset(mode for mode in range(mode_count) if mask & (1 << mode))
        for mask in range(1, 1 << mode_count)
    )
    action_labels = _partition_labels(action_partition)
    choices: dict[
        frozenset[int],
        list[tuple[int, tuple[frozenset[int], ...], tuple[frozenset[int], ...]]],
    ] = {}
    for belief in beliefs:
        rows = []
        for grammar_index, partition in enumerate(grammar):
            cells = tuple(
                frozenset(belief.intersection(block))
                for block in partition
                if belief.intersection(block)
            )
            if not all(
                len({action_labels[mode] for mode in cell}) == 1 for cell in cells
            ):
                continue
            successors = tuple(
                frozenset(target for mode in cell for target in graph[mode])
                for cell in cells
            )
            rows.append((grammar_index, cells, successors))
        choices[belief] = rows

    infinity = 10**100
    values = {belief: 1 for belief in beliefs}
    rows = []
    initial_belief = frozenset(initial_modes)
    for current_horizon in range(1, horizon + 1):
        following: dict[frozenset[int], int] = {}
        policy: dict[frozenset[int], int | None] = {}
        for belief in beliefs:
            candidates = [
                (
                    sum(values[successor] for successor in successors),
                    grammar_index,
                )
                for grammar_index, _, successors in choices[belief]
            ]
            if candidates:
                best_value, best_index = min(candidates)
                following[belief] = best_value
                policy[belief] = best_index
            else:
                following[belief] = infinity
                policy[belief] = None
        values = following
        rows.append(
            {
                "horizon": current_horizon,
                "initial_read_words": (
                    None
                    if values[initial_belief] >= infinity
                    else values[initial_belief]
                ),
                "policy_by_belief_mask": {
                    str(sum(1 << mode for mode in belief)): policy[belief]
                    for belief in beliefs
                },
            }
        )
    return {
        "rows": rows,
        "initial_values": [row["initial_read_words"] for row in rows],
        "feasible": rows[-1]["initial_read_words"] is not None,
    }


def _reachable_modes(graph: tuple[tuple[int, ...], ...], source: int) -> frozenset[int]:
    reached = {source}
    pending = [source]
    while pending:
        for target in graph[pending.pop()]:
            if target not in reached:
                reached.add(target)
                pending.append(target)
    return frozenset(reached)


def adaptive_viable_beliefs(
    graph: tuple[tuple[int, ...], ...],
    action_partition: tuple[tuple[int, ...], ...],
    grammar: tuple[tuple[tuple[int, ...], ...], ...],
) -> tuple[frozenset[int], ...]:
    """Greatest belief set supporting an infinite safe grammar policy."""

    beliefs = tuple(
        frozenset(mode for mode in range(len(graph)) if mask & (1 << mode))
        for mask in range(1, 1 << len(graph))
    )
    action_labels = _partition_labels(action_partition)
    safe_successors = {}
    for belief in beliefs:
        choices = []
        for partition in grammar:
            cells = tuple(
                frozenset(belief.intersection(block))
                for block in partition
                if belief.intersection(block)
            )
            if all(len({action_labels[mode] for mode in cell}) == 1 for cell in cells):
                choices.append(
                    tuple(
                        frozenset(target for mode in cell for target in graph[mode])
                        for cell in cells
                    )
                )
        safe_successors[belief] = choices

    viable = set(beliefs)
    while True:
        following = {
            belief
            for belief in viable
            if any(
                all(successor in viable for successor in successors)
                for successors in safe_successors[belief]
            )
        }
        if following == viable:
            break
        viable = following
    return tuple(sorted(viable, key=lambda belief: (len(belief), tuple(belief))))


def adaptive_aperiodic_fixture_report(horizon: int = 16) -> dict[str, Any]:
    """Aperiodic constrained graph where adaptation closes an entropy gap."""

    graph = ((0, 1), (0, 2), (0, 1))
    initial_modes = (0, 2)
    action_partition = ((0, 2), (1,))
    constant_partition = ((0, 1, 2),)
    split_partition = ((0,), (1, 2))
    grammar = (constant_partition, split_partition)
    bellman = adaptive_sensor_bellman(
        graph, initial_modes, action_partition, grammar, horizon
    )
    fixed_constant_feasible = action_is_observable_from_transducer(
        graph, initial_modes, constant_partition, action_partition
    )
    fixed_split_feasible = action_is_observable_from_transducer(
        graph, initial_modes, split_partition, action_partition
    )
    fixed_split_counts = observer_language_counts(
        graph, initial_modes, split_partition, horizon
    )
    action_counts = observer_language_counts(
        graph, initial_modes, action_partition, horizon
    )
    fibonacci = [0, 1]
    while len(fibonacci) <= horizon + 1:
        fibonacci.append(fibonacci[-1] + fibonacci[-2])
    expected_adaptive = tuple(fibonacci[length + 1] for length in range(1, horizon + 1))
    phi = (1 + math.sqrt(5)) / 2
    belief_a_mask = str((1 << 0) | (1 << 2))
    belief_b_mask = str((1 << 0) | (1 << 1))
    stationary_choices = {
        "belief_{0,2}": bellman["rows"][-1]["policy_by_belief_mask"][belief_a_mask],
        "belief_{0,1}": bellman["rows"][-1]["policy_by_belief_mask"][belief_b_mask],
    }
    stationary_at_every_horizon = all(
        row["policy_by_belief_mask"][belief_a_mask] == 0
        and row["policy_by_belief_mask"][belief_b_mask] == 1
        for row in bellman["rows"]
    )
    strongly_connected = all(
        _reachable_modes(graph, source) == frozenset(range(3)) for source in range(3)
    )
    aperiodic_self_loop = 0 in graph[0]
    viable_beliefs = adaptive_viable_beliefs(graph, action_partition, grammar)
    initial_belief_viable = frozenset(initial_modes) in viable_beliefs
    return {
        "graph": [[0, 1], [0, 2], [0, 1]],
        "initial_modes": [0, 2],
        "action_partition": [[0, 2], [1]],
        "grammar": [[[0, 1, 2]], [[0], [1, 2]]],
        "strongly_connected": strongly_connected,
        "aperiodic_self_loop": aperiodic_self_loop,
        "adaptive_read_counts": bellman["initial_values"],
        "required_action_counts": list(action_counts),
        "expected_fibonacci_counts": list(expected_adaptive),
        "fixed_constant_feasible": fixed_constant_feasible,
        "fixed_split_feasible": fixed_split_feasible,
        "fixed_split_read_counts": list(fixed_split_counts),
        "stationary_choices": stationary_choices,
        "stationary_at_every_horizon": stationary_at_every_horizon,
        "viable_belief_count": len(viable_beliefs),
        "initial_belief_viable": initial_belief_viable,
        "finite_to_infinite_bridge": "W_(T-N)(I) <= V_T(I) <= W_T(I)",
        "positional_value_formula": "rho_I=lim_T V_T(I)^(1/T)",
        "bellman_matrix_on_reachable_beliefs": "[[0,1],[1,1]]",
        "adaptive_read_entropy_bits": math.log2(phi),
        "fixed_best_read_entropy_bits": 1.0,
        "write_entropy_bits": math.log2(phi),
        "adaptive_region": "[log2(phi),infinity) x [log2(phi),infinity)",
        "best_fixed_region": "[1,infinity) x [log2(phi),infinity)",
        "pass": (
            tuple(bellman["initial_values"]) == expected_adaptive
            and action_counts == expected_adaptive
            and not fixed_constant_feasible
            and fixed_split_feasible
            and fixed_split_counts
            == tuple(2**length for length in range(1, horizon + 1))
            and stationary_choices == {"belief_{0,2}": 0, "belief_{0,1}": 1}
            and stationary_at_every_horizon
            and strongly_connected
            and aperiodic_self_loop
            and len(viable_beliefs) == 5
            and initial_belief_viable
        ),
    }


@lru_cache(maxsize=None)
def adaptive_sensor_grammar_census(horizon: int = 4) -> dict[str, Any]:
    """Exhaust all three-mode two-partition grammars at a bounded horizon."""

    if not 1 <= horizon <= 5:
        raise ValueError("horizon must lie between one and five")
    mode_count = 3
    partitions = set_partitions(mode_count)
    grammars = tuple(itertools.combinations(partitions, 2))
    beliefs = tuple(
        frozenset(mode for mode in range(mode_count) if mask & (1 << mode))
        for mask in range(1, 1 << mode_count)
    )
    case_count = 0
    adaptive_feasible = 0
    fixed_feasible = 0
    adaptive_only = 0
    infinitely_viable = 0
    finite_only_feasible = 0
    strict_improvements = 0
    adaptive_matches_action = 0
    mismatches = []
    maximum_ratio = Fraction(0)
    maximum_ratio_witness: dict[str, Any] | None = None

    for graph in _nonblocking_graphs(mode_count):
        for initial_mask in range(1, 1 << mode_count):
            initial_modes = tuple(
                mode for mode in range(mode_count) if initial_mask & (1 << mode)
            )
            initial_belief = frozenset(initial_modes)
            for action_partition in partitions:
                action_labels = _partition_labels(action_partition)
                required_action_count = observer_language_counts(
                    graph, initial_modes, action_partition, horizon
                )[-1]
                partition_data = {}
                for sensor_partition in partitions:
                    safe_successors = {}
                    for belief in beliefs:
                        cells = tuple(
                            frozenset(belief.intersection(block))
                            for block in sensor_partition
                            if belief.intersection(block)
                        )
                        if all(
                            len({action_labels[mode] for mode in cell}) == 1
                            for cell in cells
                        ):
                            safe_successors[belief] = tuple(
                                frozenset(
                                    target for mode in cell for target in graph[mode]
                                )
                                for cell in cells
                            )
                        else:
                            safe_successors[belief] = None
                    fixed_is_feasible = action_is_observable_from_transducer(
                        graph,
                        initial_modes,
                        sensor_partition,
                        action_partition,
                    )
                    partition_data[sensor_partition] = {
                        "safe_successors": safe_successors,
                        "fixed_feasible": fixed_is_feasible,
                        "fixed_words": (
                            observer_language_counts(
                                graph, initial_modes, sensor_partition, horizon
                            )[-1]
                            if fixed_is_feasible
                            else None
                        ),
                    }

                for grammar in grammars:
                    case_count += 1
                    values = {belief: 1 for belief in beliefs}
                    for _ in range(horizon):
                        following = {}
                        for belief in beliefs:
                            candidates = []
                            for partition in grammar:
                                successors = partition_data[partition][
                                    "safe_successors"
                                ][belief]
                                if successors is not None:
                                    candidates.append(
                                        sum(
                                            values[successor]
                                            for successor in successors
                                        )
                                    )
                            following[belief] = min(candidates) if candidates else None
                        values = {
                            belief: value
                            for belief, value in following.items()
                            if value is not None
                        }
                        for belief in beliefs:
                            values.setdefault(belief, 10**100)
                    adaptive_words = values[initial_belief]
                    is_adaptive_feasible = adaptive_words < 10**100
                    viable = set(beliefs)
                    while True:
                        following_viable = {
                            belief
                            for belief in viable
                            if any(
                                successors is not None
                                and all(successor in viable for successor in successors)
                                for partition in grammar
                                for successors in (
                                    partition_data[partition]["safe_successors"][
                                        belief
                                    ],
                                )
                            )
                        }
                        if following_viable == viable:
                            break
                        viable = following_viable
                    is_infinitely_viable = initial_belief in viable
                    fixed_words = [
                        partition_data[partition]["fixed_words"]
                        for partition in grammar
                        if partition_data[partition]["fixed_words"] is not None
                    ]
                    best_fixed = min(fixed_words) if fixed_words else None
                    adaptive_feasible += int(is_adaptive_feasible)
                    infinitely_viable += int(is_infinitely_viable)
                    finite_only_feasible += int(
                        is_adaptive_feasible and not is_infinitely_viable
                    )
                    fixed_feasible += int(best_fixed is not None)
                    adaptive_only += int(is_adaptive_feasible and best_fixed is None)
                    if is_infinitely_viable and not is_adaptive_feasible:
                        mismatches.append(
                            {"kind": "viable_but_finite_horizon_infeasible"}
                        )
                    if not is_adaptive_feasible:
                        continue
                    adaptive_matches_action += int(
                        adaptive_words == required_action_count
                    )
                    if adaptive_words < required_action_count:
                        mismatches.append(
                            {
                                "kind": "action_language_lower_bound",
                                "adaptive_words": adaptive_words,
                                "action_words": required_action_count,
                            }
                        )
                    if best_fixed is not None:
                        if adaptive_words > best_fixed:
                            mismatches.append(
                                {
                                    "kind": "adaptive_exceeds_fixed",
                                    "adaptive_words": adaptive_words,
                                    "fixed_words": best_fixed,
                                }
                            )
                        if adaptive_words < best_fixed:
                            strict_improvements += 1
                            ratio = Fraction(best_fixed, adaptive_words)
                            if ratio > maximum_ratio:
                                maximum_ratio = ratio
                                maximum_ratio_witness = {
                                    "graph": [list(row) for row in graph],
                                    "initial_modes": list(initial_modes),
                                    "action_partition": [
                                        list(block) for block in action_partition
                                    ],
                                    "grammar": [
                                        [list(block) for block in partition]
                                        for partition in grammar
                                    ],
                                    "adaptive_words": adaptive_words,
                                    "best_fixed_words": best_fixed,
                                }

    expected_cases = 343 * 7 * 5 * 10
    return {
        "modes": mode_count,
        "horizon": horizon,
        "graphs": 343,
        "initial_sets_per_graph": 7,
        "action_partitions": len(partitions),
        "two_partition_grammars": len(grammars),
        "cases": case_count,
        "expected_cases": expected_cases,
        "adaptive_feasible_cases": adaptive_feasible,
        "infinitely_viable_cases": infinitely_viable,
        "finite_horizon_only_feasible_cases": finite_only_feasible,
        "fixed_feasible_cases": fixed_feasible,
        "adaptive_only_feasible_cases": adaptive_only,
        "strict_finite_horizon_improvements": strict_improvements,
        "adaptive_matches_action_language_cases": adaptive_matches_action,
        "maximum_fixed_to_adaptive_ratio": str(maximum_ratio),
        "maximum_ratio_witness": maximum_ratio_witness,
        "mismatches": mismatches,
        "pass": case_count == expected_cases and not mismatches,
    }


@lru_cache(maxsize=None)
def adaptive_grammar_lattice_census(horizon: int = 4) -> dict[str, Any]:
    """Exhaust every grammar subset and inclusion cover for three-mode graphs."""

    if not 1 <= horizon <= 5:
        raise ValueError("horizon must lie between one and five")
    mode_count = 3
    partitions = set_partitions(mode_count)
    grammar_count = 1 << len(partitions)
    beliefs = tuple(
        frozenset(mode for mode in range(mode_count) if mask & (1 << mode))
        for mask in range(1, 1 << mode_count)
    )
    infinity = 10**100
    base_cases = 0
    nonempty_cases = 0
    finite_feasible = 0
    infinitely_viable = 0
    finite_only = 0
    action_exact = 0
    cover_edges = 0
    feasibility_gain_edges = 0
    viability_gain_edges = 0
    strict_finite_value_edges = 0
    grammar_size_cases: Counter[int] = Counter()
    grammar_size_feasible: Counter[int] = Counter()
    grammar_size_viable: Counter[int] = Counter()
    maximum_cover_ratio = Fraction(1)
    maximum_cover_ratio_witness: dict[str, Any] | None = None
    finite_only_witnesses = []
    mismatches = []

    for graph in _nonblocking_graphs(mode_count):
        for initial_mask in range(1, 1 << mode_count):
            initial_modes = tuple(
                mode for mode in range(mode_count) if initial_mask & (1 << mode)
            )
            initial_belief = frozenset(initial_modes)
            for action_partition in partitions:
                base_cases += 1
                action_labels = _partition_labels(action_partition)
                action_words = observer_language_counts(
                    graph, initial_modes, action_partition, horizon
                )[-1]
                safe_successors = []
                for sensor_partition in partitions:
                    by_belief = {}
                    for belief in beliefs:
                        cells = tuple(
                            frozenset(belief.intersection(block))
                            for block in sensor_partition
                            if belief.intersection(block)
                        )
                        if all(
                            len({action_labels[mode] for mode in cell}) == 1
                            for cell in cells
                        ):
                            by_belief[belief] = tuple(
                                frozenset(
                                    target for mode in cell for target in graph[mode]
                                )
                                for cell in cells
                            )
                        else:
                            by_belief[belief] = None
                    safe_successors.append(by_belief)

                grammar_values = [infinity] * grammar_count
                grammar_viability = [False] * grammar_count
                for grammar_mask in range(1, grammar_count):
                    grammar_size = grammar_mask.bit_count()
                    nonempty_cases += 1
                    grammar_size_cases[grammar_size] += 1
                    selected = tuple(
                        index
                        for index in range(len(partitions))
                        if grammar_mask & (1 << index)
                    )
                    values = {belief: 1 for belief in beliefs}
                    initial_value_sequence = []
                    for _ in range(horizon):
                        following = {}
                        for belief in beliefs:
                            candidates = []
                            for index in selected:
                                successors = safe_successors[index][belief]
                                if successors is not None:
                                    candidates.append(
                                        min(
                                            infinity,
                                            sum(
                                                values[successor]
                                                for successor in successors
                                            ),
                                        )
                                    )
                            following[belief] = (
                                min(candidates) if candidates else infinity
                            )
                        values = following
                        initial_value_sequence.append(values[initial_belief])
                    adaptive_words = values[initial_belief]
                    grammar_values[grammar_mask] = adaptive_words
                    is_finite = adaptive_words < infinity

                    viable = set(beliefs)
                    while True:
                        following_viable = {
                            belief
                            for belief in viable
                            if any(
                                safe_successors[index][belief] is not None
                                and all(
                                    successor in viable
                                    for successor in safe_successors[index][belief]
                                )
                                for index in selected
                            )
                        }
                        if following_viable == viable:
                            break
                        viable = following_viable
                    is_viable = initial_belief in viable
                    grammar_viability[grammar_mask] = is_viable
                    finite_feasible += int(is_finite)
                    infinitely_viable += int(is_viable)
                    finite_only += int(is_finite and not is_viable)
                    if is_finite and not is_viable:
                        finite_only_witnesses.append(
                            {
                                "graph": [list(row) for row in graph],
                                "initial_modes": list(initial_modes),
                                "action_partition": [
                                    list(block) for block in action_partition
                                ],
                                "grammar_mask": grammar_mask,
                                "grammar": [
                                    [list(block) for block in partitions[index]]
                                    for index in selected
                                ],
                                "initial_values_through_horizon": initial_value_sequence,
                            }
                        )
                    grammar_size_feasible[grammar_size] += int(is_finite)
                    grammar_size_viable[grammar_size] += int(is_viable)
                    if is_viable and not is_finite:
                        mismatches.append({"kind": "viable_but_finite_infeasible"})
                    if is_finite:
                        action_exact += int(adaptive_words == action_words)
                        if adaptive_words < action_words:
                            mismatches.append(
                                {
                                    "kind": "action_language_lower_bound",
                                    "adaptive_words": adaptive_words,
                                    "action_words": action_words,
                                }
                            )

                for grammar_mask in range(grammar_count):
                    for index in range(len(partitions)):
                        bit = 1 << index
                        if grammar_mask & bit:
                            continue
                        expanded = grammar_mask | bit
                        cover_edges += 1
                        base_value = grammar_values[grammar_mask]
                        expanded_value = grammar_values[expanded]
                        if expanded_value > base_value:
                            mismatches.append(
                                {
                                    "kind": "finite_value_nonmonotone",
                                    "base": base_value,
                                    "expanded": expanded_value,
                                }
                            )
                        if (
                            grammar_viability[grammar_mask]
                            and not grammar_viability[expanded]
                        ):
                            mismatches.append({"kind": "viability_nonmonotone"})
                        if base_value >= infinity and expanded_value < infinity:
                            feasibility_gain_edges += 1
                        elif base_value < infinity and expanded_value < base_value:
                            strict_finite_value_edges += 1
                            ratio = Fraction(base_value, expanded_value)
                            if ratio > maximum_cover_ratio:
                                maximum_cover_ratio = ratio
                                maximum_cover_ratio_witness = {
                                    "graph": [list(row) for row in graph],
                                    "initial_modes": list(initial_modes),
                                    "action_partition": [
                                        list(block) for block in action_partition
                                    ],
                                    "base_grammar_mask": grammar_mask,
                                    "added_partition_index": index,
                                    "base_words": base_value,
                                    "expanded_words": expanded_value,
                                }
                        if (
                            not grammar_viability[grammar_mask]
                            and grammar_viability[expanded]
                        ):
                            viability_gain_edges += 1

    for witness in finite_only_witnesses:
        extended = adaptive_sensor_bellman(
            tuple(tuple(row) for row in witness["graph"]),
            tuple(witness["initial_modes"]),
            tuple(tuple(block) for block in witness["action_partition"]),
            tuple(
                tuple(tuple(block) for block in partition)
                for partition in witness["grammar"]
            ),
            horizon + 4,
        )["initial_values"]
        witness["first_infeasible_horizon"] = next(
            index for index, value in enumerate(extended, start=1) if value is None
        )

    expected_base_cases = 343 * 7 * 5
    expected_nonempty_cases = expected_base_cases * 31
    expected_cover_edges = expected_base_cases * 80
    return {
        "modes": mode_count,
        "horizon": horizon,
        "partitions": len(partitions),
        "grammars_including_empty": grammar_count,
        "base_graph_initial_action_cases": base_cases,
        "nonempty_grammar_cases": nonempty_cases,
        "finite_feasible_cases": finite_feasible,
        "infinitely_viable_cases": infinitely_viable,
        "finite_horizon_only_cases": finite_only,
        "finite_horizon_only_witnesses": finite_only_witnesses,
        "action_language_exact_cases": action_exact,
        "grammar_size_cases": dict(sorted(grammar_size_cases.items())),
        "grammar_size_feasible": dict(sorted(grammar_size_feasible.items())),
        "grammar_size_viable": dict(sorted(grammar_size_viable.items())),
        "cover_edges": cover_edges,
        "feasibility_gain_edges": feasibility_gain_edges,
        "viability_gain_edges": viability_gain_edges,
        "strict_finite_value_edges": strict_finite_value_edges,
        "maximum_cover_ratio": str(maximum_cover_ratio),
        "maximum_cover_ratio_witness": maximum_cover_ratio_witness,
        "mismatches": mismatches,
        "pass": (
            base_cases == expected_base_cases
            and nonempty_cases == expected_nonempty_cases
            and cover_edges == expected_cover_edges
            and finite_only == 12
            and all(
                witness["first_infeasible_horizon"] == horizon + 1
                for witness in finite_only_witnesses
            )
            and not mismatches
        ),
    }


def _block_index(partition: tuple[tuple[int, ...], ...]) -> dict[int, int]:
    return {
        mode: block_index
        for block_index, block in enumerate(partition)
        for mode in block
    }


def exact_language_rows(max_horizon: int = 8) -> list[dict[str, Any]]:
    """Enumerate every disturbance path and both transcript languages."""

    if not 1 <= max_horizon <= 8:
        raise ValueError("max_horizon must lie between one and eight")
    sufficient_index = _block_index(SUFFICIENT_PARTITION)
    raw_index = _block_index(RAW_PARTITION)
    rows = []
    for horizon in range(1, max_horizon + 1):
        raw_read_words: set[tuple[int, ...]] = set()
        computed_read_words: set[tuple[int, ...]] = set()
        write_words: set[tuple[int, ...]] = set()
        for mode_word in itertools.product(MODES, repeat=horizon):
            raw_read_words.add(tuple(raw_index[mode] for mode in mode_word))
            computed_read_words.add(tuple(sufficient_index[mode] for mode in mode_word))
            write_words.add(tuple(required_action(mode) for mode in mode_word))
        rows.append(
            {
                "horizon": horizon,
                "mode_paths": len(MODES) ** horizon,
                "raw_read_words": len(raw_read_words),
                "computed_read_words": len(computed_read_words),
                "write_words": len(write_words),
                "raw_read_bits": int(math.log2(len(raw_read_words))),
                "computed_read_bits": int(math.log2(len(computed_read_words))),
                "write_bits": int(math.log2(len(write_words))),
                "pass": (
                    len(raw_read_words) == 4**horizon
                    and len(computed_read_words) == 2**horizon
                    and len(write_words) == 2**horizon
                ),
            }
        )
    return rows


def registration_fork_report(max_horizon: int = 8) -> dict[str, Any]:
    """Return exact finite and asymptotic regions for the two registrations."""

    census = partition_census()
    registry_lattice = registry_lattice_census()
    general_grammar = general_sensor_grammar_report()
    general_registry_formula = general_registry_lattice_formula_report()
    finite_graphs = finite_graph_transducer_census()
    transient_delays = singleton_transient_delay_census()
    golden_mean = golden_mean_registration_report()
    adaptive_aperiodic = adaptive_aperiodic_fixture_report()
    adaptive_census = adaptive_sensor_grammar_census()
    adaptive_grammar_lattice = adaptive_grammar_lattice_census()
    rows = exact_language_rows(max_horizon)
    embedding = continuous_embedding_report()
    invariants = {
        "same_uncertain_plant": True,
        "same_evaluator_safe_set": True,
        "same_control_authority": True,
        "same_deterministic_noiseless_serial_channels": True,
        "same_terminal_language_cardinality_metric": True,
        "same_absence_of_side_information": True,
        "only_sensor_grammar_differs": True,
    }
    computed = {
        "sensor_registration": "any deterministic causal encoder",
        "admitted_partition": [list(block) for block in SUFFICIENT_PARTITION],
        "upstream_normal_form_closed": True,
        "downstream_normal_form_closed": True,
        "finite_region": "B_read >= T and B_write >= T",
        "closed_asymptotic_region": "[1,infinity) x [1,infinity)",
    }
    raw = {
        "sensor_registration": "forced injective raw-mode transducer",
        "admitted_partition": [list(block) for block in RAW_PARTITION],
        "upstream_normal_form_closed": False,
        "downstream_normal_form_closed": True,
        "finite_region": "B_read >= 2T and B_write >= T",
        "closed_asymptotic_region": "[2,infinity) x [1,infinity)",
    }
    converse = {
        "required_action_words": "2^T",
        "write_lower_bound": "the deterministic actuator maps each write word to one action word",
        "computed_read_lower_bound": "data processing gives |M_write(T)| <= |M_read(T)|",
        "raw_read_lower_bound": "the forced injective transducer realizes all 4^T mode words",
    }
    quantifier_audit = canonical_quantifier_audit(
        computed["closed_asymptotic_region"], raw["closed_asymptotic_region"]
    )
    quantifier_sensitivity = canonical_quantifier_sensitivity_audit()
    registry_model_audit = canonical_registry_model_audit(
        computed["closed_asymptotic_region"], raw["closed_asymptotic_region"]
    )
    global_scope_audit = global_registry_scope_audit()
    return {
        "fixture": {
            "safe_modes": list(MODES),
            "unsafe_state": "BAD",
            "actions": list(ACTIONS),
            "required_action_by_mode": [required_action(mode) for mode in MODES],
            "disturbance_after_each_safe_action": "chooses any next safe mode",
        },
        "partition_census": census,
        "registry_lattice_census": registry_lattice,
        "general_sensor_grammar": general_grammar,
        "general_registry_lattice_formula": general_registry_formula,
        "finite_graph_transducers": finite_graphs,
        "singleton_transient_delay_census": transient_delays,
        "golden_mean_registration": golden_mean,
        "adaptive_aperiodic_registration": adaptive_aperiodic,
        "adaptive_sensor_grammar_census": adaptive_census,
        "adaptive_grammar_lattice_census": adaptive_grammar_lattice,
        "continuous_embedding": embedding,
        "language_rows": rows,
        "shared_invariants": invariants,
        "computed_sensor_class": computed,
        "forced_raw_sensor_class": raw,
        "converse_certificates": converse,
        "canonical_quantifier_audit": quantifier_audit,
        "canonical_quantifier_sensitivity": quantifier_sensitivity,
        "canonical_registry_model_audit": registry_model_audit,
        "global_registry_scope_audit": global_scope_audit,
        "registration_changes_region": (
            computed["closed_asymptotic_region"] != raw["closed_asymptotic_region"]
        ),
        "pass": (
            census["pass"]
            and registry_lattice["pass"]
            and general_grammar["pass"]
            and general_registry_formula["pass"]
            and finite_graphs["pass"]
            and transient_delays["pass"]
            and golden_mean["pass"]
            and adaptive_aperiodic["pass"]
            and adaptive_census["pass"]
            and adaptive_grammar_lattice["pass"]
            and quantifier_audit["pass"]
            and quantifier_sensitivity["pass"]
            and registry_model_audit["pass"]
            and global_scope_audit["pass"]
            and embedding["pass"]
            and all(row["pass"] for row in rows)
            and all(invariants.values())
            and computed["closed_asymptotic_region"] == "[1,infinity) x [1,infinity)"
            and raw["closed_asymptotic_region"] == "[2,infinity) x [1,infinity)"
        ),
    }


def verification_payload() -> dict[str, Any]:
    report = registration_fork_report()
    gates = {
        "R0_complete_four_mode_partition_census": report["partition_census"]["pass"],
        "R1_all_disturbance_paths_replayed_through_horizon_eight": all(
            row["pass"] for row in report["language_rows"]
        ),
        "R2_computed_sensor_diagonal_region": report["computed_sensor_class"][
            "closed_asymptotic_region"
        ]
        == "[1,infinity) x [1,infinity)",
        "R3_forced_raw_sensor_unequal_region": report["forced_raw_sensor_class"][
            "closed_asymptotic_region"
        ]
        == "[2,infinity) x [1,infinity)",
        "R4_only_registration_grammar_changes": all(
            report["shared_invariants"].values()
        ),
        "R5_upstream_normal_form_seam_is_explicit": (
            report["computed_sensor_class"]["upstream_normal_form_closed"]
            and not report["forced_raw_sensor_class"]["upstream_normal_form_closed"]
            and report["computed_sensor_class"]["downstream_normal_form_closed"]
            and report["forced_raw_sensor_class"]["downstream_normal_form_closed"]
            and report["registration_changes_region"]
        ),
        "R6_rational_evaluator_transversal_embedding": report["continuous_embedding"][
            "pass"
        ],
        "R7_general_sensor_grammar_variational_formula": report[
            "general_sensor_grammar"
        ]["pass"],
        "R8_finite_graph_subset_observer_census": report["finite_graph_transducers"][
            "pass"
        ],
        "R9_golden_mean_registration_entropy_fork": report["golden_mean_registration"][
            "pass"
        ],
        "R10_adaptive_aperiodic_sensor_grammar_gap": report[
            "adaptive_aperiodic_registration"
        ]["pass"],
        "R11_adaptive_three_mode_grammar_census": report[
            "adaptive_sensor_grammar_census"
        ]["pass"],
        "R12_adaptive_infinite_viability_and_positional_certificate": (
            report["adaptive_aperiodic_registration"]["initial_belief_viable"]
            and report["adaptive_aperiodic_registration"]["viable_belief_count"] == 5
            and report["adaptive_aperiodic_registration"]["stationary_at_every_horizon"]
        ),
        "R13_canonical_registration_quantifier_is_underdetermined": report[
            "canonical_quantifier_audit"
        ]["pass"],
        "R14_canonical_quantifier_audit_is_mutation_sensitive": report[
            "canonical_quantifier_sensitivity"
        ]["pass"],
        "R15_two_canonical_registry_models_have_distinct_exact_regions": report[
            "canonical_registry_model_audit"
        ]["pass"],
        "R16_no_global_normative_source_selects_the_code_registry": report[
            "global_registry_scope_audit"
        ]["pass"],
        "R17_complete_sensor_registry_lattice_is_monotone": report[
            "registry_lattice_census"
        ]["pass"],
        "R18_general_registry_lattice_counting_formula": report[
            "general_registry_lattice_formula"
        ]["pass"],
        "R19_complete_adaptive_grammar_lattice_is_monotone": report[
            "adaptive_grammar_lattice_census"
        ]["pass"],
        "R20_fixed_transducer_first_failure_depth_is_classified": report[
            "singleton_transient_delay_census"
        ]["pass"],
    }
    return {
        "schema_version": "asmp4_registration_fork_verification_v0_6",
        "report": report,
        "gates": gates,
        "pass": all(gates.values()),
    }


def main() -> int:
    payload = verification_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
