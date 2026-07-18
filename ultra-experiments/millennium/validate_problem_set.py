"""Deterministic structural validator for ASMP-CANDIDATE-SET v0.1."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY = ROOT / "problem_set_v0_1.json"
README = ROOT / "README.md"
AUDIT = ROOT / "REFEREE_AUDIT_v0_1.md"
RECEIPT = ROOT / "VALIDATION_RECEIPT_v0_1.json"

EXPECTED_IDS = [f"ASMP-{index}" for index in range(1, 8)]
REQUIRED_JSON_FIELDS = {
    "id",
    "slug",
    "title",
    "domains",
    "canonical_target",
    "positive_resolution_requires",
    "negative_resolution_requires",
    "negative_resolution_allowed",
    "empirical_resolution_allowed",
}
REQUIRED_SECTIONS = (
    "## Safety question",
    "## Canonical mathematical setting",
    "## What a complete resolution requires",
    "## Liveness and kill examples",
    "## Existing theory this must exceed",
    "## Safety consequence",
)
FORMULA_SENTINELS = (
    "O_(E,I)(M) = O_(E,I)(M')  implies",
    "inf_(m in M) Pr_(D_src drawn from family m)",
    "a_H(k) = inf_(registered k-query aggregators A)",
    "r_r(C) = limsup_(T->infinity)",
    "R_r >= h_read_perp",
    "z_(t+1) = F_t(z_t)",
    "C_coll(P_0,D,{epsilon_T},{rho_T})",
    "omega_T(D,rho,delta)",
    "Err(K) = {(a,b)",
    "c*(alpha,beta)",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_utf8(path: Path) -> str:
    payload = path.read_bytes()
    text = payload.decode("utf-8", errors="strict")
    require("\ufffd" not in text, f"replacement character in {path.name}")
    # Common signatures of UTF-8 decoded once as a legacy single-byte encoding.
    bad_prefixes = ("\u00c3", "\u00c2", "\u00e2\u20ac")
    require(not any(token in text for token in bad_prefixes), f"mojibake in {path.name}")
    return text


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    main_text = read_utf8(MAIN)
    readme_text = read_utf8(README)
    audit_text = read_utf8(AUDIT)
    registry = json.loads(read_utf8(REGISTRY))
    receipt = json.loads(read_utf8(RECEIPT))

    require(registry["set_id"] == "ASMP-CANDIDATE-SET-v0.1", "ambiguous set identifier")
    require(registry["problem_count"] == 7, "registry problem_count must equal 7")
    require(len(registry["graduation_requirements"]) == 12, "graduation checklist must have 12 gates")
    require(registry["actual_prize_announced"] is False, "draft must not claim a prize")
    require(
        registry["affiliated_with_clay_mathematics_institute"] is False,
        "draft must not claim Clay affiliation",
    )
    require(
        registry["status"] == "proposed_candidate_definition_draft",
        "unexpected registry status",
    )
    require(registry["graduation_standard_satisfied"] is False, "v0.1 must not claim graduation")
    require(registry["registry_is_normative"] is False, "registry must defer to normative Markdown")
    require(
        registry["normative_statement_file"] == MAIN.name,
        "registry points at the wrong normative statement",
    )

    problems = registry["problems"]
    require(len(problems) == 7, "registry must contain exactly seven problems")
    ids = [problem["id"] for problem in problems]
    require(ids == EXPECTED_IDS, f"problem IDs/order differ: {ids}")
    require(registry["set_id"] not in ids, "set identifier collides with a problem identifier")

    heading_pattern = re.compile(r"^# (ASMP-[1-7]) \u2014 (.+)$", re.MULTILINE)
    headings = list(heading_pattern.finditer(main_text))
    require(len(headings) == 7, f"main document has {len(headings)} problem headings")
    require([match.group(1) for match in headings] == EXPECTED_IDS, "heading IDs/order differ")

    overview_rows = re.findall(r"^\| (ASMP-[1-7]) \| ([^|]+?) \|", main_text, re.MULTILINE)
    require(len(overview_rows) == 7, "overview table must contain exactly seven problem rows")
    require([problem_id for problem_id, _ in overview_rows] == EXPECTED_IDS, "overview IDs/order differ")

    for index, (problem, heading) in enumerate(zip(problems, headings)):
        missing = REQUIRED_JSON_FIELDS - problem.keys()
        require(not missing, f"{problem['id']} missing JSON fields: {sorted(missing)}")
        require(problem["title"] == heading.group(2), f"{problem['id']} title mismatch")
        require(problem["title"] == overview_rows[index][1].strip(), f"{problem['id']} overview title mismatch")
        require(problem["negative_resolution_allowed"] is True, f"{problem['id']} is one-sided")
        require(problem["empirical_resolution_allowed"] is False, f"{problem['id']} permits empirical resolution")
        require(problem["positive_resolution_requires"], f"{problem['id']} lacks resolution obligations")
        require(problem["negative_resolution_requires"], f"{problem['id']} lacks negative-resolution obligations")
        require(problem["domains"], f"{problem['id']} lacks mathematical domains")

        start = heading.start()
        stop = headings[index + 1].start() if index + 1 < len(headings) else main_text.index(
            "# Coverage map, reductions, and overlap"
        )
        section = main_text[start:stop]
        section_positions = []
        for required in REQUIRED_SECTIONS:
            require(section.count(required) == 1, f"{problem['id']} must contain exactly one {required}")
            section_positions.append(section.index(required))
        require(section_positions == sorted(section_positions), f"{problem['id']} sections are out of order")
        require(
            re.search(r"^## .*(Conjectures?|Problem)$", section, re.MULTILINE) is not None,
            f"{problem['id']} lacks a conjecture/classification heading",
        )
        require(
            re.search(r"\*\*Positive[^*]*:\*\*", section) is not None,
            f"{problem['id']} lacks a positive liveness witness",
        )
        require(
            re.search(r"\*\*(Negative|Zero capacity)[^*]*:\*\*", section) is not None,
            f"{problem['id']} lacks a negative/kill witness",
        )

    for sentinel in FORMULA_SENTINELS:
        require(sentinel in main_text, f"formula sentinel missing: {sentinel}")

    require("not an actual prize" in readme_text.lower(), "README lacks prize disclaimer")
    require("no affiliation" in readme_text.lower(), "README lacks affiliation disclaimer")
    require("candidate" in readme_text.lower(), "README overstates graduation status")
    require(registry["set_id"] in readme_text, "README omits the exact set identifier")
    require(registry["set_id"] in main_text, "main document omits the exact set identifier")
    require("candidate" in main_text[:1000].lower(), "main document overstates graduation status")
    require("not an actual prize" in main_text[:2000].lower(), "main document lacks prize disclaimer")
    require("candidate" in audit_text[:1000].lower(), "referee audit overstates graduation status")
    require("not yet be advertised as an actual" in audit_text[:1000].lower(), "audit lacks prize warning")
    for problem_id in EXPECTED_IDS:
        require(problem_id in audit_text, f"referee audit omits {problem_id}")
    for problem in problems:
        require(problem["title"] in audit_text, f"referee audit abbreviates {problem['id']} title")
    by_id = {problem["id"]: problem for problem in problems}
    require(
        "matching_communication_semantic_query_and_honest_prover_lower_bounds"
        in by_id["ASMP-3"]["positive_resolution_requires"],
        "ASMP-3 registry omits honest-prover lower bounds",
    )
    require(
        "single_letter_tensorizing_quantitative_resolving_modulus"
        in by_id["ASMP-6"]["positive_resolution_requires"],
        "ASMP-6 registry omits its resolving-modulus obligation",
    )
    require(
        registry["resolution_policy"]["benchmark_or_simulation_alone_can_resolve"] is False,
        "empirical firewall missing from resolution policy",
    )
    require(
        registry["resolution_policy"]["counterexample_or_impossibility_can_resolve"] is True,
        "negative resolution is not recognized",
    )
    urls = re.findall(r"\]\((https://[^)]+)\)", main_text)
    require(len(urls) >= 20, "primary-literature boundary is unexpectedly sparse")
    require(len(urls) == len(set(urls)), "duplicate primary-reference URL")

    require(receipt["set_id"] == registry["set_id"], "receipt set identifier mismatch")
    require(receipt["validation_status"] == "passed", "receipt does not record a pass")
    for filename, expected_hash in receipt["sha256"].items():
        target = ROOT / filename
        require(target.is_file(), f"receipt target missing: {filename}")
        require(sha256(target) == expected_hash, f"receipt hash mismatch: {filename}")

    print("ASMP candidate-set validation passed")
    print(
        f"problems=7 headings=7 overview_titles_match=true urls={len(urls)} "
        f"utf8=true sealed_files={len(receipt['sha256'])}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, UnicodeError) as error:
        print(f"ASMP candidate-set validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
