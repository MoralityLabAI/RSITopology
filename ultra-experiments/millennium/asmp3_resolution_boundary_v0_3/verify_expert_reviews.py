from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "RELEASE_MANIFEST_v0_3.json"
CHECKLIST = HERE / "external_review_checklist_v0_6.json"
REVIEWS = HERE / "reviews"
STATUS = HERE / "artifacts" / "expert_review_status_v0_6.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def verify_manifest_members(manifest_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return False, [f"unreadable release manifest: {error}"]
    files = manifest.get("files")
    if not isinstance(files, dict):
        return False, ["release manifest files object is missing"]
    if manifest.get("file_count") != len(files):
        errors.append("release manifest file_count mismatch")
    allowed_root = manifest_path.parent.parent.resolve()
    for relative, record in files.items():
        if not isinstance(relative, str) or not isinstance(record, dict):
            errors.append("invalid release manifest member record")
            continue
        path = (manifest_path.parent / relative).resolve()
        try:
            path.relative_to(allowed_root)
        except ValueError:
            errors.append(f"release manifest member escapes allowed root: {relative}")
            continue
        if not path.is_file():
            errors.append(f"release manifest member missing: {relative}")
            continue
        if record.get("bytes") != path.stat().st_size:
            errors.append(f"release manifest byte count mismatch: {relative}")
        if record.get("sha256") != sha256(path):
            errors.append(f"release manifest hash mismatch: {relative}")
    return not errors, errors


def validate_receipt(
    receipt: dict[str, object],
    manifest_sha256: str,
    checklist: dict[str, object],
    reviews_directory: Path,
) -> list[str]:
    errors: list[str] = []
    required_fields = {
        "schema_version",
        "reviewer",
        "expertise",
        "conflicts",
        "review_track",
        "release_manifest_sha256",
        "independent_initial_review",
        "question_answers",
        "verdict",
        "material_issue_found",
        "repository_storage_permission",
        "independent_checker",
    }
    missing = sorted(required_fields - receipt.keys())
    if missing:
        errors.append(f"missing fields: {missing}")
        return errors
    unexpected = sorted(receipt.keys() - required_fields)
    if unexpected:
        errors.append(f"unexpected fields: {unexpected}")
    if receipt["schema_version"] != "asmp3_v0_3_expert_review_v3":
        errors.append("unexpected schema_version")
    if not isinstance(receipt["reviewer"], str) or not receipt["reviewer"].strip():
        errors.append("reviewer identity is empty")
    if not isinstance(receipt["expertise"], str) or not receipt["expertise"].strip():
        errors.append("expertise is empty")
    if receipt["review_track"] not in checklist["required_review_tracks"]:
        errors.append("unknown review_track")
    if receipt["release_manifest_sha256"] != manifest_sha256:
        errors.append("release manifest hash mismatch")
    if receipt["independent_initial_review"] is not True:
        errors.append("review was not independently initialized")
    answers = receipt["question_answers"]
    if not isinstance(answers, list) or len(answers) != checklist[
        "required_questions_per_receipt"
    ]:
        errors.append("question answer count mismatch")
    else:
        questions = []
        for answer in answers:
            if not isinstance(answer, dict):
                errors.append("question answer is not an object")
                continue
            if set(answer) != {"question", "answer", "evidence"}:
                errors.append("question answer fields mismatch")
                continue
            questions.append(answer["question"])
            if answer["answer"] not in {"yes", "no", "unclear"}:
                errors.append("invalid question answer")
            if not isinstance(answer["evidence"], str) or not answer[
                "evidence"
            ].strip():
                errors.append("question evidence is empty")
        if sorted(questions) != list(
            range(1, checklist["required_questions_per_receipt"] + 1)
        ):
            errors.append("question numbers must be exactly 1 through 12")
    if receipt["verdict"] not in {
        "accept",
        "accept_with_nonmaterial_corrections",
        "major_revision",
        "reject",
    }:
        errors.append("invalid verdict")
    if not isinstance(receipt["material_issue_found"], bool):
        errors.append("material_issue_found is not boolean")
    if receipt["repository_storage_permission"] is not True:
        errors.append("repository storage permission is absent")
    checker = receipt["independent_checker"]
    checker_fields = {
        "implemented_by_review_team",
        "artifact",
        "artifact_sha256",
        "method",
        "result",
    }
    if not isinstance(checker, dict) or set(checker) != checker_fields:
        errors.append("independent_checker fields mismatch")
    else:
        implemented = checker["implemented_by_review_team"]
        artifact = checker["artifact"]
        artifact_sha256 = checker["artifact_sha256"]
        method = checker["method"]
        result = checker["result"]
        if not isinstance(implemented, bool):
            errors.append("implemented_by_review_team is not boolean")
        if result not in {"pass", "fail", "not_run"}:
            errors.append("invalid independent checker result")
        if not isinstance(method, str):
            errors.append("independent checker method is not a string")
        if implemented is True:
            if result not in {"pass", "fail"}:
                errors.append("implemented checker result must be pass or fail")
            if not isinstance(method, str) or not method.strip():
                errors.append("implemented checker method is empty")
            if not isinstance(artifact, str) or not artifact.strip():
                errors.append("implemented checker artifact is empty")
            if not isinstance(artifact_sha256, str) or re.fullmatch(
                r"[A-F0-9]{64}", artifact_sha256
            ) is None:
                errors.append("implemented checker SHA-256 is invalid")
            if (
                isinstance(artifact, str)
                and artifact.strip()
                and isinstance(artifact_sha256, str)
                and re.fullmatch(r"[A-F0-9]{64}", artifact_sha256) is not None
            ):
                base = reviews_directory.resolve()
                checker_path = (reviews_directory / artifact).resolve()
                try:
                    checker_path.relative_to(base)
                except ValueError:
                    errors.append("independent checker artifact escapes reviews directory")
                else:
                    if not checker_path.is_file():
                        errors.append("independent checker artifact is missing")
                    elif sha256(checker_path) != artifact_sha256:
                        errors.append("independent checker artifact hash mismatch")
        else:
            if result != "not_run":
                errors.append("non-implementing review must use checker result not_run")
            if artifact not in {"", None} or artifact_sha256 not in {"", None}:
                errors.append("non-implementing review must not name a checker artifact")
    return errors


def evaluate_reviews(
    reviews_directory: Path = REVIEWS,
    manifest_path: Path = MANIFEST,
    checklist_path: Path = CHECKLIST,
) -> dict[str, object]:
    checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
    manifest_sha256 = sha256(manifest_path)
    manifest_members_valid, manifest_member_errors = verify_manifest_members(
        manifest_path
    )
    records = []
    for path in sorted(reviews_directory.glob("*.json")):
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
            errors = validate_receipt(
                receipt,
                manifest_sha256,
                checklist,
                reviews_directory,
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            receipt = {}
            errors = [f"unreadable receipt: {error}"]
        answers = receipt.get("question_answers")
        all_answers_yes = (
            isinstance(answers, list)
            and len(answers) == checklist["required_questions_per_receipt"]
            and all(
                isinstance(answer, dict) and answer.get("answer") == "yes"
                for answer in answers
            )
        )
        qualifies = (
            not errors
            and receipt["verdict"] in checklist["acceptable_verdicts"]
            and receipt["material_issue_found"] is False
            and all_answers_yes
        )
        checker = receipt.get("independent_checker", {})
        independently_checked = (
            qualifies
            and isinstance(checker, dict)
            and checker.get("implemented_by_review_team") is True
            and checker.get("result") == "pass"
        )
        records.append(
            {
                "file": path.name,
                "reviewer": receipt.get("reviewer"),
                "review_track": receipt.get("review_track"),
                "verdict": receipt.get("verdict"),
                "all_required_questions_answered_yes": all_answers_yes,
                "qualifies": qualifies,
                "independently_implemented_checker_passed": independently_checked,
                "errors": errors,
            }
        )

    qualifying = [record for record in records if record["qualifies"]]
    identities = [record["reviewer"] for record in qualifying]
    tracks = {record["review_track"] for record in qualifying}
    distinct_identities = len(identities) == len(set(identities))
    required_tracks = set(checklist["required_review_tracks"])
    independently_checked = sum(
        bool(record["independently_implemented_checker_passed"])
        for record in qualifying
    )
    completion = (
        len(qualifying) >= checklist["minimum_independent_teams"]
        and distinct_identities
        and required_tracks.issubset(tracks)
        and manifest_members_valid
        and independently_checked
        >= checklist["minimum_independently_implemented_checkers"]
    )
    return {
        "schema_version": "asmp3_expert_review_status_v0_6",
        "problem_id": checklist["problem_id"],
        "problem_version": checklist["problem_version"],
        "release_manifest_sha256": manifest_sha256,
        "release_manifest_members_valid": manifest_members_valid,
        "release_manifest_member_errors": manifest_member_errors,
        "minimum_independent_teams": checklist["minimum_independent_teams"],
        "required_review_tracks": checklist["required_review_tracks"],
        "receipt_files_seen": len(records),
        "qualifying_receipts": len(qualifying),
        "distinct_qualifying_identities": distinct_identities,
        "covered_review_tracks": sorted(tracks),
        "qualifying_independently_implemented_checkers": independently_checked,
        "minimum_independently_implemented_checkers": checklist[
            "minimum_independently_implemented_checkers"
        ],
        "receipts": records,
        "completion_gate_satisfied": completion,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    status = evaluate_reviews()
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        "ASMP-3 expert-review gate: "
        f"{status['qualifying_receipts']}/"
        f"{status['minimum_independent_teams']} qualifying; "
        f"complete={str(status['completion_gate_satisfied']).lower()}"
    )
    if args.require_complete and not status["completion_gate_satisfied"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
