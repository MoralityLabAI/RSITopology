"""Source-only unit and mutation tests; these never execute the registered grid."""

from __future__ import annotations

import ast
import copy
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import inertial_selector as primary
import run as runner
import verify_independent as verifier


HERE = Path(__file__).resolve().parent


class ExactPrimitiveTests(unittest.TestCase):
    def test_exact_json_rejects_duplicate_float_and_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            primary.load_json_bytes_strict(b'{"a":1,"a":2}')
        for payload in (b'{"a":0.5}', b'{"a":NaN}', b'{"a":Infinity}'):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    primary.load_json_bytes_strict(payload)
                with self.assertRaises(ValueError):
                    verifier.load_json_bytes_strict(payload)

    def test_fraction_parser_is_canonical(self) -> None:
        self.assertEqual(primary.exact_fraction("301/100"), Fraction(301, 100))
        for value in (True, 3.01, "6/2", "03/1", "3"):
            with self.subTest(value=value):
                with self.assertRaises((TypeError, ValueError)):
                    primary.exact_fraction(value)

    def test_catalog_action_and_payoff_orientation(self) -> None:
        self.assertEqual(primary.actions(primary.CANONICAL_CATALOG, 2, 1), (0, 1))
        self.assertEqual(
            primary.payoff(
                primary.CANONICAL_CATALOG,
                "pd_threshold",
                Fraction(301, 100),
                (2, 1),
            ),
            (Fraction(301, 100), Fraction(0)),
        )
        self.assertEqual(
            primary.payoff(
                primary.CANONICAL_CATALOG,
                "chicken_threshold",
                Fraction(301, 100),
                (2, 1),
            ),
            (Fraction(301, 100), Fraction(1)),
        )

    def test_inertia_precedes_attached_cost_tie_break(self) -> None:
        programs = (0, 1, 2)
        inertial = primary.best_response_decision(
            primary.CANONICAL_CATALOG,
            "pd_threshold",
            Fraction(301, 100),
            programs,
            primary.FROZEN_COSTS,
            (2, 0),
            0,
        )
        noninertial = primary.best_response_decision(
            primary.CANONICAL_CATALOG,
            "pd_threshold",
            Fraction(301, 100),
            programs,
            primary.FROZEN_COSTS,
            (2, 0),
            0,
            inertia=False,
        )
        self.assertEqual((inertial["chosen_program"], noninertial["chosen_program"]), (2, 0))
        self.assertEqual(inertial["reason"], "incumbent_best_response_inertia")


class SelectorTests(unittest.TestCase):
    def terminal(
        self, family: str, temptation: Fraction, budget: int, schedule: str
    ) -> list[int] | None:
        return primary.trace_selector(
            primary.CANONICAL_CATALOG,
            family,
            temptation,
            primary.FROZEN_COSTS,
            budget,
            primary.FROZEN_START,
            schedule,
        )["terminal_profile"]

    def test_registered_boundary_and_schedule_examples(self) -> None:
        cases = (
            ("pd_threshold", Fraction(3), 3, "row_first", [1, 1]),
            ("pd_threshold", Fraction(301, 100), 2, "row_first", [1, 1]),
            ("pd_threshold", Fraction(301, 100), 3, "row_first", [2, 0]),
            ("pd_threshold", Fraction(301, 100), 3, "column_first", [0, 2]),
            ("chicken_threshold", Fraction(301, 100), 3, "row_first", [2, 1]),
            ("chicken_threshold", Fraction(301, 100), 3, "column_first", [1, 2]),
        )
        for family, temptation, budget, schedule, expected in cases:
            with self.subTest(case=(family, temptation, budget, schedule)):
                self.assertEqual(self.terminal(family, temptation, budget, schedule), expected)

    def test_source_blind_is_early_vulnerability_not_cooperation(self) -> None:
        for family, expected in (("pd_threshold", [0, 0]), ("chicken_threshold", [0, 1])):
            traces = [
                primary.trace_selector(
                    primary.SOURCE_BLIND_CATALOG,
                    family,
                    Fraction(301, 100),
                    primary.FROZEN_COSTS,
                    budget,
                    primary.FROZEN_START,
                    "row_first",
                )
                for budget in primary.FROZEN_BUDGETS
            ]
            self.assertEqual([trace["terminal_profile"] for trace in traces], [expected, expected])
            self.assertNotEqual(primary.actions(primary.SOURCE_BLIND_CATALOG, *expected), (1, 1))

    def test_repaired_catalog_retains_initialized_cooperation(self) -> None:
        trace = primary.trace_selector(
            primary.REPAIRED_CATALOG,
            "pd_threshold",
            Fraction(301, 100),
            primary.FROZEN_COSTS,
            3,
            primary.FROZEN_START,
            "row_first",
        )
        self.assertEqual(trace["terminal_profile"], [1, 1])
        self.assertEqual(primary.actions(primary.REPAIRED_CATALOG, 1, 1), (1, 1))

    def test_padding_and_one_nontrivial_relabel_are_exact(self) -> None:
        base = primary.trace_selector(
            primary.CANONICAL_CATALOG,
            "chicken_threshold",
            Fraction(301, 100),
            primary.FROZEN_COSTS,
            3,
            primary.FROZEN_START,
            "column_first",
        )
        padded = primary.trace_selector(
            primary.CANONICAL_CATALOG,
            "chicken_threshold",
            Fraction(301, 100),
            (3, 4, 5),
            5,
            primary.FROZEN_START,
            "column_first",
        )
        self.assertEqual(primary._semantic_trace_signature(base), primary._semantic_trace_signature(padded))
        permutation = (2, 0, 1)
        catalog, costs = primary.relabel_catalog(
            primary.CANONICAL_CATALOG, primary.FROZEN_COSTS, permutation
        )
        transformed = primary.trace_selector(
            catalog,
            "chicken_threshold",
            Fraction(301, 100),
            costs,
            3,
            (permutation[1], permutation[1]),
            "column_first",
        )
        expected = primary._semantic_trace_signature(base)
        self.assertEqual(expected, primary.relabel_trace_signature_back(transformed, permutation))
        base_graph = primary.complete_augmented_graph(
            primary.CANONICAL_CATALOG,
            "chicken_threshold",
            Fraction(301, 100),
            primary.FROZEN_COSTS,
            3,
        )
        transformed_graph = primary.complete_augmented_graph(
            catalog,
            "chicken_threshold",
            Fraction(301, 100),
            costs,
            3,
        )
        inverse = [0] * 3
        for old, new in enumerate(permutation):
            inverse[new] = old
        self.assertEqual(
            primary._semantic_graph_signature(base_graph),
            primary._semantic_graph_signature(transformed_graph, inverse),
        )

    def test_max_cost_and_simultaneous_are_causal_scope_breakers(self) -> None:
        maximum = primary.trace_selector(
            primary.CANONICAL_CATALOG,
            "pd_threshold",
            Fraction(301, 100),
            primary.FROZEN_COSTS,
            3,
            primary.FROZEN_START,
            "row_first",
            tie_mode="max_cost",
        )
        self.assertEqual(maximum["terminal_profile"], [2, 2])
        self.assertEqual(
            maximum["attractor_cycle"],
            [[2, 2, 0], [2, 2, 1]],
        )
        self.assertEqual(
            primary.simultaneous_trace(
                primary.CANONICAL_CATALOG,
                "pd_threshold",
                Fraction(301, 100),
                primary.FROZEN_COSTS,
                3,
                primary.FROZEN_START,
            ),
            {"termination": "fixed_profile", "visited_profiles": [[1, 1], [2, 2], [2, 2]]},
        )
        chicken = primary.simultaneous_trace(
            primary.CANONICAL_CATALOG,
            "chicken_threshold",
            Fraction(301, 100),
            primary.FROZEN_COSTS,
            3,
            primary.FROZEN_START,
        )
        self.assertEqual(chicken["termination"], "profile_cycle")
        self.assertEqual(chicken["cycle"], [[1, 1], [2, 2]])

    def test_cycle_fixture_uses_real_trace_and_rejects_attractor_mutation(self) -> None:
        fixture = primary.cycle_detection_fixture()
        self.assertTrue(fixture["pass"])
        self.assertEqual(fixture["termination"], "augmented_state_cycle")
        self.assertEqual(len(fixture["observed_attractor_cycle"]), 6)
        independent = verifier.independent_trace(
            verifier.CYCLE_FIXTURE,
            "pd_threshold",
            Fraction(301, 100),
            verifier.COSTS,
            3,
            (0, 0),
            "row_first",
        )
        self.assertEqual(
            fixture["observed_attractor_cycle"],
            independent["observed_attractor_cycle"],
        )
        graph = primary.complete_augmented_graph(
            primary.CYCLE_FIXTURE_CATALOG,
            "pd_threshold",
            Fraction(301, 100),
            primary.FROZEN_COSTS,
            3,
        )
        mutated = copy.deepcopy(graph)
        start_edge = next(edge for edge in mutated["edges"] if edge["from"] == [0, 0, 0])
        attractor = next(
            item for item in mutated["attractors"] if item["id"] == start_edge["attractor_id"]
        )
        attractor["cycle"][0][0] = (attractor["cycle"][0][0] + 1) % 3
        trace = primary.trace_selector(
            primary.CYCLE_FIXTURE_CATALOG,
            "pd_threshold",
            Fraction(301, 100),
            primary.FROZEN_COSTS,
            3,
            (0, 0),
            "row_first",
            graph=mutated,
        )
        self.assertFalse(trace["reported_attractor_matches_observed"])


class GraphAndIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.primary_graph = primary.complete_augmented_graph(
            primary.CANONICAL_CATALOG,
            "pd_threshold",
            Fraction(301, 100),
            primary.FROZEN_COSTS,
            3,
        )
        cls.independent_graph = verifier.independent_graph(
            "pd_threshold", Fraction(301, 100), 3
        )

    def test_one_complete_graph_matches_independent_reconstruction(self) -> None:
        self.assertEqual(self.primary_graph, self.independent_graph)
        self.assertEqual(
            primary._semantic_graph_signature(self.primary_graph),
            verifier.graph_signature(self.independent_graph),
        )
        self.assertEqual(self.primary_graph["state_count"], 18)
        self.assertEqual(self.primary_graph["edge_count"], 18)
        self.assertEqual(sum(item["basin_size"] for item in self.primary_graph["attractors"]), 18)
        self.assertTrue(all(self.primary_graph["checks"].values()))

    def test_initialized_trace_is_bound_to_graph_attractor_and_equilibrium(self) -> None:
        row = primary.primary_row(
            "pd_threshold", Fraction(301, 100), 3, "row_first", self.primary_graph
        )
        independent = verifier.independent_row(
            "pd_threshold", Fraction(301, 100), 3, "row_first", self.independent_graph
        )
        self.assertEqual(row, independent)
        self.assertTrue(row["checks"]["initialized_state_binds_to_graph_attractor"])
        self.assertTrue(row["checks"]["selected_profile_is_pure_equilibrium"])

    def test_exact_fair_two_point_distribution(self) -> None:
        rows = [
            verifier.independent_row(
                "pd_threshold", Fraction(301, 100), 3, schedule, self.independent_graph
            )
            for schedule in verifier.SCHEDULES
        ]
        outcome = verifier.aggregate(rows)
        self.assertEqual(outcome["distinct_terminal_profiles"], 2)
        self.assertEqual([atom["weight"] for atom in outcome["outcome_atoms"]], ["1/2", "1/2"])
        self.assertEqual(outcome["cooperation_distribution"], [{"cooperative_selected": False, "weight": "1/1"}])
        primary_signature = primary._selection_distribution_signature(
            primary.CANONICAL_CATALOG,
            "pd_threshold",
            Fraction(301, 100),
            [(row["schedule"], row["trace"]) for row in rows],
        )
        independent_signature = verifier.distribution_signature(
            verifier.CANONICAL,
            "pd_threshold",
            Fraction(301, 100),
            [(row["schedule"], row["trace"]) for row in rows],
        )
        self.assertEqual(primary_signature, independent_signature)

    def test_semantic_mutations_are_rejected_by_strict_comparison(self) -> None:
        mutations = []
        changed_edge = copy.deepcopy(self.primary_graph)
        changed_edge["edges"][0]["to"][0] = 2
        mutations.append(changed_edge)
        dropped_edge = copy.deepcopy(self.primary_graph)
        dropped_edge["edges"].pop()
        mutations.append(dropped_edge)
        changed_basin = copy.deepcopy(self.primary_graph)
        changed_basin["attractors"][0]["basin_size"] += 1
        mutations.append(changed_basin)
        for candidate in mutations:
            with self.subTest(candidate=len(candidate["edges"])):
                self.assertFalse(verifier.strict_equal(candidate, self.independent_graph))
                self.assertEqual(verifier.mismatch("graph_cells", candidate, self.independent_graph), ["graph_cells"])


class FreezeAndEntrypointTests(unittest.TestCase):
    def test_manifest_binding_and_source_inventory(self) -> None:
        manifest = primary.load_json_strict(HERE / "manifest_v0_4.json")
        digest = primary.canonical_sha256(manifest)
        self.assertEqual(primary.FROZEN_MANIFEST_CANONICAL_SHA256, digest)
        self.assertEqual(verifier.MANIFEST_DIGEST, digest)
        self.assertTrue(all(primary.manifest_binding_checks(manifest).values()))
        self.assertEqual(
            tuple(item["name"] for item in manifest["controls"]),
            primary.FROZEN_CONTROL_IDS,
        )
        self.assertEqual({path.name for path in HERE.iterdir()}, set(primary.FROZEN_SOURCE_FILES))
        self.assertEqual(set(runner.FROZEN_SOURCE_FILES), set(primary.FROZEN_SOURCE_FILES))
        self.assertEqual(set(verifier.SOURCE_FILES), set(primary.FROZEN_SOURCE_FILES))

    def test_verifier_has_no_primary_import(self) -> None:
        tree = ast.parse((HERE / "verify_independent.py").read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertNotIn("inertial_selector", imported)
        self.assertIn('"implementation_imported": False', (HERE / "verify_independent.py").read_text(encoding="utf-8"))

    def test_postcommit_real_repository_source_binding(self) -> None:
        root = Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=HERE,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        relative = HERE.relative_to(root)
        expected = {(relative / name).as_posix() for name in runner.FROZEN_SOURCE_FILES}
        listed = set(
            subprocess.run(
                ["git", "ls-tree", "-r", "--name-only", commit, "--", relative.as_posix()],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
        )
        if listed != expected:
            self.skipTest("source candidate is not yet committed as the exact eight-file tree")
        for name in runner.FROZEN_SOURCE_FILES:
            committed = subprocess.run(
                ["git", "show", f"{commit}:{(relative / name).as_posix()}"],
                cwd=root,
                check=True,
                capture_output=True,
            ).stdout
            if committed != (HERE / name).read_bytes():
                self.skipTest("live source bytes are not yet frozen at HEAD")
        binding = runner.bootstrap_source_commit_binding(commit)
        self.assertEqual(verifier.replay_source_binding(binding), binding)

    def test_entrypoints_reject_nonisolated_launch_before_work(self) -> None:
        for filename in ("run.py", "verify_independent.py"):
            completed = subprocess.run(
                [sys.executable, "-B", str(HERE / filename), "--help"],
                cwd=HERE,
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("refusing unsafe launch before imports", completed.stderr)

    def test_write_once_rejects_occupied_destination_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text("sentinel", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                primary.write_once_json(path, {"pass": True})
            self.assertEqual(path.read_text(encoding="utf-8"), "sentinel")

    def test_result_and_verification_universes_are_frozen(self) -> None:
        self.assertEqual(primary.FROZEN_RESULT_FIELDS, verifier.RESULT_FIELDS)
        self.assertEqual(primary.FROZEN_PRIMARY_GATES, verifier.PRIMARY_GATES)
        self.assertEqual(primary.FROZEN_PROBE_IDS, verifier.PROBE_IDS)
        self.assertEqual(primary.FROZEN_CONTROL_IDS, verifier.CONTROL_IDS)
        self.assertEqual(primary.FROZEN_PREVERIFICATION_LAYERS, verifier.PREVERIFICATION_LAYERS)


if __name__ == "__main__":
    unittest.main()
